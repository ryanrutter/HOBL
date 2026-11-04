# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Keep credential values from device profiles out of HOBL logs."""

import re

REDACTED = "********"

_SENSITIVE_KEY = re.compile(r"(password|passwd|secret|token|access_key|(^|_)pin$|(^|_)(account|username)$)", re.IGNORECASE)
_MIN_SECRET_LENGTH = 4
_secrets = set()


def is_sensitive_key(key):
    return bool(key) and _SENSITIVE_KEY.search(str(key)) is not None


def register(value):
    if value is None:
        return
    value = str(value).strip().strip('"')
    if len(value) >= _MIN_SECRET_LENGTH and value != "-1":
        _secrets.add(value)


def register_param(key, value):
    if is_sensitive_key(key):
        register(value)


def redact(text):
    if not _secrets or not isinstance(text, str):
        return text
    for secret in sorted(_secrets, key=len, reverse=True):
        if secret in text:
            text = text.replace(secret, REDACTED)
    return text


def clear():
    _secrets.clear()
