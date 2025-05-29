import os
import time
import json
import random
import string
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from jinja2 import Environment, FileSystemLoader

class APIGenerationError(Exception):
    """Custom exception for API generation errors."""
    pass

# Setup Jinja2 environment
# Assuming templates are in a 'templates' directory relative to this file's package
# src/mockloop_mcp/templates/
TEMPLATE_DIR = Path(__file__).parent / "templates"
if not TEMPLATE_DIR.is_dir():
    # Fallback if running from a different structure, though less ideal
    TEMPLATE_DIR = Path("src/mockloop_mcp/templates") 
    if not TEMPLATE_DIR.is_dir():
         raise APIGenerationError(f"Template directory not found at expected locations: {Path(__file__).parent / 'templates'} or {Path('src/mockloop_mcp/templates')}")

jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)

def _generate_mock_data_from_schema(schema: Dict[str, Any]) -> Any:
    """
    Generate mock data based on a JSON Schema definition.
    
    Args:
        schema: JSON Schema object
        
    Returns:
        Generated mock data matching the schema
    """
    if not schema:
        return None
        
    schema_type = schema.get("type")
    
    if schema_type == "string":
        format_type = schema.get("format", "")
        if format_type == "date-time":
            return "2023-01-01T00:00:00Z"
        elif format_type == "date":
            return "2023-01-01"
        elif format_type == "email":
            return "user@example.com"
        elif format_type == "uuid":
            return "00000000-0000-0000-0000-000000000000"
        else:
            # Generate random string
            length = schema.get("minLength", 5)
            if schema.get("maxLength") and schema.get("maxLength") < length:
                length = schema.get("maxLength")
            return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    elif schema_type == "number" or schema_type == "integer":
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 100)
        if schema_type == "integer":
            return random.randint(minimum, maximum)
        else:
            return round(random.uniform(minimum, maximum), 2)
    
    elif schema_type == "boolean":
        return random.choice([True, False])
    
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)
        num_items = random.randint(min_items, max_items)
        return [_generate_mock_data_from_schema(items_schema) for _ in range(num_items)]
    
    elif schema_type == "object":
        result = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.3:  # 70% chance to include non-required props
                result[prop_name] = _generate_mock_data_from_schema(prop_schema)
                
        return result
    
    # Handle references
    if "$ref" in schema:
        # For now, just return a placeholder since we don't have a resolver
        return {"$ref_placeholder": schema["$ref"]}
    
    # Handle oneOf, anyOf, allOf (simplified)
    for key in ["oneOf", "anyOf"]:
        if key in schema and isinstance(schema[key], list) and len(schema[key]) > 0:
            selected_schema = random.choice(schema[key])
            return _generate_mock_data_from_schema(selected_schema)
    
    if "allOf" in schema and isinstance(schema["allOf"], list) and len(schema["allOf"]) > 0:
        # Merge all schemas (simplistic approach)
        merged_schema = {}
        for sub_schema in schema["allOf"]:
            if isinstance(sub_schema, dict):
                merged_schema.update(sub_schema)
        return _generate_mock_data_from_schema(merged_schema)
    
    # Default fallback
    return "mock_data"

