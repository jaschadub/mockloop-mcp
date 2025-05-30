import json
from pathlib import Path

import requests
import yaml


def load_spec(path_or_url):
    if path_or_url.startswith("http"):
        content = requests.get(path_or_url, timeout=30).text
    else:
        content = Path(path_or_url).read_text()

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        return json.loads(content)
