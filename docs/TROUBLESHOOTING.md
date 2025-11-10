# Troubleshooting Guide

## Common Issues & Solutions

### **Installation Issues**

#### **Problem: Virtual environment creation fails**

```
Error: No module named 'venv'
```

**Solution:**
```bash
# Install Python venv
sudo apt-get install python3-venv  # Ubuntu/Debian
brew install python3                # macOS

# Try again
python3 -m venv venv
```

---

#### **Problem: Dependency installation fails**

```
ERROR: No matching distribution found for torch
```

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch correctly (select appropriate version)
pip install torch torchvision torchaudio -f https://download.pytorch.org/whl/torch_stable.html

# Or install from requirements in order
pip install -r requirements.txt --no-cache-dir
```

---

### **Runtime Issues**

#### **Problem: Application won't start**

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Ensure you're in project root
pwd  # Should be /path/to/job-application-agent

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Try again
python app.py
```

---

#### **Problem: Port already in use**

```
Address already in use
bind: Address already in use
```

**Solution:**
```bash
# Find process using port 7860
lsof -i :7860
# or
netstat -tlnp | grep 7860

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 8080
```

---

#### **Problem: GPU not detected**

```
torch.cuda.is_available() returns False
```

**Solution:**
```bash
# Check NVIDIA drivers
nvidia-smi

# Install CUDA toolkit
# Visit: https://developer.nvidia.com/cuda-downloads

# Verify installation
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
python app.py
```

---

### **Testing Issues**

#### **Problem: Tests fail with import errors**

```
ModuleNotFoundError: No module named 'tests'
```

**Solution:**
```bash
# Run tests from project root
cd /path/to/job-application-agent
bash scripts/run_tests.sh

# Or run pytest directly
python -m pytest tests/ -v
```

---

#### **Problem: Some tests pass, some fail**

**Solution:**
```bash
# Run with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/test_specific.py::TestClass::test_method -v

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x
```

---

#### **Problem: Coverage report shows missing coverage**

**Solution:**
```bash
# Generate detailed coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Add missing tests for uncovered code
```

---

### **Configuration Issues**

#### **Problem: Configuration file not found**

```
FileNotFoundError: config/config.yaml not found
```

**Solution:**
```bash
# Check file exists
ls -la config/config.yaml

# Create from template if missing
cp config/config.example.yaml config/config.yaml

# Edit configuration
nano config/config.yaml
```

---

#### **Problem: Invalid YAML syntax**

```
yaml.YAMLError: mapping values are not allowed here
```

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Common mistakes:
# - Missing spaces after colons
# - Inconsistent indentation (use 2 spaces)
# - Tabs instead of spaces
# - Unquoted strings with special characters
```

---

### **Database Issues**

#### **Problem: Cannot connect to database**

```
psycopg2.OperationalError: could not translate host name
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Test connection
psql -h localhost -U postgres -d job_agent

# Check environment variables
echo $DATABASE_URL
```

---

#### **Problem: Database schema errors**

**Solution:**
```bash
# Initialize schema
psql -d job_agent -f scripts/schema.sql

# Check schema
psql -d job_agent -c "\dt"

# Reset database (WARNING: deletes data)
dropdb job_agent
createdb job_agent
psql -d job_agent -f scripts/schema.sql
```

---

### **Docker Issues**

#### **Problem: Docker build fails**

**Solution:**
```bash
# Build with verbose output
docker build -t job-agent:latest . --verbose

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile

# Clear build cache
docker build --no-cache -t job-agent:latest .
```

---

#### **Problem: Container exits immediately**

**Solution:**
```bash
# Check logs
docker logs <container-id>

# Run with interactive shell
docker run -it job-agent:latest /bin/bash

# Check container setup
docker inspect <container-id>
```

---

#### **Problem: Volume mounting issues**

**Solution:**
```bash
# Verify mount
docker run -v $(pwd)/data:/app/data -it job-agent:latest ls -la /app/data

# Check permissions
chmod 755 data/
chmod 755 models/

# Fix ownership
sudo chown -R $USER:$USER data models
```

---

### **API Issues**

#### **Problem: API returns 500 error**

**Solution:**
```bash
# Check application logs
tail -f logs/app.log

# Enable debug mode
export DEBUG=true
python app.py

# Check request/response
curl -v http://localhost:7860/endpoint
```

---

#### **Problem: Slow API response**

**Solution:**
```bash
# Profile application
python -m cProfile -s cumulative app.py

# Check resource usage
top -p $(pgrep -f "python app.py")

# Increase workers
gunicorn --workers 8 app:app

# Enable caching
export CACHE_ENABLED=true
```

---

### **Model Issues**

#### **Problem: Model loading fails**

```
RuntimeError: Model file not found
```

**Solution:**
```bash
# Download model
python scripts/download_model.py

# Check model path
ls -lh models/

# Verify model integrity
python -c "import torch; torch.load('models/model_latest.pt')"
```

---

#### **Problem: Out of memory during inference**

**Solution:**
```bash
# Reduce batch size
batch_size = 8  # instead of 32

# Use CPU
export CUDA_VISIBLE_DEVICES=""

# Gradient checkpointing (if supported)
model.gradient_checkpointing_enable()
```

---

### **Logging Issues**

#### **Problem: Logs not being written**

**Solution:**
```bash
# Check permissions
ls -la logs/
chmod 755 logs/

# Check log configuration
cat config/logging.yaml

# Enable console output
export LOG_LEVEL=DEBUG
```

---

#### **Problem: Log file too large**

**Solution:**
```bash
# Rotate logs
ls -lh logs/app.log

# Archive old logs
gzip logs/app.log.1

# Remove old logs
find logs/ -name "*.gz" -mtime +30 -delete
```

---

## Performance Tuning

### **Slow Search**
```bash
# Add database indexes
psql job_agent < scripts/create_indexes.sql

# Increase cache TTL
CACHE_TTL=7200
```

### **Slow Model Inference**
```bash
# Use batch processing
batch_size = 32

# Enable GPU
USE_GPU=true

# Quantize model
python scripts/quantize_model.py
```

---

## Monitoring & Debugging

### **Check System Health**

```bash
# Monitor resources
python scripts/monitor.py

# Database health
pg_isready -h localhost -U postgres

# Redis health
redis-cli ping
```

### **Debug Mode**

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with Python debugger
python -m pdb app.py

# Use IDE debugger (VS Code, PyCharm)
```

---

## Getting Help

1. **Check existing issues**: GitHub Issues
2. **Search documentation**: docs/ folder
3. **Ask community**: Discussions tab
4. **Report bugs**: New Issue (include logs)
5. **Email support**: support@job-agent.com

---

## Emergency Procedures

### **Application Crash**

```bash
# 1. Check logs
tail -f logs/app.log

# 2. Restart application
bash scripts/setup_environment.sh
python app.py

# 3. Check dependencies
pip install -r requirements.txt --force-reinstall
```

### **Database Corruption**

```bash
# 1. Backup current data
pg_dump job_agent > backup_emergency.sql

# 2. Restore from backup
psql job_agent < backup_latest.sql

# 3. Verify integrity
psql -d job_agent -c "SELECT COUNT(*) FROM applications;"
```

### **API Unresponsive**

```bash
# 1. Restart API
docker restart job-agent

# 2. Check logs
docker logs job-agent

# 3. Clear cache
redis-cli FLUSHALL

# 4. Restart application
```

---

**Still having issues?** Open an issue on GitHub with:
- Error message
- Steps to reproduce
- System information
- Log file contents
