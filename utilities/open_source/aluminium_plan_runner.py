# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Dashboard plan launch helper used by Aluminium prep scenarios."""

import logging
import os
from urllib.parse import urlencode, urlparse, urlunparse

import requests

import core.arguments
from core.parameters import Params


def run_plans(scenario, prep_list, plans_to_launch):
    import scenarios.common.prep as prep_module

    prep = prep_module.Prep()
    prep.scenarios_to_prep = prep_list
    pending = prep.get_prep_scenarios()
    if pending:
        names = [entry[0] if isinstance(entry, tuple) else entry for entry in pending]
        scenario.fail(f"Preps still pending: {', '.join(names)}")

    dashboard = Params.get("global", "dashboard_url")
    if not dashboard:
        scenario.fail("global:dashboard_url is required to launch follow-up test plans.")
    profile_path = core.arguments.args.profile
    if not profile_path:
        scenario.fail("A profile is required to launch follow-up test plans.")

    profile = os.path.basename(profile_path).rsplit(".", 1)[0]
    url = urlunparse(urlparse(dashboard)._replace(path="/plan/RunPlan"))
    study_type = Params.getOverride("global", "study_type")
    for plan in plans_to_launch:
        query = {"profile": profile, "plan": plan}
        if study_type:
            query["studyType"] = study_type
        response = requests.get(f"{url}?{urlencode(query)}", timeout=30)
        response.raise_for_status()
        logging.info("Launched %s for profile %s: %s", plan, profile, response)
