from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader("templates"))

def generate_routes(spec: dict, output_path: str):
    template = env.get_template("route_template.j2")
    paths = spec.get("paths", {})

    routes_code = ""
    for path, methods in paths.items():
        for method, details in methods.items():
            route = template.render(
                method=method,
                path=path.replace("{", "{"),
                summary=details.get("summary", ""),
                response_body={"message": "mock response"},
            )
            routes_code += route + "\n"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(f"from fastapi import FastAPI\n\napp = FastAPI()\n\n{routes_code}")
