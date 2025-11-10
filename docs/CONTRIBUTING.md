# Contributing Guidelines

## Welcome!

Thank you for your interest in contributing to the Job Application Agent project. This document provides guidelines and instructions for contributing.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our Code of Conduct:

- Be respectful and inclusive
- Welcome people of all backgrounds
- Focus on constructive criticism
- Respect different opinions
- Report inappropriate behavior

## Getting Started

### **1. Fork the Repository**

```bash
# Click "Fork" on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/job-application-agent.git
cd job-application-agent
```

### **2. Create a Feature Branch**

```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Branch naming conventions:
# - feature/add-feature-name
# - fix/fix-description
# - docs/documentation-update
# - refactor/refactoring-description
```

### **3. Set Up Development Environment**

```bash
# Install dependencies
bash scripts/setup_environment.sh

# Activate environment
source venv/bin/activate

# Install development tools
pip install -r requirements-dev.txt
```

## Development Workflow

### **Code Style**

We use **Black** for formatting and **Flake8** for linting:

```bash
# Format code
black src tests

# Check linting
flake8 src tests

# Type checking
mypy src --ignore-missing-imports
```

### **Writing Code**

**Python Standards:**
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for classes and functions
- Keep functions small and focused
- DRY (Don't Repeat Yourself)

**Example:**
```python
def calculate_skill_match(
    resume_skills: List[str],
    job_skills: List[str]
) -> float:
    """
    Calculate skill match percentage between resume and job.
    
    Args:
        resume_skills: List of skills from resume
        job_skills: List of required job skills
    
    Returns:
        Match percentage (0-1)
    
    Raises:
        ValueError: If lists are empty
    """
    if not resume_skills or not job_skills:
        raise ValueError("Skill lists cannot be empty")
    
    matching = len(set(resume_skills) & set(job_skills))
    return matching / len(job_skills)
```

### **Commit Messages**

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "feat: add skill extraction from job descriptions"
git commit -m "fix: resolve memory leak in model inference"
git commit -m "docs: update API documentation"
git commit -m "test: add integration tests for classifier"

# Bad
git commit -m "update stuff"
git commit -m "fix bug"
git commit -m "WIP"
```

**Format:** `<type>: <subject>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Build/dependency changes

## Testing Requirements

### **Unit Tests**

Every new feature must have corresponding unit tests:

```python
# tests/test_your_feature.py
import pytest
from src.your_module import YourClass

class TestYourClass:
    @pytest.fixture
    def instance(self):
        return YourClass()
    
    def test_basic_functionality(self, instance):
        result = instance.method()
        assert result is not None
    
    def test_error_handling(self, instance):
        with pytest.raises(ValueError):
            instance.method(invalid_param)
```

### **Run Tests**

```bash
# Run all tests
bash scripts/run_tests.sh

# Run specific test file
pytest tests/test_your_feature.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### **Coverage Requirements**

- Minimum 80% code coverage
- All public methods must be tested
- All error paths must be tested

## Documentation

### **Docstring Format**

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
        TypeError: When param1 is not a string
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

### **Update Documentation**

When adding features, update relevant docs:
- `docs/API_DOCUMENTATION.md` (for API changes)
- `docs/ARCHITECTURE.md` (for structural changes)
- `README.md` (for user-facing changes)
- `CONTRIBUTING.md` (for contribution process changes)

## Pull Request Process

### **1. Before Submitting**

```bash
# Update main branch
git fetch origin
git rebase origin/main

# Run all checks locally
bash scripts/run_tests.sh
black src tests
flake8 src tests --max-line-length=120
mypy src --ignore-missing-imports
```

### **2. Create Pull Request**

**Title Format:**
```
[TYPE] Brief description of changes
```

Examples:
- `[FEATURE] Add skill extraction from job descriptions`
- `[FIX] Resolve memory leak in model inference`
- `[DOCS] Update API documentation`

**Description Template:**
```markdown
## Description
Brief description of changes made.

## Related Issue
Fixes #123

## Type of Change
- [ ] New feature (non-breaking change)
- [ ] Bug fix (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Testing Done
- Tested locally: [describe]
- Coverage: [%]
- New tests: [describe]

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commits are clean
- [ ] No new warnings generated
```

### **3. Code Review**

- Be open to feedback
- Respond to review comments
- Request changes if needed
- Update code based on feedback
- Re-request review when ready

### **4. Merge Approval**

Requirements:
- At least 2 approving reviews
- All CI checks passing
- No unresolved discussions
- Coverage maintained/improved

## Project Structure

```
job-application-agent/
├── src/              # Source code
├── tests/            # Test files
├── config/           # Configuration files
├── scripts/          # Automation scripts
├── docs/             # Documentation
├── .github/          # GitHub configs
└── README.md         # Project overview
```

## Adding New Features

### **1. Create Issue**

Describe the feature:
- Title: Clear, concise
- Description: What, why, how
- Labels: feature, enhancement
- Assignee: Yourself

### **2. Implement Feature**

```bash
# Create feature branch
git checkout -b feature/my-feature

# Implement changes
# Add tests
# Update documentation
# Commit changes
```

### **3. Submit Pull Request**

```bash
# Push to fork
git push origin feature/my-feature

# Create PR on GitHub
# Fill in template
# Link to related issue
```

## Bug Reports

### **Report Template**

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS]
- Python: [e.g., 3.9]
- Branch: [e.g., main]

## Error Message
Include full error traceback if applicable.

## Screenshots
Attach if relevant.
```

## Performance Considerations

- Profile code before optimizing
- Benchmark changes: `scripts/benchmark.sh`
- Use appropriate data structures
- Avoid unnecessary computations
- Cache expensive operations

## Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Follow OWASP guidelines
- Report security issues privately

## Release Process

1. Version bump (semver)
2. Update CHANGELOG
3. Create release tag
4. Update documentation
5. Announce release

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README
- GitHub insights

## Need Help?

- **Questions**: Open a Discussion
- **Bugs**: Create an Issue
- **Chat**: Join our Slack community
- **Email**: contribute@job-agent.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
