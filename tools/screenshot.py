# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Take screenshots during scenario, where pause = the number of seconds between screenshots.
# Set pause = 0 (default) to only take screenshots at the beginning and end of the scenario.
#
# To use, add "global:tools=screenshot" and optionally "screenshot:pause=<number of seconds>"
# to the hobl command.
# 
# Need this in hobl_bin on DUT: \\ntwdata\powtel\CTF\ClientPower\Tests\x64\ScreenCapture.exe

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import time
import threading
import core.call_rpc as rpc
import cv2 as cv
from PIL import Image

def single_screenshot(name, scenario, platform):
    '''
    Record periodic screen shots, for debug purposes.
    '''
    logging.info("Saving screenshot: " + name)
    if platform.lower() == "android":
        scenario._host_call("adb -s " + scenario.dut_ip + ":5555 shell screencap " + name)
    else:
        img = scenario._capture_screen()
        rgb_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        Image.fromarray(rgb_image).save(name)
    return

class ScreenshotThread(threading.Thread):
    def __init__(self, pause, scenario, platform, screenshot_path):
        threading.Thread.__init__(self)
        self.pause = pause
        self.scenario = scenario
        self.platform = platform
        self.event = threading.Event()
        self.screenshot_path = screenshot_path
        self.setDaemon(True)
        
    def run(self):
        num = 0
        while not self.event.is_set():
            try:
                single_screenshot(os.path.join(self.screenshot_path, self.scenario.testname + "_" + str(num).zfill(3) + ".png"), self.scenario, self.platform)
                num = num + 1
                time.sleep(self.pause)
            except: 
                return

class Tool(Scenario):
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'pause', '0')

    pause = int(Params.get(module, 'pause'))
    platform = Params.get('global', 'platform')
    
    def initCallback(self, scenario):
        if self.platform.lower() == "android":
            self.screenshot_path = scenario.dut_data_path + "/screenshots/"
            try:
                scenario._host_call("adb -s " + scenario.dut_ip + ":5555 shell rm -r " + self.screenshot_path)
            except:
                pass
            scenario._host_call("adb -s " + scenario.dut_ip + ":5555 shell mkdir -p " + self.screenshot_path)
        else:
            # self.screenshot_path = os.path.join(scenario.dut_data_path, "screenshots")
            # scenario._remote_make_dir(self.screenshot_path, True)
            self.screenshot_path = os.path.join(scenario.result_dir, "screenshots")
            os.makedirs(self.screenshot_path)

        logging.info("Initializing screenshot tool, path: " + self.screenshot_path)
        self.scenario = scenario
        self.conn_timeout = False
        
        # if self.platform.lower() != "android":
        #     self.scenario._upload("utilities\\ScreenShot\\x64\\Release\\ScreenShot.exe", self.scenario.dut_exec_path)
        
        if self.pause > 0:
            self.thread = ScreenshotThread(self.pause, self.scenario, self.platform, self.screenshot_path)
        return
        
    def testBeginCallback(self):
        if self.pause > 0:
            logging.info("Starting screenshot thread")
            self.thread.start()
        else:
            single_screenshot(os.path.join(self.screenshot_path, self.scenario.testname + "_begin.png"), self.scenario, self.platform)
        return
        
    def testEndCallback(self):
        if self.conn_timeout:
            logging.info("Skipping end screenshot because DUT communication timed out.")
            return
        if self.pause > 0 and self.conn_timeout == False :
            logging.info("Stopping screenshot thread")
            self.thread.event.set()
        single_screenshot(os.path.join(self.screenshot_path, self.scenario.testname + "_end.png"), self.scenario, self.platform)
        time.sleep(1)
        # Everything in dut_data_path is automatically copied back after this returns.
        
    def dataReadyCallback(self):
        return

    def testTimeoutCallback(self):
        if self.pause > 0:
            logging.info("Stopping screenshot thread")
            self.thread.event.set()
        self.conn_timeout = True
