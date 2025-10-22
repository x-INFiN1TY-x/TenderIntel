# Contributing to TenderIntel 🤝

Thank you for your interest in contributing to TenderIntel! This document provides guidelines for contributing to our AI-powered competitive intelligence platform for government procurement.

## 🎯 **How to Contribute**

### **Types of Contributions We Welcome**
- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new functionality or improvements  
- 📝 **Documentation**: Improve our guides, examples, and API docs
- 🔧 **Code Contributions**: Implement features, fix bugs, optimize performance
- 🌐 **Portal Integration**: Add support for new government procurement portals
- 🔍 **Search Enhancement**: Improve keyword expansion and synonym dictionaries

## 🚀 **Getting Started**

### **Development Setup**
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork locally
git clone https://github.com/yourusername/tenderintel.git
cd TenderIntel

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install development dependencies
pip install -e ".[dev,tenderx]"

# 5. Set up pre-commit hooks
pre-commit install

# 6. Run tests to ensure everything works
pytest
```

### **Project Structure**
```
TenderIntel/
├── src/tenderintel/           # Main package source code
│   ├── core/                  # Core functionality (database, models)
│   ├── search/                # Search engine and synonym management
│   ├── scraper/               # Portal scraping with TenderX integration
│   ├── api/                   # FastAPI server and endpoints
│   └── ui/                    # Web interface components
├── tests/                     # Test suites (unit, integration, e2e)
├── docs/                      # Documentation (user, dev, API)
├── examples/                  # Usage examples and tutorials
├── scripts/                   # Utility scripts (setup, data, deploy)
├── config/                    # Configuration files (dev, prod)
└── docker/                    # Docker configurations
```

## 🛠️ **Development Workflow**

### **Making Changes**
1. **Create a Branch**: `git checkout -b feature/your-feature-name`
2. **Make Changes**: Implement your feature or fix
3. **Add Tests**: Ensure good test coverage for new functionality
4. **Run Quality Checks**: `make lint test`
5. **Commit Changes**: Use clear, descriptive commit messages
6. **Push and Create PR**: Submit a pull request for review

### **Code Style and Quality**
We use several tools to maintain code quality:

```bash
# Format code (required before commits)
black src/ tests/

# Sort imports  
isort src/ tests/

# Run linting (must pass)
flake8 src/ tests/

# Type checking (recommended)
mypy src/

# Run all quality checks
make lint
```

### **Testing Guidelines**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/tenderintel --cov-report=html

# Run specific test category
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests  
pytest tests/e2e/           # End-to-end tests

# Test specific functionality
pytest -k "search" -v       # Search-related tests
pytest -k "scraper" -v      # Scraping tests
```

## 📋 **Contribution Areas**

### **🔍 Search Engine Improvements**
- **Keyword Expansion**: Add new technical terms to the 215+ synonym dictionary
- **Domain Classification**: Improve categorization accuracy
- **Anti-Patterns**: Help prevent false positive matches
- **Performance**: Optimize BM25 ranking and FTS5 queries

**Example contribution:**
```python
# Add new synonyms to search/synonym_manager.py
"devops": ["development operations", "ci cd pipeline", "automated deployment"],
"k8s": ["kubernetes", "container orchestration", "k8s platform"]
```

### **🏭 Portal Integration**
- **New Portals**: Add support for state government procurement portals
- **Enhanced Scraping**: Improve CAPTCHA handling and data extraction
- **Document Processing**: Better PDF/document content analysis
- **Rate Limiting**: Optimize scraping performance and compliance

### **📊 Competitive Intelligence**
- **Firm Detection**: Improve competitor identification algorithms  
- **Market Analysis**: Add new analytical dimensions and metrics
- **Trend Analysis**: Implement time-series analysis and forecasting
- **Visualization**: Create new dashboard components and charts

### **🔧 Infrastructure & DevOps**
- **Docker**: Improve containerization and deployment
- **CI/CD**: Enhance GitHub Actions workflows
- **Monitoring**: Add more comprehensive health checks and metrics
- **Documentation**: Improve setup guides and API documentation

## 🚦 **Pull Request Process**

