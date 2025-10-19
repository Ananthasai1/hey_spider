# ============================================
# Makefile - CHANGE #1: Populate Empty Makefile
# Priority: 🔴 CRITICAL
# ============================================

.PHONY: help install test run clean calibrate setup check health logs dev

help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║     🕷️  HEY SPIDER ROBOT - Makefile Commands          ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup      - Run interactive setup wizard"
	@echo "  make install    - Install all dependencies"
	@echo "  make check      - Check system requirements"
	@echo ""
	@echo "🚀 Running:"
	@echo "  make run        - Start the robot"
	@echo "  make dev        - Run in development mode"
	@echo ""
	@echo "🧪 Testing & Calibration:"
	@echo "  make test       - Run all tests"
	@echo "  make calibrate  - Calibrate sensors"
	@echo "  make test-camera - Test camera"
	@echo "  make test-servos - Test servo motors"
	@echo ""
	@echo "🏥 Monitoring:"
	@echo "  make health     - Check robot health"
	@echo "  make logs       - View live logs"
	@echo "  make stats      - Show statistics"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean      - Clean temporary files"
	@echo "  make clean-all  - Clean everything"
	@echo ""

# ============================================
# Setup Commands
# ============================================

setup:
	@echo "🔧 Running setup wizard..."
	@python3 scripts/setup_wizard.py

install:
	@echo "📦 Installing dependencies..."
	@bash install.sh

check:
	@echo "🔍 Checking system requirements..."
	@python3 scripts/check_requirements.py

# ============================================
# Running Commands
# ============================================

run:
	@echo "🚀 Starting Hey Spider Robot..."
	@python3 main.py

dev:
	@echo "🔧 Starting in development mode..."
	@export DEBUG_MODE=true && python3 main.py

# ============================================
# Testing Commands
# ============================================

test:
	@echo "🧪 Running all tests..."
	@pytest tests/ -v --tb=short

test-unit:
	@echo "🧪 Running unit tests..."
	@pytest tests/ -v -m unit

test-integration:
	@echo "🧪 Running integration tests..."
	@pytest tests/ -v -m integration

calibrate:
	@echo "⚙️  Calibrating sensors..."
	@python3 scripts/calibrate_sensors.py -a

test-camera:
	@echo "📹 Testing camera..."
	@python3 scripts/test_camera.py -a

test-servos:
	@echo "🤖 Testing servos..."
	@python3 scripts/test_servos.py -c

# ============================================
# Monitoring Commands
# ============================================

health:
	@echo "🏥 Checking robot health..."
	@curl -s http://localhost:5000/api/health/detailed | python3 -m json.tool || echo "❌ Robot not running"

health-simple:
	@echo "🏥 Simple health check..."
	@curl -s http://localhost:5000/health | python3 -m json.tool || echo "❌ Robot not running"

logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	@tail -f logs/spider.log

logs-errors:
	@echo "📋 Viewing error logs..."
	@grep -i error logs/spider.log | tail -20

stats:
	@echo "📊 Robot Statistics:"
	@echo ""
	@echo "Files:"
	@find . -name "*.py" | wc -l | xargs echo "  Python files:"
	@find images/raw -type f 2>/dev/null | wc -l | xargs echo "  Photos captured:"
	@find images/detections -type f 2>/dev/null | wc -l | xargs echo "  Detection images:"
	@echo ""
	@echo "Logs:"
	@wc -l logs/spider.log 2>/dev/null | xargs echo "  Log lines:" || echo "  No logs yet"

# ============================================
# Maintenance Commands
# ============================================

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf build/
	@rm -rf dist/
	@echo "✅ Cleanup complete"

clean-all: clean
	@echo "🧹 Deep cleaning..."
	@rm -rf venv/
	@rm -rf logs/*.log
	@rm -rf images/raw/*
	@rm -rf images/detections/*
	@rm -rf data/*.json
	@echo "✅ Deep cleanup complete"

# ============================================
# Development Helpers
# ============================================

format:
	@echo "🎨 Formatting code..."
	@black src/ tests/ scripts/ --line-length 100

lint:
	@echo "🔍 Linting code..."
	@flake8 src/ --max-line-length=100

docker-build:
	@echo "🐋 Building Docker image..."
	@docker build -t hey-spider-robot .

docker-run:
	@echo "🐋 Running in Docker..."
	@docker-compose up

# ============================================
# Quick Start
# ============================================

quickstart: install check calibrate
	@echo "✅ Quick start complete!"
	@echo "🚀 Run: make run"