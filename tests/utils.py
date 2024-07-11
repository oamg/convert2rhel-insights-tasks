import json


def extract_json(stdout):
    delims = {
        "prefix": "### JSON START ###",
        "suffix": "### JSON END ###",
    }

    if delims["prefix"] not in stdout:
        return None
    start = stdout.index(delims["prefix"]) + len(delims["prefix"])
    if delims["suffix"] not in stdout:
        return None
    end = stdout.index(delims["suffix"], start)

    try:
        results = json.loads(stdout[start:end])
    except Exception:
        results = None
    return results
