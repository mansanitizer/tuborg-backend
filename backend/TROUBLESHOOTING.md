# Backend Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

### **Issue 1: "No module named 'pandas'"**

**Symptoms:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Root Cause:** Virtual environment not properly activated in subprocess

**Solutions:**

#### **Solution A: Use the new start_server.sh script**
```bash
cd backend
./start_server.sh
```

#### **Solution B: Manual activation**
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Solution C: Direct virtual environment python**
```bash
cd backend
./venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Issue 2: "Address already in use"**

**Symptoms:**
```
ERROR: [Errno 48] Address already in use
```

**Solutions:**

#### **Solution A: Kill existing processes**
```bash
pkill -f uvicorn
pkill -f "python.*main"
sleep 2
```

#### **Solution B: Use reset script**
```bash
./reset_backend.sh
```

#### **Solution C: Check what's using the port**
```bash
lsof -i :8000
kill -9 <PID>
```

### **Issue 3: Script not found**

**Symptoms:**
```
zsh: no such file or directory: ./quick_reset.sh
```

**Solutions:**

#### **Solution A: Run from correct directory**
```bash
cd backend
./quick_reset.sh
```

#### **Solution B: Use bash explicitly**
```bash
bash quick_reset.sh
```

#### **Solution C: Check file permissions**
```bash
ls -la *.sh
chmod +x *.sh
```

### **Issue 4: Virtual environment not activated**

**Symptoms:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solutions:**

#### **Solution A: Check if venv exists**
```bash
ls -la venv/
```

#### **Solution B: Recreate virtual environment**
```bash
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **Solution C: Check activation**
```bash
echo $VIRTUAL_ENV
which python
```

## 🔧 **Quick Fix Commands**

### **For Immediate Server Start:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **For Complete Reset:**
```bash
cd backend
pkill -f uvicorn
pkill -f "python.*main"
rm -rf __pycache__
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **For Dependency Issues:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pip check
```

## 🎯 **Recommended Workflow**

### **Daily Development:**
1. **Use the reliable script:**
   ```bash
   cd backend
   ./start_server.sh
   ```

2. **Or manual start:**
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### **When Issues Occur:**
1. **Kill processes:**
   ```bash
   pkill -f uvicorn
   ```

2. **Check virtual environment:**
   ```bash
   echo $VIRTUAL_ENV
   source venv/bin/activate
   ```

3. **Test imports:**
   ```bash
   python -c "import pandas as pd; print('OK')"
   ```

4. **Start server:**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🚀 **Reliable Scripts**

### **start_server.sh** (Recommended)
- ✅ Explicit virtual environment usage
- ✅ Process cleanup
- ✅ Import testing
- ✅ Clear error messages

### **quick_reset.sh** (Fast)
- ⚡ Quick process cleanup
- ⚡ Cache cleanup
- ⚡ Fast startup

### **reset_backend.sh** (Complete)
- 🔧 Full environment reset
- 🔧 Dependency checking
- 🔧 Database testing
- 🔧 Comprehensive validation

## 📋 **Checklist for Issues**

- [ ] Are you in the `backend` directory?
- [ ] Is the virtual environment activated?
- [ ] Are all processes killed?
- [ ] Are all dependencies installed?
- [ ] Is port 8000 free?
- [ ] Are file permissions correct?

## 🆘 **Emergency Commands**

### **Kill Everything and Start Fresh:**
```bash
cd backend
pkill -f uvicorn
pkill -f python
sleep 3
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Nuclear Option (Recreate Everything):**
```bash
cd backend
pkill -f uvicorn
pkill -f python
rm -rf venv
rm -rf __pycache__
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
``` 