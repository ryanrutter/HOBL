# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from core.app_scenario import Scenario
import logging
import re
import time


TRACE_DIR = "/data/misc/perfetto-traces"


class Tool(Scenario):
    '''
    Aluminium only.  Records a Perfetto system trace during the test, the Android equivalent of the Windows etl_trace tool.  The trace is copied to the results as <test name>.pftrace and can be opened at https://ui.perfetto.dev.  Tracing has some power impact, so don't use it for measured runs.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'categories', 'sched freq idle power am wm gfx view', desc="Space-separated atrace and ftrace categories to record; see 'perfetto --help' on the DUT.")
    Params.setDefault(module, 'buffer', '64mb', desc="Trace buffer size; when it is full, the oldest data is overwritten.")

    def initCallback(self, scenario):
        self.scenario = scenario
        self.pid = None

    def testBeginCallback(self):
        if self.platform.lower() != "aluminium":
            logging.warning("The perfetto_trace tool is only supported on Aluminium.")
            return
        categories = Params.get(self.module, 'categories')
        buffer_size = Params.get(self.module, 'buffer')
        self.trace = f"{TRACE_DIR}/{self.scenario.testname}.pftrace"
        output = self._call(["sh", f"-c \"rm -f {self.trace}; perfetto --background -o {self.trace} -t 24h -b {buffer_size} {categories}\""])
        match = re.search(r"(\d+)\s*$", output or "")
        if not match:
            logging.error(f"Perfetto tracing did not start: {output}")
            return
        self.pid = match.group(1)
        logging.info("Perfetto tracing started.")

    def testEndCallback(self):
        if not self.pid:
            return
        try:
            self._call(["kill", f"-TERM {self.pid}"], expected_exit_code="")
            for _ in range(30):
                if self._call(["sh", f"-c \"kill -0 {self.pid} 2>/dev/null && echo running\""], expected_exit_code="").strip() != "running":
                    break
                time.sleep(1)
            self._call(["sh", f"-c \"cp {self.trace} {self.scenario.dut_data_path}/ && rm -f {self.trace}\""])
            logging.info("Perfetto tracing stopped.")
        except Exception as e:
            logging.warning(f"Could not stop Perfetto tracing: {e}")
        self.pid = None

    def testScenarioFailed(self):
        self.testEndCallback()

    def testTimeoutCallback(self):
        self.pid = None

    def dataReadyCallback(self):
        pass
