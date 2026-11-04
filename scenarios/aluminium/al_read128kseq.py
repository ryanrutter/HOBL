# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Sequential 128 KB disk reads
##

import logging
import os
import time
import core.app_scenario
from core.parameters import Params


FILE_MB = 1024


class AlRead128kseq(core.app_scenario.Scenario):
    '''
    Reads a 1 GB file sequentially in 128 KB blocks, bypassing the file cache, for the specified duration on an Aluminium (Android desktop) DUT.  The Aluminium version of read128kseq, using toybox dd with direct I/O instead of diskspd.  The throughput is written to disk_throughput.csv.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'block', '128', desc="Block size in KB")
    Params.setDefault(module, 'duration', '300', desc="Seconds")

    write = False

    def setUp(self):
        self.block = int(Params.get(self.module, 'block'))
        self.duration = int(Params.get(self.module, 'duration'))
        self.test_dir = self.dut_exec_path + "/al_disk"
        self.test_file = self.test_dir + "/1Gseq.tmp"
        size = self._call(["sh", f"-c \"stat -c %s {self.test_file} 2>/dev/null || echo 0\""]).strip()
        if size != str(FILE_MB * 1024 * 1024):
            logging.info("Creating the 1 GB test file")
            self._call(["mkdir", f"-p {self.test_dir}"])
            self._call(["sh", f"-c \"dd if=/dev/zero of={self.test_file} bs=1m count={FILE_MB} conv=fsync 2>/dev/null\""], timeout=600)
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        kind = "write" if self.write else "read"
        blocks = FILE_MB * 1024 // self.block
        if self.write:
            transfer = f"dd if=/dev/zero of={self.test_file} bs={self.block}k count={blocks} oflag=direct conv=notrunc 2>/dev/null"
        else:
            transfer = f"dd if={self.test_file} of=/dev/null bs={self.block}k iflag=direct 2>/dev/null"
        logging.info(f"Performing {self.block}K block sequential {kind} test for {self.duration} seconds")
        start = time.time()
        # Whole passes over the file, until the duration has elapsed.
        output = self._call(["sh", f"-c \"end=$(($(date +%s) + {self.duration})); n=0; while [ $(date +%s) -lt $end ]; do {transfer} || exit 1; n=$((n+1)); done; echo passes=$n\""], timeout=self.duration + 600)
        elapsed = time.time() - start
        passes = int(output.strip().rsplit("passes=", 1)[-1])
        mb_per_s = passes * FILE_MB / elapsed
        logging.info(f"Sequential {kind}: {passes} passes of {FILE_MB} MB in {elapsed:.0f}s, {mb_per_s:.0f} MB/s")
        with open(os.path.join(self.result_dir, "disk_throughput.csv"), "w") as f:
            f.write(f"disk_seq_{kind}_mb_per_s,{mb_per_s:.1f}\n")

    def kill(self):
        try:
            self._call(["pkill", "-f \"^dd .*1Gseq.tmp\""], expected_exit_code="")
        except Exception:
            pass
        return 0
