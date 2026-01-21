# Windows Setup (C:\Python314)

If you are on Windows and want to create a project-local virtual environment using a system Python installed at `C:\Python314\python.exe`, run the bundled PowerShell helper and follow these steps:

```powershell
# Create venv and install dev dependencies
.\scripts\create_venv_windows.ps1 -PythonPath 'C:\\Python314\\python.exe'

# Activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# Run the API
python -m api.main
```

Notes:
- The script will attempt `pip install -e .[dev]` and fall back to `requirements-dev.txt`.
- Keep your `OPENAI_API_KEY` in `.env` (do not commit `.env` to git).
