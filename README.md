# My FastAPI App

A minimal FastAPI application.

## Quick Start

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd my_fastapi_app
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
```

Activate it:

- **Linux / macOS**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
uvicorn app.main:app --reload
```

### 5. Test the app
Open your browser and go to:

- Root endpoint → [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
  Response:
  ```json
  { "status": "ok", "docs": "/docs" }
  ```

- Interactive API docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
