#!/bin/bash

# Run Tests Script
# Comprehensive testing runner with coverage and reporting
# Usage: ./scripts/run_tests.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Default values
RUN_UNIT_TESTS=true
RUN_INTEGRATION_TESTS=true
RUN_COVERAGE=true
RUN_LINTING=true
VERBOSE=false
HTML_REPORT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_INTEGRATION_TESTS=false
            RUN_COVERAGE=false
            RUN_LINTING=false
            shift
            ;;
        --coverage-only)
            RUN_UNIT_TESTS=false
            RUN_INTEGRATION_TESTS=false
            RUN_LINTING=false
            shift
            ;;
        --lint-only)
            RUN_UNIT_TESTS=false
            RUN_INTEGRATION_TESTS=false
            RUN_COVERAGE=false
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: ./scripts/run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --unit-only          Run only unit tests"
            echo "  --coverage-only      Run only coverage analysis"
            echo "  --lint-only          Run only linting"
            echo "  --html               Generate HTML coverage report"
            echo "  -v, --verbose        Verbose output"
            echo "  --help               Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

print_header "Job Application Agent - Test Suite"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Run: pip install pytest pytest-cov"
    exit 1
fi

TEST_FAILED=false

# Run linting
if [ "$RUN_LINTING" = true ]; then
    print_header "Linting Checks"
    
    # Black
    if command -v black &> /dev/null; then
        print_info "Running black code formatter check..."
        if black --check src tests 2>/dev/null; then
            print_success "Black check passed"
        else
            print_error "Black formatting issues found"
            print_info "Run: black src tests"
            TEST_FAILED=true
        fi
    fi
    
    # Flake8
    if command -v flake8 &> /dev/null; then
        print_info "Running flake8 linter..."
        if flake8 src tests --max-line-length=120 2>/dev/null; then
            print_success "Flake8 check passed"
        else
            print_error "Flake8 linting issues found"
            TEST_FAILED=true
        fi
    fi
    
    # MyPy
    if command -v mypy &> /dev/null; then
        print_info "Running mypy type checker..."
        if mypy src --ignore-missing-imports 2>/dev/null; then
            print_success "MyPy check passed"
        else
            print_warning "MyPy found type issues (non-blocking)"
        fi
    fi
fi

# Run unit and integration tests
if [ "$RUN_UNIT_TESTS" = true ] || [ "$RUN_INTEGRATION_TESTS" = true ]; then
    print_header "Running Tests"
    
    if [ "$RUN_COVERAGE" = true ]; then
        print_info "Running tests with coverage analysis..."
        
        if [ "$VERBOSE" = true ]; then
            pytest tests/ \
                --cov=src \
                --cov-report=term-missing \
                --cov-report=html \
                --cov-report=xml \
                -v \
                -x
        else
            pytest tests/ \
                --cov=src \
                --cov-report=term-missing \
                --cov-report=html \
                --cov-report=xml \
                -q
        fi
    else
        print_info "Running tests without coverage..."
        
        if [ "$VERBOSE" = true ]; then
            pytest tests/ -v -x
        else
            pytest tests/ -q
        fi
    fi
    
    if [ $? -ne 0 ]; then
        print_error "Tests failed"
        TEST_FAILED=true
    else
        print_success "All tests passed"
    fi
fi

# Print coverage report
if [ "$RUN_COVERAGE" = true ] && [ -f "htmlcov/index.html" ]; then
    print_header "Coverage Report"
    print_info "Coverage report generated: htmlcov/index.html"
    
    if [ "$HTML_REPORT" = true ] && command -v open &> /dev/null; then
        print_info "Opening coverage report in browser..."
        open htmlcov/index.html
    fi
fi

# Final summary
echo ""
if [ "$TEST_FAILED" = true ]; then
    print_header "Test Summary"
    print_error "Some tests failed or issues found"
    exit 1
else
    print_header "Test Summary"
    print_success "All tests passed successfully!"
    echo ""
    echo "Test Statistics:"
    if command -v pytest &> /dev/null; then
        pytest tests/ --co -q 2>/dev/null | tail -1 || echo "  Tests completed"
    fi
    exit 0
fi
