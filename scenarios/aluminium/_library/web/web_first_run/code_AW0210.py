# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging

import utilities.open_source.aluminium_browser as browser
import utilities.open_source.aluminium_ui as ui


# Chrome's and Edge's first-run and promotional prompts, and the button that dismisses each without signing in,
# turning on sync, allowing notifications, or changing the default browser.  Windows web_prep turns off the same
# prompts in Edge.  Each prompt is identified by its own text, so buttons on ordinary web pages are never tapped.
PROMPTS = [
    (["Welcome to Chrome", "Accept & continue"], ["Accept & continue", "Accept and continue"]),
    (["Sign in to Chrome", "Use without an account", "Sign in to browse"], ["Use without an account", "No thanks", "No, thanks"]),
    (["Turn on sync?", "Sync your passwords, history & more on all devices"], ["No thanks", "No, thanks", "Cancel"]),
    (["Chrome notifications make things easier"], ["No thanks", "No, thanks"]),
    (["Allow Chrome to send you notifications?"], ["Don't allow", "Don\u2019t allow"]),
    (["Make Chrome your default browser", "Set Chrome as your default browser?"], ["No thanks", "No, thanks", "Not now", "Cancel"]),
    (["Enhanced ad privacy in Chrome", "Ad privacy"], ["Got it", "No thanks", "No, thanks"]),
    (["Viewing full screen"], ["Got it"]),
    # Edge
    (["Set Edge as your default browser app?", "Set Edge Beta as your default browser app?", "Set Edge Dev as your default browser app?",
      "Set Edge Canary as your default browser app?"], ["Cancel"]),
    (["Sign in to sync"], ["Not now"]),
    (["Your data, your privacy"], ["Confirm"]),
    (["Allow Edge to send you notifications?", "Allow Edge Beta to send you notifications?", "Allow Edge Dev to send you notifications?",
      "Allow Edge Canary to send you notifications?"], ["Don't allow", "Don\u2019t allow"]),
    (["Personalize your web experience"], ["Not now"]),
]

MAX_PROMPTS = 10


def dismiss_next(scenario):
    '''Dismisses one known prompt.  Returns its title, or None when no known prompt is shown.'''
    root = ui.read_ui(scenario)
    for titles, buttons in PROMPTS:
        title = ui.find_any(root, titles)
        if title is None:
            continue
        button = ui.find_any(root, buttons)
        if button is not None:
            ui.tap(scenario, button, settle=2)
            return title.get("text") or title.get("content-desc")
    return None


def run(scenario):
    for _ in range(MAX_PROMPTS):
        title = dismiss_next(scenario)
        if title is None:
            return
        logging.info(f"Dismissed {browser.name()} prompt: {title}")
    scenario.fail(f"{browser.name()} kept showing first-run prompts.  Open it on the DUT, complete its setup, and run al_web_prep again.")
