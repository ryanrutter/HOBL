# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Sequential 128 KB disk writes
##

from core.parameters import Params
import scenarios.aluminium.al_read128kseq


class AlWrite128kseq(scenarios.aluminium.al_read128kseq.AlRead128kseq):
    '''
    Writes a 1 GB file sequentially in 128 KB blocks, bypassing the file cache, for the specified duration on an Aluminium (Android desktop) DUT.  The Aluminium version of write128kseq, using toybox dd with direct I/O instead of diskspd.  The throughput is written to disk_throughput.csv.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'block', '128', desc="Block size in KB")
    Params.setDefault(module, 'duration', '300', desc="Seconds")

    write = True
