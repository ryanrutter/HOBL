# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import collections
import json
import os

class Params(object):
    defaults = collections.OrderedDict()
    defaultsInfo = collections.OrderedDict()
    overrides = collections.OrderedDict()
    fileParams = collections.OrderedDict()
    calculated = collections.OrderedDict()

    def __init__(self, cfgfile):
        pass

    @classmethod
    def setOverrides(cls, override_list):
        for override in override_list:
            try:
                (section_key, val) = override.split('=', 1)
                (section, key) = section_key.split(':', 1)
                Params.setOverride(section, key, val)
            except:
                pass

    @classmethod
    def setOverride(cls, section, key, val):
        val = val.strip('"')
        if section not in Params.overrides:
            Params.overrides[section] = collections.OrderedDict()
        Params.overrides[section][key] = val

    @classmethod
    def setParam(cls, section, key, val):
        pass

    @classmethod
    def getSectionForKey(cls, key):
        return "global"

    @classmethod
    def deleteParam(cls, section, key):
        pass

    @classmethod
    def setDefault(cls, section, key, val, desc = "", valOptions = [], multiple = False):
        if section not in Params.defaults:
            Params.defaults[section] = collections.OrderedDict()
        Params.defaults[section][key] = val

        if section not in Params.defaultsInfo:
            Params.defaultsInfo[section] = collections.OrderedDict()
        Params.defaultsInfo[section][key] = {
            "desc": desc,
            "valOptions": valOptions,
            "multiple": multiple
        }

    @classmethod
    def setUserDefault(cls, section, key, val, desc = "", valOptions = [], multiple = False):
        if section is None:
            section = Params.getCalculated('scenario_section')

        if not section:
            return

        Params.setDefault(section, key, val, desc, valOptions, multiple)

    @classmethod
    def setCalculated(cls, key, val):
        Params.calculated[key] = val

    @classmethod
    def dump(cls):
        pass

    @classmethod
    def dumpDefault(cls):
        for section in Params.defaults:
            for key in Params.defaults[section]:
                val = Params.defaults[section][key]
                print(section + ":" + key)

    @classmethod
    def dumpDefaultWithInfo(cls, print_json=True):
        for section in Params.defaultsInfo:
            for key in Params.defaultsInfo[section]:
                valOptions = Params.defaultsInfo[section][key]["valOptions"]

                if len(valOptions) == 1 and valOptions[0].startswith("@\\"):
                    d = os.path.join(os.getcwd(), valOptions[0][2:])

                    for root, dirs, files in os.walk(d):
                            valOptions.extend(files)

                    del valOptions[0]

                Params.defaultsInfo[section][key]["valOptions"] = valOptions

        if print_json:
            print(json.dumps(Params.defaultsInfo))

    @classmethod
    def dumpResolved(cls):
       pass

    @classmethod
    def getCalculated(cls, key):
        try:
            val = Params.calculated[key]
        except:
            val = ""
        return val

    @classmethod
    def get(cls, section, key, log = True, recurse_init = True):
        if section in Params.overrides:
            if key in Params.overrides[section]:
                return Params.overrides[section][key]
        if section in Params.defaults:
            if key in Params.defaults[section]:
                return Params.defaults[section][key]
        return None

    @classmethod
    def get_raw(cls, section, key, log = True, recurse_init=False):
        return ""

    @classmethod
    def getKeysForSection(cls, section):
        keys = []
        return keys

    @classmethod
    def getOverride(cls, section, key, log = True):
        return ""

    @classmethod
    def getDefault(cls, section, key):
        if section in Params.defaults:
            if key in Params.defaults[section]:
                val = Params.defaults[section][key]
                return val
        return None

    @classmethod
    def getDefaults(cls, section):
        try:
            return Params.defaults[section]
        except:
            return dict()

    @classmethod
    def getFileParams(cls, section = None):
        if section == None:
            return Params.fileParams

        try:
            return Params.fileParams[section]
        except:
            return dict()

    @classmethod
    def getOverrides(cls, section = None):
        if section == None:
            return Params.overrides

        try:
            return Params.overrides[section]
        except:
            return dict()

    @classmethod
    def setAssociatedSections(cls, section, list):
        pass

    @classmethod
    def getAssociatedSections(cls, section):
        pass

    @classmethod
    def clear(cls):
        Params.overrides.clear()
        Params.fileParams.clear()
        Params.defaults.clear()
        Params.defaultsInfo.clear()

    @classmethod
    def clearOverrides(cls):
        Params.overrides.clear()

    @classmethod
    def clearFileParams(cls):
        Params.fileParams.clear()

    @classmethod
    def checkParams(cls):
        return True

    @classmethod
    def resolveHostIp(cls):
        return "127.0.0.1"

    @classmethod
    def resolveVars(cls, original):
        return ""

    @classmethod
    def expandStudyVars(cls):
        return ""


def get_hobl_version():
    return "Unknown"
