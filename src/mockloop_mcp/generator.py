import os
import sys
import time
import json
import random
import string
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from jinja2 import Environment, FileSystemLoader

print("GENERATOR.PY TOP LEVEL PRINT STATEMENT - VERSION CHECK - FINAL") 

class APIGenerationError(Exception):
    """Custom exception for API generation errors."""
    pass

TEMPLATE_DIR = Path(__file__).parent / "templates"
if not TEMPLATE_DIR.is_dir():
    TEMPLATE_DIR = Path("src/mockloop_mcp/templates") 
    if not TEMPLATE_DIR.is_dir():
         raise APIGenerationError(f"Template directory not found at expected locations.")

jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)

def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    if isinstance(value, int):
        return value != 0
    return bool(value)

def _generate_mock_data_from_schema(schema: Dict[str, Any]) -> Any:
    if not schema: return None
    schema_type = schema.get("type")
    if schema_type == "string":
        format_type = schema.get("format", "")
        if format_type == "date-time": return "2023-01-01T00:00:00Z"
        if format_type == "date": return "2023-01-01"
        if format_type == "email": return "user@example.com"
        if format_type == "uuid": return "00000000-0000-0000-0000-000000000000"
        length = schema.get("minLength", 5)
        if schema.get("maxLength") and schema.get("maxLength") < length: length = schema.get("maxLength")
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    if schema_type == "number" or schema_type == "integer":
        minimum = schema.get("minimum", 0); maximum = schema.get("maximum", 100)
        return random.randint(minimum, maximum) if schema_type == "integer" else round(random.uniform(minimum, maximum), 2)
    if schema_type == "boolean": return random.choice([True, False])
    if schema_type == "array":
        items_schema = schema.get("items", {}); min_items = schema.get("minItems", 1); max_items = schema.get("maxItems", 3)
        num_items = random.randint(min_items, max_items)
        return [_generate_mock_data_from_schema(items_schema) for _ in range(num_items)]
    if schema_type == "object":
        result = {}; properties = schema.get("properties", {}); required = schema.get("required", [])
        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.3: result[prop_name] = _generate_mock_data_from_schema(prop_schema)
        return result
    if "$ref" in schema: return {"$ref_placeholder": schema["$ref"]}
    for key in ["oneOf", "anyOf"]:
        if key in schema and isinstance(schema[key], list) and len(schema[key]) > 0:
            return _generate_mock_data_from_schema(random.choice(schema[key]))
    if "allOf" in schema and isinstance(schema["allOf"], list) and len(schema["allOf"]) > 0:
        merged_schema = {}
        for sub_schema in schema["allOf"]:
            if isinstance(sub_schema, dict): merged_schema.update(sub_schema)
        return _generate_mock_data_from_schema(merged_schema)
    return "mock_data"

