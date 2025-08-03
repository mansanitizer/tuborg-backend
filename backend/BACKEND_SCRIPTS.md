# Backend Reset Scripts

This directory contains scripts to reset and restart the Webhound backend with a clean state.

## Scripts Overview

### 1. `reset_backend.sh` - Full Reset Script
**Use this for:** Complete environment reset, troubleshooting, or first-time setup

**Features:**
- ✅ Kills all related processes
- ✅ Cleans Python cache
- ✅ Optional database cleanup
- ✅ Checks Python environment
- ✅ Verifies virtual environment
- ✅ Tests dependencies
- ✅ Validates database functionality
- ✅ Starts server with health checks

**Usage:**
```bash
./reset_backend.sh
```

**What it does:**
1. **Process Cleanup**: Kills all uvicorn and Python processes
2. **Port Management**: Waits for ports 8000, 8001, 8002 to be free
3. **Cache Cleanup**: Removes `__pycache__` directories
4. **Database Options**: Asks if you want to delete existing database
5. **Environment Check**: Verifies Python and virtual environment
6. **Dependency Check**: Tests if all requirements are installed
7. **Database Test**: Validates SQLite functionality
8. **Server Start**: Starts uvicorn with health monitoring

### 2. `quick_reset.sh` - Quick Reset Script
**Use this for:** Fast development restarts, when you just need a clean restart

**Features:**
- ⚡ Fast execution (no prompts)
- ⚡ Minimal checks
- ⚡ Quick process cleanup
- ⚡ Immediate server start

**Usage:**
```bash
./quick_reset.sh
```

**What it does:**
1. **Quick Cleanup**: Kills uvicorn and Python processes
2. **Cache Clean**: Removes `__pycache__`
3. **Fast Start**: Starts server immediately

## When to Use Each Script

### Use `reset_backend.sh` when:
- 🔧 **Troubleshooting issues**
- 🆕 **First-time setup**
- 🧹 **Complete cleanup needed**
- 🐛 **Debugging problems**
- 🔄 **After major changes**

### Use `quick_reset.sh` when:
- ⚡ **Quick development restarts**
- 🔄 **Regular development workflow**
- 🚀 **Fast iteration**
- 📝 **Testing changes**

## Manual Reset Steps

If you prefer to reset manually:

```bash
# 1. Kill processes
pkill -f uvicorn
pkill -f "python.*main"

# 2. Clean cache
rm -rf __pycache__

# 3. Wait for port
sleep 2

# 4. Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill specific process
kill -9 <PID>
```

### Database Issues
```bash
# Remove database file
rm webhound.db

# Run full reset
./reset_backend.sh
```

### Virtual Environment Issues
```bash
# Reactivate virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Permission Issues
```bash
# Make scripts executable
chmod +x reset_backend.sh
chmod +x quick_reset.sh
```

## Script Safety Features

### `reset_backend.sh` Safety:
- ✅ **Confirmation prompts** for destructive actions
- ✅ **Error checking** at each step
- ✅ **Graceful failure** handling
- ✅ **Process verification** before killing
- ✅ **Port availability** checking

### `quick_reset.sh` Safety:
- ✅ **Safe process killing** (ignores errors)
- ✅ **Non-destructive** operations only
- ✅ **Fast execution** without prompts

## Integration with Development Workflow

### Recommended Workflow:
1. **Development**: Use `quick_reset.sh` for regular restarts
2. **Issues**: Use `reset_backend.sh` for troubleshooting
3. **Deployment**: Use `reset_backend.sh` for clean deployment

### Git Integration:
```bash
# After pulling changes
./reset_backend.sh

# During development
./quick_reset.sh
```

## Environment Variables

The scripts respect these environment variables:
- `VIRTUAL_ENV`: Virtual environment path
- `PYTHONPATH`: Python module search path
- `PORT`: Server port (defaults to 8000)

## Logging

### `reset_backend.sh` Logging:
- 📝 **Detailed step-by-step output**
- 🎨 **Colored status messages**
- ⚠️ **Warning and error highlighting**
- ✅ **Success confirmation**

### `quick_reset.sh` Logging:
- 📝 **Minimal essential output**
- ⚡ **Fast execution feedback**

## Performance

### `reset_backend.sh`:
- ⏱️ **~10-30 seconds** (with checks)
- 🔍 **Comprehensive validation**
- 🛡️ **Safe and thorough**

### `quick_reset.sh`:
- ⏱️ **~3-5 seconds** (minimal checks)
- ⚡ **Fast execution**
- 🚀 **Quick restart**

## Best Practices

1. **Always use scripts** instead of manual commands
2. **Use quick_reset.sh** for regular development
3. **Use reset_backend.sh** when troubleshooting
4. **Keep scripts executable** with `chmod +x`
5. **Run from backend directory** for proper paths
6. **Check output** for any warnings or errors 