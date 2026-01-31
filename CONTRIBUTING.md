# 🤝 Contributing to BlueZscript

First off, thank you for considering contributing to BlueZscript! It's people like you that make this project better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated promptly and fairly.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When creating a bug report, include:**

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior** and what actually happened
- **Screenshots** if applicable
- **Environment details**:
  - Raspberry Pi model and OS version
  - Python version
  - Android version (if app issue)
  - BlueZscript version
- **Logs**:
  ```bash
  sudo journalctl -u ble-listener-secure -n 100 > logs.txt
  ```

**Example Bug Report:**

```markdown
## Bug: BLE Listener Crashes on Invalid Message

**Description:**
The BLE listener service crashes when receiving malformed JSON messages.

**Steps to Reproduce:**
1. Start BLE listener
2. Send invalid JSON: `{"invalid": json}`
3. Service crashes

**Expected:**
Service should log error and continue running

**Environment:**
- Raspberry Pi 4 Model B
- Raspberry Pi OS Bullseye
- Python 3.9.2
- BlueZscript v1.0.0

**Logs:**
[Attach logs.txt]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When suggesting an enhancement, include:**

- **Clear title and description**
- **Use case** explaining why this would be useful
- **Proposed solution** or implementation ideas
- **Alternatives considered**
- **Mockups/diagrams** if applicable

**Example Enhancement:**

```markdown
## Enhancement: Support Multiple Actions per Device

**Use Case:**
Users want to trigger different actions (e.g., "lights on", "camera capture") from the same device.

**Proposed Solution:**
1. Add `action_type` field to BLE message
2. Map action types to different scripts in config
3. Update Android app UI with action selector

**Alternatives:**
- Use multiple paired devices (current workaround)
- Voice commands (future feature)

**Mockup:**
[Attach UI mockup]
```

### Contributing Code

We welcome code contributions! Here's how to get started.

---

## Development Setup

### Prerequisites

- **Raspberry Pi**: Pi 3/4 with BLE support
- **Python**: 3.9+
- **Git**: Latest version
- **Android Studio**: For Android development
- **Tools**: `pytest`, `black`, `flake8`

### Fork and Clone

```bash
# Fork repository on GitHub (click Fork button)

# Clone your fork
git clone https://github.com/YOUR_USERNAME/BlueZscript.git
cd BlueZscript

# Add upstream remote
git remote add upstream https://github.com/RevEngine3r/BlueZscript.git

# Verify remotes
git remote -v
```

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r raspberry-pi/requirements.txt

# Install development tools
pip install pytest pytest-cov black flake8 mypy

# Run tests to verify setup
pytest tests/ -v
```

### Android Setup

```bash
# Open in Android Studio
cd android-app
# File → Open → Select android-app directory

# Sync Gradle
# Build → Make Project

# Run on emulator or device
# Run → Run 'app'
```

### Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/amazing-feature

# Or for bug fixes:
git checkout -b fix/issue-123
```

---

## Coding Standards

### Python Style Guide

**We follow PEP 8 with some modifications:**

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Docstrings**: Google style

**Example:**

```python
class CryptoUtils:
    """Utility class for cryptographic operations.
    
    This class provides TOTP generation, validation, and
    secure key management functionality.
    """
    
    def generate_totp(self, secret: str, window: int = 0) -> str:
        """Generate TOTP code for given secret.
        
        Args:
            secret: Base32-encoded secret key
            window: Time window offset (default: 0)
            
        Returns:
            Six-digit TOTP code as string
            
        Raises:
            ValueError: If secret is invalid
        """
        if not secret:
            raise ValueError("Secret cannot be empty")
        
        # Implementation...
        return totp_code
```

### Format Code with Black

```bash
# Format all Python files
black raspberry-pi/*.py tests/*.py

# Check without modifying
black --check raspberry-pi/*.py
```

### Lint with Flake8

```bash
# Check code quality
flake8 raspberry-pi/ tests/

# Ignore specific warnings (if justified)
flake8 --extend-ignore=E203,W503 raspberry-pi/
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Dict, Optional

def validate_totp(
    secret: str, 
    code: str, 
    window: int = 1
) -> bool:
    """Validate TOTP code."""
    # Implementation...
    return True
```

### Kotlin Style Guide

**We follow official Kotlin style:**

- **Naming**: 
  - Classes: `PascalCase`
  - Functions/variables: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Indentation**: 4 spaces
- **Line length**: 100 characters

**Example:**

```kotlin
class TotpManager(private val context: Context) {
    companion object {
        private const val TAG = "TotpManager"
        private const val TOTP_PERIOD = 30
    }
    
    /**
     * Generate TOTP code for given secret.
     * 
     * @param secret Base32-encoded secret key
     * @return Six-digit TOTP code
     */
    fun generateTotp(secret: String): String {
        require(secret.isNotEmpty()) { "Secret cannot be empty" }
        
        // Implementation...
        return totpCode
    }
}
```

---

## Commit Guidelines

### Commit Message Format

We use **Conventional Commits** for clear, semantic commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring (no functionality change)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)

**Examples:**

```bash
# Good commits
git commit -m "feat(crypto): add HMAC verification support"
git commit -m "fix(ble): handle connection timeout gracefully"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(pairing): add tests for duplicate device names"