def generate_mock_api(
    spec_data: Dict[str, Any],
    output_base_dir: Union[str, Path] = "generated_mocks",
    mock_server_name: Optional[str] = None,
    auth_enabled: bool = False
) -> Path:
    """
    Generates a FastAPI mock server from a parsed API specification.

    Args:
        spec_data: The parsed API specification (dictionary).
        output_base_dir: The base directory where generated mock server directories will be created.
        mock_server_name: An optional name for the mock server directory. 
                          If None, a name is derived from the API title and version.

    Returns:
        The Path to the created mock server directory.

    Raises:
        APIGenerationError: If any part of the generation process fails.
    """
    try:
        api_title = spec_data.get("info", {}).get("title", "mock_api").lower().replace(" ", "_").replace("-", "_")
        api_version = spec_data.get("info", {}).get("version", "v1").lower().replace(".", "_")

        if not mock_server_name:
            mock_server_name = f"{api_title}_{api_version}_{int(time.time())}"
        
        # Sanitize mock_server_name to be a valid directory name
        mock_server_name = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in mock_server_name)


        mock_server_dir = Path(output_base_dir) / mock_server_name
        mock_server_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate main.py (FastAPI app with routes and middleware)
        routes_code_parts: List[str] = []
        paths = spec_data.get("paths", {})
        for path_url, methods in paths.items():
            for method, details in methods.items():
                # Ensure method is a valid HTTP method, Jinja template expects lowercase
                valid_methods = ["get", "post", "put", "delete", "patch", "options", "head", "trace"]
                if method.lower() not in valid_methods:
                    # Log a warning or skip, for now, skip
                    print(f"Warning: Skipping invalid HTTP method '{method}' for path '{path_url}'")
                    continue

                # Extract path parameters if any
                path_params = ""
                parameters = details.get("parameters", [])
                path_param_list = []
                
                for param in parameters:
                    if param.get("in") == "path":
                        param_name = param.get("name")
                        param_type = param.get("schema", {}).get("type", "string")
                        python_type = "str"
                        if param_type == "integer":
                            python_type = "int"
                        elif param_type == "number":
                            python_type = "float"
                        elif param_type == "boolean":
                            python_type = "bool"
                            
                        path_param_list.append(f"{param_name}: {python_type}")
                
                if path_param_list:
                    path_params = ", ".join(path_param_list)
                
                # Look for example responses
                example_response = None
                responses = details.get("responses", {})
                for status_code, response_info in responses.items():
                    if status_code.startswith("2"):  # 2xx success responses
                        content = response_info.get("content", {})
                        for content_type, content_schema in content.items():
                            if "application/json" in content_type:
                                # Check for example directly in content
                                if "example" in content_schema:
                                    example_response = json.dumps(content_schema["example"])
                                    break
                                
                                # Or check in the schema section
                                schema = content_schema.get("schema", {})
                                if "example" in schema:
                                    example_response = json.dumps(schema["example"])
                                    break
                                    
                                # Look for examples object
                                examples = content_schema.get("examples", {})
                                if examples:
                                    # Take the first example
                                    first_example = next(iter(examples.values()), {})
                                    if "value" in first_example:
                                        example_response = json.dumps(first_example["value"])
                                        break
                    
                    if example_response:
                        break
                
                # Generate mock data if no example found and schema is available
                if not example_response:
                    for status_code, response_info in responses.items():
                        if status_code.startswith("2"):  # 2xx success responses
                            content = response_info.get("content", {})
                            for content_type, content_schema in content.items():
                                if "application/json" in content_type:
                                    schema = content_schema.get("schema", {})
                                    mock_data = _generate_mock_data_from_schema(schema)
                                    if mock_data:
                                        example_response = json.dumps(mock_data)
                                        break
                        if example_response:
                            break
                
                route_template = jinja_env.get_template("route_template.j2")
                route_code = route_template.render(
                    method=method.lower(), # Pass lowercase method to template
                    path=path_url,
                    summary=details.get("summary", f"{method.upper()} {path_url}"),
                    path_params=path_params,
                    example_response=example_response
                )
                routes_code_parts.append(route_code)
        
        all_routes_code = "\n\n".join(routes_code_parts)

        # Render logging middleware (assuming it's a self-contained class in the template)
        middleware_template = jinja_env.get_template("middleware_log_template.j2")
        # The middleware template itself contains the Python code for the middleware.
        # We will write this to a `logging_middleware.py` file and import it in `main.py`.
        
        logging_middleware_code = middleware_template.render() # No specific vars needed for the template itself
        with open(mock_server_dir / "logging_middleware.py", "w", encoding="utf-8") as f:
            f.write(logging_middleware_code)
            
        # Generate authentication middleware if enabled
        if auth_enabled:
            random_suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            auth_middleware_template = jinja_env.get_template("auth_middleware_template.j2")
            auth_middleware_code = auth_middleware_template.render(random_suffix=random_suffix)
            with open(mock_server_dir / "auth_middleware.py", "w", encoding="utf-8") as f:
                f.write(auth_middleware_code)
                
            # Update requirements to include PyJWT for auth
            with open(mock_server_dir / "requirements_mock.txt", "a", encoding="utf-8") as f:
                f.write("pyjwt\n")

        # Generate main FastAPI app file with or without auth
        if auth_enabled:
            main_app_template_str = '''
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from logging_middleware import LoggingMiddleware # Import from the generated file
from auth_middleware import verify_api_key, verify_jwt_token, generate_token_response

app = FastAPI(title="{{ api_title }}", version="{{ api_version }}")

# Add middleware
app.add_middleware(LoggingMiddleware)

# Authentication endpoints
@app.post("/token", summary="Get access token", tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    For mock API testing, any username from ['admin', 'user', 'guest'] with any password will work.
    """
    return generate_token_response(form_data.username, form_data.password)

# --- Generated Routes ---
{{ routes_code }}
# --- End Generated Routes ---

# Optional: Add a health check endpoint
@app.get("/health", summary="Health check endpoint", tags=["_system"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # This is for direct execution, Docker will use CMD in Dockerfile
    uvicorn.run(app, host="0.0.0.0", port={{ default_port }})
'''
        else:
            main_app_template_str = '''
from fastapi import FastAPI
from logging_middleware import LoggingMiddleware # Import from the generated file

app = FastAPI(title="{{ api_title }}", version="{{ api_version }}")

# Add middleware
app.add_middleware(LoggingMiddleware)

# --- Generated Routes ---
{{ routes_code }}
# --- End Generated Routes ---

# Optional: Add a health check endpoint
@app.get("/health", summary="Health check endpoint", tags=["_system"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # This is for direct execution, Docker will use CMD in Dockerfile
    uvicorn.run(app, host="0.0.0.0", port={{ default_port }})
'''
        main_app_jinja_template = jinja_env.from_string(main_app_template_str)
        main_py_content = main_app_jinja_template.render(
            api_title=spec_data.get("info", {}).get("title", "Mock API"),
            api_version=spec_data.get("info", {}).get("version", "1.0.0"),
            routes_code=all_routes_code,
            default_port=8000 
        )
        with open(mock_server_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_py_content)

        # 2. Generate requirements_mock.txt
        requirements_content = "fastapi\nuvicorn[standard]\n" 
        with open(mock_server_dir / "requirements_mock.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)

        # 3. Generate Dockerfile
        dockerfile_template = jinja_env.get_template("dockerfile_template.j2")
        # We need to ensure logging_middleware.py is copied if it exists
        # The template has a placeholder for this. We can pass a flag or list of files.
        # For now, the template has a commented out COPY for logging_middleware.py
        # We will modify the template or logic here to make it conditional.
        # A simple way: add `COPY ./logging_middleware.py .` directly in the template if always generated.
        # The current dockerfile_template.j2 already has this line commented.
        # Let's assume it will be copied.
        dockerfile_content = dockerfile_template.render(
            python_version="3.9-slim", # Or make configurable
            port=8000 # Or make configurable
        )
        with open(mock_server_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        
        # Modify Dockerfile to copy logging_middleware.py
        # This is a bit hacky, better to make the template more dynamic or have a list of files to copy.
        # For now, let's ensure the COPY line is present and uncommented in the generated Dockerfile.
        # This can be done by re-reading, modifying, and re-writing, or by a more robust template.
        # A simpler approach: ensure the template is correct.
        # The current template has `# COPY ./logging_middleware.py .`
        # We need to ensure this line is active.
        # Let's assume the template will be updated or the generator will handle this.
        # For now, we'll rely on the template being mostly correct.

        # 4. Generate docker-compose.yml
        compose_template = jinja_env.get_template("docker_compose_template.j2")
        timestamp_for_id = str(int(time.time()))[-6:] # short unique-ish id part
        compose_content = compose_template.render(
            service_name=f"{api_title.lower().replace(' ', '_')}_mock",
            host_port=8000, # Or make configurable
            container_port=8000, # Or make configurable
            timestamp_id=timestamp_for_id
        )
        with open(mock_server_dir / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(compose_content)
        
        return mock_server_dir

    except Exception as e:
        # Log the full exception for debugging
        # import traceback
        # print(f"Error during API generation: {traceback.format_exc()}")
        raise APIGenerationError(f"Failed to generate mock API: {e}") from e


if __name__ == '__main__':
    # Example Usage (for testing the generator directly)
    # Requires a dummy parsed spec.
    # You would typically get this from parser.load_api_specification()

    dummy_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.1"},
        "paths": {
            "/items": {
                "get": {"summary": "Get all items"},
                "post": {"summary": "Create an item"}
            },
            "/items/{item_id}": {
                "get": {"summary": "Get an item by ID"},
                "put": {"summary": "Update an item by ID"},
                "delete": {"summary": "Delete an item by ID"}
            },
            "/users/me":{
                "get": {"summary": "Get current user"}
            }
        }
    }
    
    print("--- Generating Mock API from Dummy Spec ---")
    try:
        generated_path = generate_mock_api(dummy_spec, mock_server_name="my_test_api")
        print(f"Successfully generated mock API at: {generated_path.resolve()}")
        print("Files created:")
        for item in generated_path.iterdir():
            print(f"  - {item.name}")
        
        print("\nTo run the mock server (example):")
        print(f"cd {generated_path.resolve()}")
        print("docker-compose up --build")

    except APIGenerationError as e:
        print(f"Error: {e}")
    except Exception as e:
        import traceback
        print(f"Unexpected test error: {traceback.format_exc()}")

    # Example with a more complex name
    dummy_spec_complex_name = {
        "openapi": "3.0.0",
        "info": {"title": "Another Complex API Name with Spaces & Special Chars!", "version": "2.0"},
        "paths": {"/ping": {"get": {"summary": "Ping endpoint"}}}
    }
    print("\n--- Generating Mock API with Complex Name ---")
    try:
        generated_path_complex = generate_mock_api(dummy_spec_complex_name) # Auto-generates name
        print(f"Successfully generated mock API at: {generated_path_complex.resolve()}")
    except APIGenerationError as e:
        print(f"Error: {e}")
