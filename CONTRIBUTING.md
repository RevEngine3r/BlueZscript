# Contributing to BlueZscript

🎉 **Thank you for considering contributing to BlueZscript!** 🎉

We welcome contributions from everyone. This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment, trolling, or insulting/derogatory comments
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by opening an issue or contacting the project maintainers.

---

## Getting Started

### Prerequisites

- **Git** for version control
- **Python 3.9+** for backend development
- **Kotlin/Android Studio** for mobile development
- **Raspberry Pi** (optional, for hardware testing)
- **Android device** (optional, for app testing)

### Fork and Clone

```bash
# Fork repository on GitHub
# Then clone your fork:
git clone https://github.com/YOUR_USERNAME/BlueZscript.git
cd BlueZscript

# Add upstream remote
git remote add upstream https://github.com/RevEngine3r/BlueZscript.git
```

### Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Try latest version to see if issue is fixed
- Collect debug information (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md))

**When submitting:**
1. Use clear, descriptive title
2. Describe exact steps to reproduce
3. Provide expected vs actual behavior
4. Include system info (OS, Python version, etc.)
5. Add logs, screenshots if relevant

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Logs**
If applicable, add logs or screenshots.

**Environment:**
- OS: [e.g., Raspberry Pi OS Bullseye]
- Python: [e.g., 3.9.2]
- BlueZscript version: [e.g., 1.0.0]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

**Before suggesting:**
- Check if suggestion already exists
- Ensure it aligns with project goals

**Enhancement Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Mockups, examples, or other relevant information.
```

### Contributing Code

**Good first issues:**
- Look for issues labeled `good first issue`
- Documentation improvements
- Test coverage improvements
- Bug fixes

**Areas needing contribution:**
- Android app features
- Additional action script examples
- Web UI improvements
- Multi-language support
- Performance optimizations

---

## Development Setup

### Backend (Raspberry Pi / Python)

```bash
cd BlueZscript

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r raspberry-pi/requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/ -v
```

### Frontend (Android / Kotlin)

```bash
cd android-app

# Open in Android Studio
# Or build from command line:
./gradlew build
./gradlew test
```

### Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install

# Runs automatically on git commit
# Or run manually:
pre-commit run --all-files
```

---

## Coding Standards

### Python Code Style

**Follow PEP 8** with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

**Format with Black:**
```bash
black raspberry-pi/ tests/
```

**Lint with flake8:**
```bash
flake8 raspberry-pi/ tests/
```

**Type checking with mypy:**
```bash
mypy raspberry-pi/
```

**Example:**
```python
from typing import Optional

class DeviceManager:
    """Manages paired devices."""
    
    def __init__(self, db_path: str) -> None:
        """Initialize device manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def get_device(self, device_id: str) -> Optional[dict]:
        """Retrieve device by ID.
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            Device dict or None if not found
        """
        # Implementation
        pass
```

### Kotlin Code Style

**Follow Kotlin Coding Conventions:**

- **Indentation**: 4 spaces
- **Line length**: 120 characters
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`

**Format with ktlint:**
```bash
./gradlew ktlintFormat
```

**Example:**
```kotlin
class DeviceRepository(
    private val deviceDao: DeviceDao,
    private val totpManager: TotpManager
) {
    /**
     * Fetches all paired devices from local database.
     */
    suspend fun getAllDevices(): List<Device> {
        return deviceDao.getAllDevices()
    }
    
    /**
     * Generates TOTP for given device.
     */
    fun generateTotp(device: Device): String {
        return totpManager.generateTotp(device.secret)
    }
}
```

### Documentation

**Python docstrings (Google style):**
```python
def validate_totp(secret: str, totp: str, window: int = 1) -> bool:
    """Validate TOTP code against secret.
    
    Args:
        secret: Base32-encoded secret key
        totp: 6-digit TOTP code to validate
        window: Time window tolerance (default: 1)
        
    Returns:
        True if TOTP is valid, False otherwise
        
    Raises:
        ValueError: If secret is invalid format
    """
    pass
```

**Kotlin KDoc:**
```kotlin
/**
 * Validates TOTP code against device secret.
 *
 * @param device Device with secret key
 * @param totp 6-digit TOTP code
 * @return true if valid, false otherwise
 */
