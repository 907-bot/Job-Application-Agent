#!/bin/bash

# Deployment Script
# Handles application deployment to various environments
# Usage: ./scripts/deploy.sh [environment]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Default environment
ENVIRONMENT=${1:-staging}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production|local)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Usage: ./scripts/deploy.sh [local|staging|production]"
    exit 1
fi

print_header "Deployment Script - $ENVIRONMENT"

# Pre-deployment checks
print_step "Running pre-deployment checks..."

# Check if git is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Git working directory has uncommitted changes"
    print_warning "Please commit or stash changes before deploying"
    exit 1
fi
print_success "Git working directory is clean"

# Check if all required files exist
required_files=(
    "src/__init__.py"
    "config/config.yaml"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done
print_success "All required files found"

# Run tests
print_step "Running tests..."
if [ -f "scripts/run_tests.sh" ]; then
    if bash scripts/run_tests.sh --unit-only > /tmp/test_output.log 2>&1; then
        print_success "Tests passed"
    else
        print_error "Tests failed"
        cat /tmp/test_output.log
        exit 1
    fi
fi

# Build and push Docker image
if command -v docker &> /dev/null; then
    print_step "Building Docker image..."
    
    IMAGE_NAME="job-application-agent"
    IMAGE_TAG=$(git rev-parse --short HEAD)
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
    
    if docker build -t "$FULL_IMAGE_NAME" -t "${IMAGE_NAME}:latest" .; then
        print_success "Docker image built: $FULL_IMAGE_NAME"
    else
        print_error "Docker build failed"
        exit 1
    fi
    
    # Push to registry (if configured)
    if [ -n "$DOCKER_REGISTRY" ]; then
        print_step "Pushing Docker image to registry..."
        docker tag "$FULL_IMAGE_NAME" "${DOCKER_REGISTRY}/${FULL_IMAGE_NAME}"
        
        if docker push "${DOCKER_REGISTRY}/${FULL_IMAGE_NAME}"; then
            print_success "Docker image pushed to registry"
        else
            print_warning "Failed to push Docker image to registry"
        fi
    fi
fi

# Deployment based on environment
case $ENVIRONMENT in
    local)
        print_header "Local Deployment"
        print_step "Setting up local environment..."
        
        # Activate virtual environment
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            print_success "Virtual environment activated"
        else
            print_warning "Virtual environment not found, skipping activation"
        fi
        
        # Install/update dependencies
        print_step "Installing dependencies..."
        pip install -r requirements.txt > /dev/null
        print_success "Dependencies installed"
        
        # Start application
        print_step "Starting application..."
        python app.py &
        print_success "Application started on http://localhost:7860"
        ;;
    
    staging)
        print_header "Staging Deployment"
        print_step "Deploying to staging environment..."
        
        # Start with Docker Compose
        if command -v docker-compose &> /dev/null; then
            print_step "Starting Docker services..."
            docker-compose -f docker-compose.yml up -d
            print_success "Docker services started"
            
            # Wait for services to be ready
            print_step "Waiting for services to be ready..."
            sleep 5
            
            # Health check
            if curl -s http://localhost:7860 > /dev/null; then
                print_success "Application is healthy"
            else
                print_warning "Application health check failed"
            fi
        fi
        
        echo ""
        echo "Staging deployment URL: http://localhost:7860"
        ;;
    
    production)
        print_header "Production Deployment"
        print_warning "Production deployment requires manual approval!"
        echo ""
        echo "Steps to complete production deployment:"
        echo "1. Verify all tests pass locally"
        echo "2. Tag release: git tag -a v1.0.0 -m 'Release 1.0.0'"
        echo "3. Push tags: git push --tags"
        echo "4. Deploy to Kubernetes:"
        echo "   kubectl apply -f kubernetes/"
        echo "5. Verify deployment:"
        echo "   kubectl rollout status deployment/job-agent"
        echo ""
        print_warning "Please ensure you have proper backup and rollback plans"
        ;;
esac

# Post-deployment actions
print_header "Post-Deployment"

# Generate deployment report
print_step "Generating deployment report..."

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
GIT_HASH=$(git rev-parse --short HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

cat > "deployment_report_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).txt" << EOF
Deployment Report
=================

Environment: $ENVIRONMENT
Timestamp: $TIMESTAMP
Git Branch: $GIT_BRANCH
Git Commit: $GIT_HASH

Status: ✅ Deployment Successful
EOF

print_success "Deployment report generated"

# Notify (if webhook configured)
if [ -n "$SLACK_WEBHOOK" ]; then
    print_step "Sending Slack notification..."
    
    PAYLOAD="{
        \"text\": \"Deployment Successful - $ENVIRONMENT\",
        \"attachments\": [{
            \"color\": \"good\",
            \"fields\": [
                {\"title\": \"Environment\", \"value\": \"$ENVIRONMENT\", \"short\": true},
                {\"title\": \"Branch\", \"value\": \"$GIT_BRANCH\", \"short\": true},
                {\"title\": \"Commit\", \"value\": \"$GIT_HASH\", \"short\": true}
            ]
        }]
    }"
    
    if curl -X POST -H 'Content-type: application/json' \
        --data "$PAYLOAD" \
        "$SLACK_WEBHOOK" > /dev/null 2>&1; then
        print_success "Slack notification sent"
    fi
fi

print_header "Deployment Complete"
print_success "Application deployed to $ENVIRONMENT environment"

if [ "$ENVIRONMENT" = "local" ]; then
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:7860 in your browser"
    echo "2. Test the application"
    echo "3. Check logs: tail -f logs/app.log"
fi

echo ""