# With body and footer
git commit -m "feat(android): add dark mode support

Implements Material 3 dynamic theming with automatic
light/dark mode switching based on system settings.

Closes #42"
```

### Commit Best Practices

- **One logical change per commit**
- **Write in imperative mood**: "Add feature" not "Added feature"
- **Limit subject to 50 characters**
- **Wrap body at 72 characters**
- **Reference issues**: `Fixes #123`, `Closes #456`

---

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/amazing-feature
   git rebase main
   ```

2. **Run tests:**
   ```bash
   # Backend tests
   pytest tests/ -v
   
   # Android tests
   cd android-app
   ./gradlew test
   ```

3. **Format code:**
   ```bash
   black raspberry-pi/ tests/
   flake8 raspberry-pi/ tests/
   ```

4. **Update documentation** if needed

5. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/amazing-feature
   ```

### Creating Pull Request

1. **Go to GitHub** and create PR from your fork

2. **Fill PR template:**

   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Changes Made
   - Added X functionality
   - Fixed Y issue
   - Updated Z documentation
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests for changes
   - [ ] Manual testing completed
   
   ## Screenshots (if applicable)
   [Attach screenshots]
   
   ## Checklist
   - [ ] Code follows project style
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   
   ## Related Issues
   Closes #123
   ```

3. **Wait for review**

### Review Process

- **Maintainers will review** within 48 hours
- **Address feedback** by pushing new commits
- **Keep PR focused** - one feature/fix per PR
- **Be patient and respectful**

### Merging

- PRs require **at least one approval**
- **All CI checks must pass**
- **Conflicts must be resolved**
- Maintainers will **squash and merge**

---

## Testing

### Writing Tests

**Every new feature or bug fix should include tests.**

**Backend Test Example:**

```python
# tests/test_crypto_utils.py
import pytest
from raspberry-pi.crypto_utils import CryptoUtils

def test_totp_generation():
    """Test TOTP code generation."""
    crypto = CryptoUtils()
    secret = "JBSWY3DPEHPK3PXP"
    
    totp = crypto.generate_totp(secret)
    
    assert len(totp) == 6
    assert totp.isdigit()

def test_totp_validation():
    """Test TOTP validation with correct code."""
    crypto = CryptoUtils()
    secret = "JBSWY3DPEHPK3PXP"
    
    totp = crypto.generate_totp(secret)
    is_valid = crypto.validate_totp(secret, totp)
    
    assert is_valid is True

def test_invalid_totp():
    """Test TOTP validation with incorrect code."""
    crypto = CryptoUtils()
    secret = "JBSWY3DPEHPK3PXP"
    
    is_valid = crypto.validate_totp(secret, "000000")
    
    assert is_valid is False
```

**Run Tests:**

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_crypto_utils.py -v

# Run with coverage
pytest tests/ --cov=raspberry-pi --cov-report=html
```

---

## Documentation

### Updating Documentation

When adding features or fixing bugs, update relevant documentation:

- **README.md**: Overview and quick start
- **INSTALL.md**: Installation procedures
- **TESTING.md**: Testing instructions
- **TROUBLESHOOTING.md**: Known issues and solutions
- **Code comments**: Docstrings for classes/functions

### Documentation Style

- **Clear and concise** language
- **Step-by-step instructions** with code examples
- **Screenshots or diagrams** for complex concepts
- **Keep it updated** with code changes

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

### Getting Help

- **Check documentation first**: README, INSTALL, TROUBLESHOOTING
- **Search existing issues** before creating new ones
- **Be specific** in questions and provide context
- **Be patient** - maintainers are volunteers

### Recognition

All contributors will be:
- **Listed in CONTRIBUTORS.md**
- **Credited in release notes**
- **Mentioned in project updates**

---

## License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

---

## Questions?

Feel free to reach out:
- **GitHub Issues**: https://github.com/RevEngine3r/BlueZscript/issues
- **Discussions**: https://github.com/RevEngine3r/BlueZscript/discussions
- **Author**: [@RevEngine3r](https://github.com/RevEngine3r)

---

**Thank you for contributing to BlueZscript! 🚀**

*Together we make this project better for everyone.*