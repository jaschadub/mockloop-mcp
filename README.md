# MockAPI-MCP

This project creates a FastAPI mock server based on any OpenAPI spec input (YAML or JSON, local or URL). It's ideal for testing, mocking services, or scaffolding APIs rapidly.

## 🚀 Features

- Parse OpenAPI specs
- Auto-generate FastAPI routes
- Return dummy/mock JSON responses
- Hot-reloading with `uvicorn`
- Supports both local files and URLs

## 🧪 Usage

```bash
pip install -r requirements.txt
python main.py path_or_url_to_openapi.yaml
```

## 🛠 Future Ideas

- [ ] Add GraphQL and Postman support
- [ ] Inject auth headers using FastAPI's `Depends`
- [ ] Use OpenAPI examples if available
- [ ] Add CLI tool (e.g., `mockgen`)
- [ ] Create a REST MCP agent endpoint to run this
- [ ] Docker integration

## 📦 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py", "/app/api.yaml"]
```

---

MIT License
