# Contributing to Country State City PyPI

Thank you for your interest in contributing! This document provides guidelines for contributing to the countrystatecity-pypi project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/countrystatecity-pypi.git
   cd countrystatecity-pypi
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/dr5hn/countrystatecity-pypi.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Install Development Dependencies

```bash
cd python/packages/countries
pip install -e ".[dev]"
```

This will install:
- pydantic (runtime dependency)
- pytest, pytest-cov (testing)
- mypy (type checking)
- black, isort (code formatting)
- ruff (linting)

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-new-function`
- `fix/bug-description`
- `docs/update-readme`

### 2. Make Your Changes

- Write clear, concise code
- Add tests for new functionality
- Update documentation as needed
- Follow the [Style Guide](#style-guide)

### 3. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

## Testing

### Run All Tests

```bash
cd python/packages/countries
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=countrystatecity_countries --cov-report=html
```

Coverage reports will be in `htmlcov/index.html`.

### Run Specific Tests

```bash
# Test a specific file
pytest tests/test_countries.py

# Test a specific function
pytest tests/test_countries.py::test_get_countries
```

### Type Checking

```bash
mypy countrystatecity_countries/ --strict
```

All code must pass strict type checking.

### Linting

```bash
ruff check countrystatecity_countries/ tests/
```

### Code Formatting

```bash
# Check formatting
black --check countrystatecity_countries/ tests/
isort --check countrystatecity_countries/ tests/

# Apply formatting
black countrystatecity_countries/ tests/
isort countrystatecity_countries/ tests/
```

## Submitting Changes

### 1. Ensure Quality

Before submitting, verify:

- ✅ All tests pass
- ✅ Code is properly formatted (black, isort)
- ✅ No linting errors (ruff)
- ✅ Type checking passes (mypy)
- ✅ Coverage is maintained or improved

Run all checks:

```bash
pytest --cov=countrystatecity_countries
mypy countrystatecity_countries/ --strict
ruff check countrystatecity_countries/ tests/
black --check countrystatecity_countries/ tests/
isort --check countrystatecity_countries/ tests/
```

### 2. Commit Your Changes

Write clear commit messages:

```bash
git commit -m "feat: add support for filtering countries by currency"
```

Use conventional commit prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

### 3. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 4. Create a Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request"
3. Select your branch
4. Fill in the PR template with:
   - Description of changes
   - Related issue(s)
   - Testing performed
   - Screenshots (if applicable)

## Style Guide

### Python Code Style

We follow PEP 8 with these tools:

- **black** - Code formatting (line length: 88)
- **isort** - Import sorting
- **ruff** - Fast linting

### Type Hints

All functions must have type hints:

```python
def get_country_by_code(country_code: str) -> Optional[Country]:
    """Get country by ISO2 or ISO3 code."""
    pass
```

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Include examples where helpful

```python
def search_countries(query: str) -> List[Country]:
    """Search countries by name (case-insensitive).
    
    Args:
        query: Search query.
    
    Returns:
        List of countries matching the query.
    
    Example:
        >>> results = search_countries("united")
        >>> len(results) > 0
        True
    """
    pass
```

### Testing

- Write tests for all new functions
- Aim for >80% code coverage
- Test edge cases and error conditions
- Use descriptive test names

```python
def test_get_country_by_code_lowercase():
    """Test getting country by lowercase code."""
    usa = get_country_by_code("us")
    assert usa is not None
    assert usa.iso2 == "US"
```

## Questions?

If you have questions, please:

1. Check the [documentation](./python/packages/countries/README.md)
2. Search [existing issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
3. Open a new [discussion](https://github.com/dr5hn/countrystatecity-pypi/discussions)

Thank you for contributing! 🎉