fun validateTotp(device: Device, totp: String): Boolean {
    // Implementation
}
```

---

## Commit Messages

### Format

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `build`: Build system or dependencies
- `ci`: CI configuration
- `chore`: Maintenance tasks

### Examples

```bash
# Good commits
feat(android): add dark mode support
fix(ble): resolve connection timeout issue
docs(readme): update installation instructions
test(crypto): add TOTP edge case tests

# With body
feat(api): add device deletion endpoint

Adds DELETE /api/devices/<id> endpoint to remove
paired devices from database. Includes authentication
check and cascade deletion of associated data.

Closes #42

# Breaking change
feat(auth)!: require TOTP for all operations

BREAKING CHANGE: All API endpoints now require TOTP
authentication. Update clients to include totp field.
```

---

## Pull Request Process

### Before Submitting

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ./gradlew test  # For Android
   ```

4. **Format code:**
   ```bash
   black raspberry-pi/ tests/
   ./gradlew ktlintFormat
   ```

5. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat(scope): add feature"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/my-awesome-feature
   ```

### Submitting PR

1. **Open Pull Request** on GitHub
2. **Fill out PR template:**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] Added tests for new functionality
- [ ] Tested on real hardware (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated

## Screenshots (if applicable)

## Related Issues
Closes #issue_number
```

3. **Wait for review**
   - Maintainers will review your PR
   - Address any requested changes
   - CI checks must pass

4. **PR approved and merged!**

### PR Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- No breaking changes (unless justified)
- Performance impact
- Security considerations

---

## Testing Requirements

### Backend Tests

**Required for new features:**
- Unit tests for all new functions
- Integration tests for API endpoints
- Edge case coverage

**Run tests:**
```bash
pytest tests/ -v --cov=raspberry-pi
```

**Minimum coverage:** 80%

### Android Tests

**Required:**
- Unit tests for ViewModels
- Unit tests for Use Cases
- UI tests for critical flows

**Run tests:**
```bash
./gradlew test
./gradlew connectedAndroidTest
```

### Writing Tests

**Example (Python):**
```python
import pytest
from raspberry_pi.crypto_utils import CryptoUtils

def test_totp_generation():
    """Test TOTP generation produces 6-digit code."""
    crypto = CryptoUtils()
    secret = crypto.generate_secret()
    totp = crypto.generate_totp(secret)
    
    assert len(totp) == 6
    assert totp.isdigit()

def test_totp_validation():
    """Test TOTP validation with correct code."""
    crypto = CryptoUtils()
    secret = crypto.generate_secret()
    totp = crypto.generate_totp(secret)
    
    assert crypto.validate_totp(secret, totp) is True
```

**Example (Kotlin):**
```kotlin
@Test
fun `generateTotp produces 6 digit code`() {
    val totpManager = TotpManager()
    val secret = "JBSWY3DPEHPK3PXP"
    
    val totp = totpManager.generateTotp(secret)
    
    assertEquals(6, totp.length)
    assertTrue(totp.all { it.isDigit() })
}
```

---

## Documentation

### Update Documentation

**When adding features:**
- Update README.md with new functionality
- Add examples to relevant guides
- Update API documentation
- Add inline code comments for complex logic

**Documentation files:**
- `README.md` - Project overview
- `INSTALL.md` - Installation guide
- `TESTING.md` - Testing procedures
- `TROUBLESHOOTING.md` - Common issues
- `PROJECT_MAP.md` - Code structure

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep formatting consistent
- Test all command examples

---

## Release Process

**For maintainers:**

1. Update version in:
   - `android-app/app/build.gradle.kts`
   - `raspberry-pi/setup.py` (if exists)
   - `PROGRESS.md`

2. Update CHANGELOG.md

3. Create release branch:
   ```bash
   git checkout -b release/v1.1.0
   ```

4. Tag release:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

5. Create GitHub Release with:
   - Release notes
   - APK file
   - Installation instructions

---

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/RevEngine3r/BlueZscript/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
- **Security issues**: Email maintainer privately

---

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

**Thank you for contributing to BlueZscript!** 🚀