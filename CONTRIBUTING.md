# Contributing to Moodle ELT Integration

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/integration-moodle_elt.git
   cd integration-moodle_elt
   ```

2. **Set up development environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ./setup.sh
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

### DAG Development

- Test DAGs locally before committing
- Use proper error handling
- Log important events
- Follow the existing pattern for consistency

### SQL Development

- Use `IF NOT EXISTS` for schema creation
- Add appropriate indexes
- Use `ON CONFLICT` for upserts
- Comment complex queries

### Testing

Before submitting:

1. **Validate Python syntax**
   ```bash
   python3 -m py_compile dags/*.py dags/utils/*.py
   ```

2. **Test DAG imports**
   ```bash
   docker-compose exec airflow-scheduler airflow dags list
   ```

3. **Test SQL scripts**
   ```bash
   docker-compose exec postgres psql -U airflow -d airflow -f /path/to/script.sql
   ```

## 🐛 Reporting Bugs

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Airflow version, Python version, etc.)
- Relevant logs

## 💡 Suggesting Features

- Check existing issues first
- Clearly describe the feature
- Explain the use case
- Consider implementation approach

## 📤 Submitting Changes

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Include testing steps

## 🔍 Code Review

All submissions require review. We'll:
- Check code quality
- Verify tests pass
- Review documentation
- Suggest improvements

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Questions?

Feel free to open an issue for any questions or concerns!
