from __future__ import annotations

import json
from enum import Enum
from json import JSONEncoder

from flask.json.provider import JSONProvider


class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder that handles Enums"""

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # Return the enum's string value
        return super(CustomJSONEncoder, self).default(obj)


class CustomJSONProvider(JSONProvider):
    """Custom JSON provider uses `CustomJSONEncoder` and is capable to serialize Enums"""
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s: str | bytes, **kwargs):
        return json.loads(s, **kwargs)