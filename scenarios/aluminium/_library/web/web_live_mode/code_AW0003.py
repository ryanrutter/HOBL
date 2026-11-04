# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging


def run(scenario):
    logging.info("Clearing the Android global proxy for live web traffic")
    scenario._call(["settings", "put global http_proxy :0"])
    scenario._sleep_to_now()
