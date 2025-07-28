# Server Launch Guide for All Agents

## ✅ Problem Solved
The Node.js error `spawn ps ENOENT` has been resolved by installing `procps` in the container.

## 🚀 Correct Server Launch Method

### For Development/Testing:
```bash
# Set the correct Python path
export PYTHONPATH=/workspace/src

# Launch the server
python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### For Background Execution:
```bash
# Set the correct Python path and run in background
export PYTHONPATH=/workspace/src && python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 &
```

### For Process Management:
```bash
# Check if server is running
ps aux | grep uvicorn

# Kill server process (replace PID with actual process ID)
kill <PID>
```

## 🔧 Why This Works
1. **PYTHONPATH**: Sets the correct module path so Python can find `src.app.main`
2. **Module Import**: Uses `src.app.main:app` instead of `app.main:app`
3. **Working Directory**: Must be run from `/workspace`

## ❌ What Doesn't Work
- `poetry run python -m app.main` (wrong module path)
- `poetry run uvicorn app.main:app` (wrong module path)
- Running without setting PYTHONPATH

## 📝 For All Agents
When testing the server or running it for verification:
1. Always use the `export PYTHONPATH=/workspace/src` method
2. Use `ps aux | grep uvicorn` to check if server is running
3. Use `kill <PID>` to terminate the server
4. The server should start without Node.js errors now that procps is installed

## 🐳 Docker Container Notes
- `procps` package has been installed to provide `ps` command
- This resolves the Node.js process management errors
- All process management commands now work correctly 