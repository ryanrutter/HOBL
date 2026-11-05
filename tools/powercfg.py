# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Powercfg tool

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import csv
import time
import xml.etree.ElementTree as ET

from utilities.open_source import aluminium_power

class Tool(Scenario):
    '''
    Collect platform power and battery reports.  On Aluminium, saves the Android batterystats check-in report,
    power state, and device-idle state, and writes a charge-counter summary to <test>_powercfg_summary.csv.
    Windows continues to collect powercfg sleep-study and battery reports.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    #Params.setDefault(module, 'delay', '0')
    #Params.setDefault(module, 'duration', '10')
    # Params.setDefault(module, 'additional_args', '/SLEEPSTUDY /OUTPUT c:\\hobl_data\\sleepstudy.html')
    Params.setDefault(module, 'battery_report', '1')

    # Get parameters
    #delay = Params.get(module, 'delay')
    #duration = Params.get(module, 'duration')
    # additional_args = Params.get(module, 'additional_args')
    battery_report = Params.get(module, 'battery_report')
    platform = Params.get('global', 'platform')

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.aluminium = (Params.get("global", "platform") or "").lower() == "aluminium"
        self.start = None
        self.end = None
        self.reports = {}
        self.battery_report = Params.get(self.module, "battery_report")
        return

    def testBeginCallback(self):
        if self.aluminium:
            self.start = aluminium_power.read_battery_sample(self.scenario)
            self.start_time = time.time()
            return
        pass
    
    def testEndCallback(self):
        if self.aluminium:
            if self.start is not None:
                self.end = aluminium_power.read_battery_sample(self.scenario)
                self.end_time = time.time()
            commands = [
                ("power_state.txt", ["dumpsys", "power"]),
                ("device_idle.txt", ["dumpsys", "deviceidle"]),
            ]
            if self.battery_report == "1":
                commands.insert(0, ("battery_stats_checkin.csv", ["dumpsys", "batterystats --checkin"]))
            self.reports = {
                name: self._call(command, log_output=False, timeout=60)
                for name, command in commands
            }
            return
        output_file_xml = '\\sleepstudy-report.xml /XML'
        battery_file_xml = '\\battery-report.xml /XML'
        output_file_html = '\\sleepstudy-report.html'
        battery_file_html = '\\battery-report.html'

        self._call(["cmd.exe", "/C powercfg.exe /SLEEPSTUDY /VERBOSE /DURATION 5 /OUTPUT " + self.scenario.dut_data_path + output_file_xml], expected_exit_code="", fail_on_exception=False)
        if self.platform.lower() != "wcos":
            self._call(["cmd.exe", "/C powercfg.exe /SLEEPSTUDY /VERBOSE /DURATION 5 /OUTPUT " + self.scenario.dut_data_path + output_file_html], expected_exit_code="", fail_on_exception=False)
        if self.battery_report  == '1':
            self._call(["cmd.exe", "/C powercfg.exe /BATTERYREPORT /DURATION 5 /OUTPUT " + self.scenario.dut_data_path + battery_file_xml], expected_exit_code="", fail_on_exception=False)
            if self.platform.lower() != "wcos":
                self._call(["cmd.exe", "/C powercfg.exe /BATTERYREPORT /DURATION 5 /OUTPUT " + self.scenario.dut_data_path + battery_file_html], expected_exit_code="", fail_on_exception=False)
        self._call(["cmd.exe", "/C powercfg.exe /SRUMUTIL /OUTPUT " + self.scenario.dut_data_path + "\\srumutil.csv"], expected_exit_code="", fail_on_exception=False)

        # if self.platform.lower() == "wcos":
        #     self._copy_data_from_remote(self.scenario.result_dir)
        #     self._host_call('%SystemRoot%\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe cmd.exe /c powercfg.exe /sleepstudy /transformxml ' 
        #                     + self.scenario.result_dir + '\\sleepstudy-report.xml /output ' + self.scenario.result_dir + '\\sleepstudy-report.html')
            
        #     if self.battery_report  == '1':
        #         self._host_call('%SystemRoot%\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe cmd.exe /c powercfg.exe /batteryreport /transformxml \"' 
        #                         + self.scenario.result_dir + '\\battery-report.xml /output ' + self.scenario.result_dir + '\\battery_report.html')

    def dataReadyCallback(self):
        if self.aluminium:
            for name, contents in self.reports.items():
                with open(os.path.join(self.scenario.result_dir, name), "w", encoding="utf-8", newline="\n") as report:
                    report.write(contents or "")
            if self.start is None or self.end is None:
                logging.warning("powercfg: no complete battery measurement is available.")
                return
            rows = aluminium_power.battery_summary(self.start, self.end, self.start_time, self.end_time)
            if self.start[2] or self.end[2]:
                logging.warning("powercfg: the DUT was on AC/USB power; battery-derived average power is unavailable.")
            elif not any(key == "battery_avg_power_mw" for key, _ in rows):
                logging.warning("powercfg: the charge counter did not change; the measurement was below its resolution.")
            aluminium_power.write_rows(
                os.path.join(self.scenario.result_dir, self.scenario.testname + "_powercfg_summary.csv"),
                rows,
            )
            return
        # You can do any post processing of data here.
        if self.platform.lower() == "wcos":
            self._host_call('%SystemRoot%\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe cmd.exe /c powercfg.exe /sleepstudy /transformxml ' 
                                + self.result_dir + '\\sleepstudy-report.xml /output ' + self.result_dir + '\\sleepstudy-report.html')
            if self.battery_report  == '1':
                    self._host_call('%SystemRoot%\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe cmd.exe /c powercfg.exe /batteryreport /transformxml \"' 
                                    + self.scenario.result_dir + '\\battery-report.xml /output ' + self.scenario.result_dir + '\\battery_report.html')
        else:
            sleep_study_path = os.path.join(self.result_dir, 'sleepstudy-report.xml')
            root = ET.parse(sleep_study_path).getroot()
            ns_prefix = root.tag.split('{')[1].split('}')[0]
            # ns = {'name_space': 'http://schemas.microsoft.com/sleepstudy/2012'}
            ns = {'name_space': ns_prefix}

            drips_under_percentage = 0
            drips_average = 0
            total_percentage = 0 
            count_drips = 0
            for buckets in root.findall('.//name_space:DripsBuckets',ns):
                ele = buckets.find('name_space:DripBucketId', ns)
                drip_percentage = 0
                for bucket in buckets.findall(".//name_space:DripsBucket", ns):
                    drip_percentage += int(bucket.get('TotalTimePercent'))
                total_percentage = total_percentage + drip_percentage
                count_drips = count_drips+1
                if drip_percentage < 80 :
                    drips_under_percentage = drips_under_percentage+1

            if count_drips != 0:
                drips_average = total_percentage // count_drips

            drips_csv = os.path.join(self.result_dir, "drips.csv")
            logging.info(drips_csv)
            row1 = ['Drips Average %', drips_average]
            row2 = ['Drips Session Under %80', drips_under_percentage]
            with open(drips_csv, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
                writer.writerow(row1)
                writer.writerow(row2)
        pass
