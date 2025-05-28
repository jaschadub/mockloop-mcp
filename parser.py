import json
import yaml
import requests

def load_spec(path_or_url):
    if path_or_url.startswith("http"):
        content = requests.get(path_or_url).text
    else:
        with open(path_or_url, "r") as f:
            content = f.read()

    try:
        return yaml.safe_load(content)
    except:
        return json.loads(content)