### **Before Submitting**
1. ✅ Ensure all tests pass: `pytest`
2. ✅ Code is properly formatted: `black src/ tests/`
3. ✅ Linting passes: `flake8 src/ tests/`
4. ✅ Documentation updated for new features
5. ✅ CHANGELOG.md updated (if applicable)

### **PR Description Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 🔧 Performance improvement  
- [ ] 📝 Documentation update
- [ ] 🧹 Code refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### **Review Process**
- All PRs require at least one review from maintainers
- Automated tests must pass (GitHub Actions)
- Code quality checks must pass (black, flake8, mypy)
- Documentation should be updated for user-facing changes

## 🔒 **Security & Compliance**

### **Responsible Disclosure**
- Report security issues privately to team@tenderintel.org
- Do not create public issues for security vulnerabilities
- We will acknowledge receipt within 24 hours

### **Data Privacy**
- Only use publicly available government procurement data
- Respect portal terms of service and rate limits
- Do not scrape or store sensitive or private information
- Implement appropriate data retention and deletion policies

### **Portal Compliance**
- Follow robots.txt and portal-specific scraping guidelines
- Implement respectful rate limiting and backoff strategies
- Use proper User-Agent strings identifying TenderIntel
- Handle CAPTCHAs and anti-bot measures appropriately

## 🎯 **Coding Guidelines**

### **Python Style**
- Follow PEP 8 with 88-character line limit (Black formatting)
- Use type hints for all function parameters and returns
- Write comprehensive docstrings using Google/NumPy style
- Prefer composition over inheritance for extensibility

### **API Design**
- RESTful endpoints with consistent naming conventions
- Comprehensive OpenAPI documentation with examples
- Proper HTTP status codes and error handling
- Input validation and sanitization for all endpoints

### **Database Design**
- Use migrations for schema changes
- Proper indexing for performance
- Data integrity constraints and validation
- Clear separation between FTS5 search and relational data

### **Testing Standards**
- Minimum 80% test coverage for new code
- Unit tests for individual components  
- Integration tests for API endpoints
- End-to-end tests for critical user flows

## 🏷️ **Issue Labels**

We use labels to categorize issues and PRs:

- `bug` - Something isn't working correctly
- `enhancement` - New feature or improvement
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `search-engine` - Search and synonym related
- `scraping` - Portal scraping and data collection
- `competitive-intel` - Analytics and intelligence features
- `api` - API server and endpoints
- `ui` - User interface and frontend
- `performance` - Performance optimization
- `security` - Security-related issues

## 📬 **Communication**

### **Getting Help**
- 💬 **Discussions**: Use GitHub Discussions for questions and ideas
- 🐛 **Issues**: Create issues for bugs and feature requests  
- 📧 **Email**: team@tenderintel.org for private communication
- 📚 **Documentation**: Check docs/ for detailed guides

### **Community Guidelines**
- Be respectful and inclusive in all interactions
- Provide constructive feedback and suggestions
- Help others learn and contribute effectively
- Follow our Code of Conduct (CODE_OF_CONDUCT.md)

## 🏆 **Recognition**

### **Contributors**
All contributors are recognized in:
- README.md acknowledgments section
- CONTRIBUTORS.md file with detailed contributions
- GitHub contributors graph and statistics
- Release notes for significant contributions

### **Maintainer Path**
Active contributors may be invited to become maintainers with:
- Commit access to the repository
- Ability to review and merge PRs
- Involvement in project direction decisions
- Recognition as core team members

## 📝 **License**

By contributing to TenderIntel, you agree that your contributions will be licensed under the MIT License. This ensures the project remains open and accessible to all users.

---

## 🎉 **Thank You!**

Your contributions help make government procurement analysis more accessible and effective for businesses and analysts worldwide. Every contribution, whether code, documentation, or feedback, makes TenderIntel better for everyone.

**Ready to contribute?** Check out our [good first issues](https://github.com/tenderintel/tenderintel/labels/good%20first%20issue) or join the discussion in [GitHub Discussions](https://github.com/tenderintel/tenderintel/discussions)!

---

**🚀 Happy Contributing!**
