# Contributing to OpenFeedback

Thank you for your interest in contributing to OpenFeedback! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.x
- Git
- pip (Python package manager)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openfeedback.git
   cd openfeedback
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   ```bash
   python migrate_db.py
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Test your changes**:
   ```bash
   python -m pytest tests/
   ```

4. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add brief description of changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** against the main repository

## Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and reasonably sized
- Comment complex logic clearly

### Python Code Example
```python
def calculate_feedback_score(feedback_items):
    """
    Calculate the average score from feedback items.
    
    Args:
        feedback_items: List of feedback dictionaries with 'score' keys
        
    Returns:
        float: Average score or 0 if no items provided
    """
    if not feedback_items:
        return 0
    return sum(item['score'] for item in feedback_items) / len(feedback_items)
```

### JavaScript Code
- Use consistent indentation (2 or 4 spaces)
- Use meaningful variable names
- Avoid global variables when possible
- Add comments for complex logic

## Testing

- Write tests for new features and bugfixes
- Ensure all tests pass before submitting a PR:
  ```bash
  python -m pytest tests/ -v
  ```
- Aim for reasonable code coverage on new functionality

## Commit Message Guidelines

Use clear and descriptive commit messages:

- **Good**: `Add user authentication endpoint with JWT tokens`
- **Good**: `Fix validation error message for empty feedback`
- **Avoid**: `update`, `fix stuff`, `changes`

Format: `<type>: <brief description>`

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code refactoring without feature changes
- `test:` - Adding or updating tests
- `chore:` - Build, dependency, or CI changes

## Pull Request Process

1. **Keep PRs focused** - one feature or bugfix per PR
2. **Update documentation** if your changes affect user-facing features
3. **Add tests** for new functionality
4. **Provide a clear description** of what your PR does
5. **Link any related issues** using `#issue_number`
6. **Be responsive** to feedback and review comments

## Project Structure

```
openfeedback/
├── app.py                 # Main Flask application
├── auth.py               # Authentication logic
├── migrate_db.py         # Database migration scripts
├── requirements.txt      # Python dependencies
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── logos/           # Logo files
├── templates/           # HTML templates
└── tests/               # Test files
```

## Questions or Need Help?

- Check existing issues and documentation
- Open an issue to discuss major changes before starting
- Be respectful and inclusive in all interactions

## License

By contributing to OpenFeedback, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing! 🎉