def generate_mock_api(
    spec_data: Dict[str, Any],
    output_base_dir: Union[str, Path] = None,
    mock_server_name: Optional[str] = None,
    auth_enabled: Any = True, 
    webhooks_enabled: Any = True,
    admin_ui_enabled: Any = True,
    storage_enabled: Any = True
) -> Path:
    auth_enabled_bool = _to_bool(auth_enabled)
    webhooks_enabled_bool = _to_bool(webhooks_enabled)
    admin_ui_enabled_bool = _to_bool(admin_ui_enabled)
    storage_enabled_bool = _to_bool(storage_enabled)

    print(f"Generator (Processed): auth_enabled: {auth_enabled_bool} (type: {type(auth_enabled_bool)}) from original: {auth_enabled}")
    print(f"Generator (Processed): webhooks_enabled: {webhooks_enabled_bool} (type: {type(webhooks_enabled_bool)}) from original: {webhooks_enabled}")
    print(f"Generator (Processed): admin_ui_enabled: {admin_ui_enabled_bool} (type: {type(admin_ui_enabled_bool)}) from original: {admin_ui_enabled}")
    print(f"Generator (Processed): storage_enabled: {storage_enabled_bool} (type: {type(storage_enabled_bool)}) from original: {storage_enabled}")

    try:
        api_title = spec_data.get("info", {}).get("title", "mock_api").lower().replace(" ", "_").replace("-", "_")
        api_version = spec_data.get("info", {}).get("version", "v1").lower().replace(".", "_")

        _mock_server_name = mock_server_name
        if not _mock_server_name:
            _mock_server_name = f"{api_title}_{api_version}_{int(time.time())}"
        
        _mock_server_name = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in _mock_server_name)

        _output_base_dir = output_base_dir
        if _output_base_dir is None:
            project_root = Path(__file__).parent.parent.parent
            _output_base_dir = project_root / "generated_mocks"
        
        mock_server_dir = Path(_output_base_dir) / _mock_server_name
        mock_server_dir.mkdir(parents=True, exist_ok=True)

        requirements_content = "fastapi\nuvicorn[standard]\n"
        
        with open(mock_server_dir / "requirements_mock.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)

        if auth_enabled_bool:
            auth_middleware_template = jinja_env.get_template("auth_middleware_template.j2")
            random_suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            auth_middleware_code = auth_middleware_template.render(random_suffix=random_suffix)
            with open(mock_server_dir / "auth_middleware.py", "w", encoding="utf-8") as f:
                f.write(auth_middleware_code)
            with open(mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8") as f: 
                f.write("pyjwt\n")
                f.write("python-multipart\n") # Add python-multipart here
        
        if webhooks_enabled_bool:
            webhook_template = jinja_env.get_template("webhook_template.j2")
            webhook_code = webhook_template.render()
            with open(mock_server_dir / "webhook_handler.py", "w", encoding="utf-8") as f:
                f.write(webhook_code)
            with open(mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8") as f: 
                f.write("httpx\n")
        
        if storage_enabled_bool:
            storage_template = jinja_env.get_template("storage_template.j2")
            storage_code = storage_template.render()
            with open(mock_server_dir / "storage.py", "w", encoding="utf-8") as f:
                f.write(storage_code)
            (mock_server_dir / "mock_data").mkdir(exist_ok=True)
        
        if admin_ui_enabled_bool:
            admin_ui_template = jinja_env.get_template("admin_ui_template.j2")
            admin_ui_code = admin_ui_template.render(
                api_title=spec_data.get("info", {}).get("title", "Mock API"),
                api_version=spec_data.get("info", {}).get("version", "1.0.0"),
                auth_enabled=auth_enabled_bool,
                webhooks_enabled=webhooks_enabled_bool,
                storage_enabled=storage_enabled_bool
            )
            (mock_server_dir / "templates").mkdir(exist_ok=True)
            with open(mock_server_dir / "templates" / "admin.html", "w", encoding="utf-8") as f:
                f.write(admin_ui_code)
            with open(mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8") as f: 
                f.write("jinja2\n")
        
        routes_code_parts: List[str] = []
        paths = spec_data.get("paths", {})
        for path_url, methods in paths.items():
            for method, details in methods.items():
                valid_methods = ["get", "post", "put", "delete", "patch", "options", "head", "trace"]
                if method.lower() not in valid_methods: continue
                path_params = ""
                parameters = details.get("parameters", [])
                path_param_list = []
                for param in parameters:
                    if param.get("in") == "path":
                        param_name = param.get("name"); param_type = param.get("schema", {}).get("type", "string")
                        python_type = "str"
                        if param_type == "integer": python_type = "int"
                        elif param_type == "number": python_type = "float"
                        elif param_type == "boolean": python_type = "bool"
                        path_param_list.append(f"{param_name}: {python_type}")
                if path_param_list: path_params = ", ".join(path_param_list)
                example_response = None 
                responses = details.get("responses", {})
                for status_code, response_info in responses.items():
                    if status_code.startswith("2"):
                        content = response_info.get("content", {})
                        for content_type, content_schema in content.items():
                            if "application/json" in content_type:
                                if "example" in content_schema: example_response = json.dumps(content_schema["example"]); break
                                schema = content_schema.get("schema", {})
                                if "example" in schema: example_response = json.dumps(schema["example"]); break
                                examples = content_schema.get("examples", {})
                                if examples:
                                    first_example = next(iter(examples.values()), {})
                                    if "value" in first_example: example_response = json.dumps(first_example["value"]); break
                        if example_response: break
                if not example_response:
                    for status_code, response_info in responses.items():
                        if status_code.startswith("2"):
                            content = response_info.get("content", {})
                            for content_type, content_schema in content.items():
                                if "application/json" in content_type:
                                    schema = content_schema.get("schema", {})
                                    mock_data = _generate_mock_data_from_schema(schema)
                                    if mock_data: example_response = json.dumps(mock_data); break
                            if example_response: break
                route_template = jinja_env.get_template("route_template.j2")
                route_code = route_template.render(method=method.lower(), path=path_url, summary=details.get("summary", f"{method.upper()} {path_url}"), path_params=path_params, example_response=example_response)
                routes_code_parts.append(route_code)
        all_routes_code = "\n\n".join(routes_code_parts)
        middleware_template = jinja_env.get_template("middleware_log_template.j2")
        logging_middleware_code = middleware_template.render()
        with open(mock_server_dir / "logging_middleware.py", "w", encoding="utf-8") as f: f.write(logging_middleware_code)
        
        common_imports = "from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Body, Query, Path\nfrom fastapi.responses import HTMLResponse, JSONResponse\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.staticfiles import StaticFiles\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom typing import List, Dict, Any, Optional\nimport json\nimport os\nimport time\nimport sqlite3\nfrom datetime import datetime\nfrom pathlib import Path\nfrom logging_middleware import LoggingMiddleware\n"
        auth_imports = "from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer\nfrom auth_middleware import verify_api_key, verify_jwt_token, generate_token_response\n" if auth_enabled_bool else ""
        webhook_imports = "from webhook_handler import register_webhook, get_webhooks, delete_webhook, get_webhook_history\n" if webhooks_enabled_bool else ""
        storage_imports = "from storage import StorageManager, get_storage_stats, get_collections\n" if storage_enabled_bool else ""
        imports_section = common_imports + auth_imports + webhook_imports + storage_imports
        app_setup = "app = FastAPI(title=\"{{ api_title }}\", version=\"{{ api_version }}\")\ntemplates = Jinja2Templates(directory=\"templates\")\napp.add_middleware(LoggingMiddleware)\napp.add_middleware(CORSMiddleware, allow_origins=[\"*\"], allow_credentials=True, allow_methods=[\"*\"], allow_headers=[\"*\"])\n\n# Setup database path for logs (same as in middleware)\ndb_dir = Path(\"db\")\ndb_dir.mkdir(exist_ok=True)\nDB_PATH = db_dir / \"request_logs.db\"\n"
        auth_endpoints_str = "@app.post(\"/token\", summary=\"Get access token\", tags=[\"authentication\"])\nasync def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):\n    return generate_token_response(form_data.username, form_data.password)\n" if auth_enabled_bool else ""
        
        admin_api_endpoints_str = ""
        if admin_ui_enabled_bool: 
            admin_api_endpoints_str = """
# --- Admin API Endpoints ---
@app.get("/admin/api/export", tags=["_admin"])
async def export_data():
    import io
    import zipfile
    from fastapi.responses import StreamingResponse
    
    # Create a BytesIO object to store the zip file
    zip_buffer = io.BytesIO()
    
    # Create a ZipFile object
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add request logs from SQLite to the zip
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all request logs
            cursor.execute("SELECT * FROM request_logs")
            rows = cursor.fetchall()
            
            # Convert to list of dicts for JSON serialization
            logs = []
            for row in rows:
                log_entry = dict(row)
                if "headers" in log_entry and log_entry["headers"]:
                    try:
                        log_entry["headers"] = json.loads(log_entry["headers"])
                    except:
                        log_entry["headers"] = {}
                logs.append(log_entry)
            
            # Add logs to the zip file
            zipf.writestr('request_logs.json', json.dumps(logs, indent=2))
            
            # Add database schema information
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schemas = cursor.fetchall()
            schema_info = {row[0].split()[2]: row[0] for row in schemas if row[0] is not None}
            zipf.writestr('database_schema.json', json.dumps(schema_info, indent=2))
            
            conn.close()
        except Exception as e:
            # If there's an error, add an error log to the zip
            zipf.writestr('db_export_error.txt', f"Error exporting database: {str(e)}")
    
        # Add configuration information
        config_info = {
            "api_title": app.title,
            "api_version": app.version,
            "server_time": datetime.now().isoformat(),
            "database_path": str(DB_PATH),
        }
        zipf.writestr('config.json', json.dumps(config_info, indent=2))
    
    # Reset the buffer position to the beginning
    zip_buffer.seek(0)
    
    # Return the zip file as a streaming response
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=mock-api-data.zip"
        }
    )

@app.get("/admin/api/requests", tags=["_admin"])
async def get_request_logs(limit: int = 100, offset: int = 0, method: str = None, path: str = None, include_admin: bool = False, id: int = None):
    try:
        
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT * FROM request_logs"
        params = []
        where_clauses = []
        
        # Filter by exact ID if provided
        if id is not None:
            where_clauses.append("id = ?")
            params.append(id)
        
        if method:
            where_clauses.append("method = ?")
            params.append(method)
        
        if path:
            where_clauses.append("path LIKE ?")
            params.append(f"%{path}%")
        
        # Filter out admin requests by default, but only if not querying by specific ID
        if not include_admin and id is None:
            where_clauses.append("(is_admin = 0 OR is_admin IS NULL)")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Skip limit/offset when querying by exact ID
        if id is not None:
            query += " ORDER BY id DESC"
        else:
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log_entry = dict(row)
            if "headers" in log_entry and log_entry["headers"]:
                try:
                    log_entry["headers"] = json.loads(log_entry["headers"])
                except:
                    log_entry["headers"] = {}
            logs.append(log_entry)
        
        conn.close()
        
        # If we're querying by ID and have a result, return just that single record instead of an array
        if id is not None and logs:
            return logs[0]
        
        return logs
    except Exception as e:
        print(f"Error getting request logs: {e}")
        return []

@app.get("/admin/api/debug", tags=["_admin"])
async def get_debug_info():
    debug_info = {
        "db_path_exists": os.path.exists(str(DB_PATH)),
        "db_directory_exists": os.path.exists(str(db_dir)),
        "db_path": str(DB_PATH),
        "working_directory": os.getcwd(),
        "db_dir_listing": os.listdir(str(db_dir)) if os.path.exists(str(db_dir)) else None,
        "sqlite_version": sqlite3.version
    }
    
    # Try to check the database tables
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        debug_info["tables"] = [table[0] for table in tables]
        
        # Check if request_logs table exists and get count
        if tables and any("request_logs" in table[0] for table in tables):
            cursor.execute("SELECT COUNT(*) FROM request_logs")
            debug_info["request_logs_count"] = cursor.fetchone()[0]
            
            # Get sample data if available
            cursor.execute("SELECT * FROM request_logs LIMIT 1")
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                if rows:
                    debug_info["sample_log"] = dict(zip(columns, rows[0]))
                else:
                    debug_info["sample_log"] = None
        
        conn.close()
    except Exception as e:
        debug_info["db_error"] = str(e)
    
    return debug_info

@app.get("/admin/api/requests/stats", tags=["_admin"])
async def get_request_stats():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        stats = {"total_requests": 0}
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM request_logs")
        result = cursor.fetchone()
        if result:
            stats["total_requests"] = result[0]
        
        # Count by method
        cursor.execute("SELECT method, COUNT(*) FROM request_logs GROUP BY method")
        stats["methods"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count by status code
        cursor.execute("SELECT status_code, COUNT(*) FROM request_logs GROUP BY status_code")
        stats["status_codes"] = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Average response time
        cursor.execute("SELECT AVG(process_time_ms) FROM request_logs")
        avg_time = cursor.fetchone()
        stats["avg_response_time"] = avg_time[0] if avg_time and avg_time[0] is not None else 0
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting request stats: {e}")
        return {"error": str(e), "total_requests": 0}
"""
        webhook_api_endpoints_str = ""
        if webhooks_enabled_bool and admin_ui_enabled_bool: 
            webhook_api_endpoints_str = """
@app.get("/admin/api/webhooks", tags=["_admin"])
async def admin_get_webhooks(): return get_webhooks()
@app.post("/admin/api/webhooks", tags=["_admin"])
async def admin_register_webhook(event_type: str = Body(..., embed=True), url: str = Body(..., embed=True), description: Optional[str] = Body(None, embed=True)):
    return register_webhook(event_type, url, description)
@app.delete("/admin/api/webhooks/{webhook_id}", tags=["_admin"])
async def admin_delete_webhook(webhook_id: str): return delete_webhook(webhook_id)
@app.get("/admin/api/webhooks/history", tags=["_admin"])
async def admin_get_webhook_history(): return get_webhook_history()
"""
        storage_api_endpoints_str = ""
        if storage_enabled_bool and admin_ui_enabled_bool: 
            storage_api_endpoints_str = """
@app.get("/admin/api/storage/stats", tags=["_admin"])
async def admin_get_storage_stats(): return get_storage_stats()
@app.get("/admin/api/storage/collections", tags=["_admin"])
async def admin_get_collections(): return get_collections()
"""

        admin_ui_endpoint_str = f'''
@app.get("/admin", response_class=HTMLResponse, summary="Admin UI", tags=["_system"])
async def read_admin_ui(request: Request):
    return templates.TemplateResponse("admin.html", {{
        "request": request,
        "api_title": "{api_title}",
        "api_version": "{api_version}",
        "auth_enabled": {auth_enabled_bool},
        "webhooks_enabled": {webhooks_enabled_bool},
        "storage_enabled": {storage_enabled_bool}
    }})
''' if admin_ui_enabled_bool else "@app.get(\"/admin\")\nasync def no_admin(): return {'message': 'Admin UI not enabled'}"

        health_endpoint_str = "@app.get(\"/health\", summary=\"Health check endpoint\", tags=[\"_system\"])\nasync def health_check(): return {\"status\": \"healthy\"}\n"
        main_section_str = "if __name__ == \"__main__\":\n    import uvicorn\n    uvicorn.run(app, host=\"0.0.0.0\", port={{ default_port }})\n"
        
        main_app_template_str = imports_section + app_setup + auth_endpoints_str + "\n# --- Generated Routes ---\n{{ routes_code }}\n# --- End Generated Routes ---\n" + admin_api_endpoints_str + webhook_api_endpoints_str + storage_api_endpoints_str + admin_ui_endpoint_str + health_endpoint_str + main_section_str
        main_app_jinja_template = jinja_env.from_string(main_app_template_str)
        main_py_content = main_app_jinja_template.render(
            api_title=api_title, api_version=api_version, routes_code=all_routes_code, default_port=8000
        )
        with open(mock_server_dir / "main.py", "w", encoding="utf-8") as f: f.write(main_py_content)

        dockerfile_template = jinja_env.get_template("dockerfile_template.j2")
        dockerfile_content = dockerfile_template.render(
            python_version="3.9-slim", port=8000,
            auth_enabled=auth_enabled_bool, webhooks_enabled=webhooks_enabled_bool,
            storage_enabled=storage_enabled_bool, admin_ui_enabled=admin_ui_enabled_bool
        )
        with open(mock_server_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        
        compose_template = jinja_env.get_template("docker_compose_template.j2")
        timestamp_for_id = str(int(time.time()))[-6:]
        raw_api_title = spec_data.get("info", {}).get("title", "mock_api")
        clean_service_name = ''.join(c if c.isalnum() else '-' for c in raw_api_title.lower())
        while '--' in clean_service_name: clean_service_name = clean_service_name.replace('--', '-')
        clean_service_name = clean_service_name.strip('-')
        if not clean_service_name: clean_service_name = 'mock-api'
        final_service_name = f"{clean_service_name}-mock"
        compose_content = compose_template.render(
            service_name=final_service_name, host_port=8000, container_port=8000, timestamp_id=timestamp_for_id
        )
        with open(mock_server_dir / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(compose_content)
        
        return mock_server_dir

    except Exception as e:
        raise APIGenerationError(f"Failed to generate mock API: {e}") from e

if __name__ == '__main__':
    dummy_spec = {"openapi": "3.0.0", "info": {"title": "Test API", "version": "1.0.1"}, "paths": {"/items": {"get": {"summary": "Get all items"}}}}
    try:
        generated_path = generate_mock_api(dummy_spec, mock_server_name="my_test_api_main")
        print(f"Successfully generated: {generated_path.resolve()}")
    except APIGenerationError as e: print(f"Error: {e}")
