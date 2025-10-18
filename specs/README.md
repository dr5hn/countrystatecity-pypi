# Specifications Documentation

This directory contains comprehensive specifications for building Python PyPI packages for the countries-states-cities-database project, mirroring the existing npm package ecosystem.

---

## 📚 Documents Overview

### 1. [Python PyPI Monorepo Plan](./1-python-pypi-monorepo-plan.md)
**Complete specifications for the Python package ecosystem**

**Key Topics:**
- Executive summary and business context
- Repository architecture and directory structure
- Detailed package specifications (countries, timezones, currencies, etc.)
- Pydantic models and type definitions
- API design and function signatures
- Data loading strategies with LRU caching
- Development tooling (Poetry, pytest, mypy)
- CI/CD with GitHub Actions
- Testing requirements and strategies
- Documentation structure
- Implementation roadmap (4-6 weeks)

**When to Use:** Start here for complete understanding of the project scope and architecture.

---

### 2. [Python vs NPM Comparison](./2-python-vs-npm-comparison.md)
**Side-by-side comparison of npm and Python implementations**

**Key Topics:**
- Package naming conventions
- Installation and usage examples
- Type systems (TypeScript vs Pydantic)
- Data loading approaches
- Testing frameworks
- Build tools and toolchains
- CI/CD workflows
- Framework integration examples
- API style differences

**When to Use:** Reference this when making design decisions to ensure consistency with npm packages.

---

### 3. [Python Quick Start Guide](./3-python-quick-start-guide.md)
**Step-by-step implementation guide for the first package**

**Key Topics:**
- Phase 1: Setup (directory structure, Poetry)
- Phase 2: Core implementation (models, loaders, API)
- Phase 3: Testing (pytest, coverage)
- Phase 4: Data generation (MySQL to JSON)
- Phase 5: Package configuration (pyproject.toml)
- Phase 6: Build and test
- Phase 7: Publish to PyPI
- Complete code examples
- Pre-launch checklist
- Troubleshooting tips

**When to Use:** Follow this guide for hands-on implementation of the first package.

---

## 🎯 Quick Reference

### Package Names

| Type | NPM | Python |
|------|-----|--------|
| **Countries** | `@countrystatecity/countries` | `countrystatecity-countries` |
| **Timezones** | `@countrystatecity/timezones` | `countrystatecity-timezones` |
| **Currencies** | `@countrystatecity/currencies` | `countrystatecity-currencies` |
| **Languages** | `@countrystatecity/languages` | `countrystatecity-languages` |
| **Phone Codes** | `@countrystatecity/phone-codes` | `countrystatecity-phonecodes` |

### Installation

```bash
# NPM
npm install @countrystatecity/countries

# Python
pip install countrystatecity-countries
```

### Basic Usage

```python
# Python
from countrystatecity_countries import get_countries, get_country_by_code

countries = get_countries()
usa = get_country_by_code("US")
```

```typescript
// TypeScript
import { getCountries, getCountryByCode } from '@countrystatecity/countries';

const countries = await getCountries();
const usa = await getCountryByCode('US');
```

---

## 🏗️ Repository Structure (After Implementation)

```
countries-states-cities-database/
├── bin/                           # [Existing] PHP export tools
├── contributions/                 # [Existing] JSON source data
├── json/                          # [Existing] JSON exports
├── sql/                           # [Existing] SQL dumps
│
├── python/                        # [NEW] Python packages
│   ├── packages/
│   │   ├── countries/             # Priority 1
│   │   ├── timezones/             # Priority 2
│   │   ├── currencies/            # Priority 3
│   │   ├── languages/             # Priority 4
│   │   └── phone-codes/           # Priority 5
│   ├── shared/                    # Shared utilities
│   ├── scripts/                   # Build scripts
│   └── README.md
│
└── specs/                         # [THIS FOLDER] Specifications
    ├── README.md                  # This file
    ├── 1-python-pypi-monorepo-plan.md
    ├── 2-python-vs-npm-comparison.md
    └── 3-python-quick-start-guide.md
```

---

## 📋 Implementation Priority

### Phase 1: Foundation (Weeks 1-4)
**Package:** `countrystatecity-countries`
- Setup repository structure
- Implement core functionality
- Write comprehensive tests
- Generate data structure
- Publish to PyPI

### Phase 2: Expansion (Weeks 5-8)
**Packages:**
- `countrystatecity-timezones`
- `countrystatecity-currencies`

### Phase 3: Completion (Weeks 9-12)
**Packages:**
- `countrystatecity-languages`
- `countrystatecity-phonecodes`

### Phase 4: Framework Integration (Weeks 13-16)
**Packages:**
- `countrystatecity-flask`
- `countrystatecity-django`

---

## 🔑 Key Design Principles

### 1. **Consistency with NPM Packages**
- Same data structure
- Similar API design (adapted for Python conventions)
- Identical functionality

### 2. **Python Best Practices**
- Type hints everywhere (Pydantic models)
- PEP 8 compliant (black, isort)
- Comprehensive testing (pytest, 80%+ coverage)
- Modern packaging (Poetry, pyproject.toml)

### 3. **Performance & Efficiency**
- Lazy loading with LRU cache
- Minimal memory footprint
- Fast import times (<50ms)
- Split data files for granular loading

### 4. **Developer Experience**
- Clear API documentation
- Type safety with mypy
- Comprehensive examples
- Easy integration with frameworks

### 5. **Data Integrity**
- Single source of truth (MySQL database)
- Automated data generation
- Validation at build time
- Immutable models (Pydantic frozen)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Package Manager** | Poetry | Dependency management, publishing |
| **Type System** | Pydantic | Data validation, immutable models |
| **Testing** | pytest | Unit and integration tests |
| **Type Checking** | mypy | Static type checking |
| **Linting** | ruff | Fast Python linter |
| **Formatting** | black + isort | Code formatting |
| **CI/CD** | GitHub Actions | Automated testing and publishing |
| **Data Source** | MySQL | Primary database |
| **Data Format** | JSON | Lazy-loadable data files |

---

## 📊 Success Metrics

### Technical Metrics
- ✅ Test coverage: 80%+
- ✅ Type coverage: 100% (mypy strict mode)
- ✅ Import time: <50ms
- ✅ Memory footprint: <10MB (base)
- ✅ Load time: <100ms (per country)

### Quality Metrics
- ✅ Zero critical bugs
- ✅ Issue response time: <48 hours
- ✅ Documentation completeness: 100%
- ✅ API consistency with npm packages

### Community Metrics
- 📈 PyPI downloads per week
- ⭐ GitHub stars
- 🐛 Issue resolution rate
- 🤝 Community contributions

---

## 🚀 Getting Started

### For Implementers

1. **Read the specifications**
   - Start with [1-python-pypi-monorepo-plan.md](./1-python-pypi-monorepo-plan.md)
   - Review [2-python-vs-npm-comparison.md](./2-python-vs-npm-comparison.md)
   
2. **Follow the quick start guide**
   - Use [3-python-quick-start-guide.md](./3-python-quick-start-guide.md)
   - Complete Phase 1 (Setup)
   - Implement Phase 2 (Core functionality)

3. **Test and iterate**
   - Write tests alongside code
   - Run mypy for type checking
   - Use black and isort for formatting

4. **Publish and monitor**
   - Publish to TestPyPI first
   - Then publish to PyPI
   - Monitor downloads and issues

### For Contributors

1. **Understand the architecture**
   - Read all specification documents
   - Review existing npm packages
   - Understand data structure

2. **Set up development environment**
   - Install Python 3.8+
   - Install Poetry
   - Clone repository

3. **Make changes**
   - Follow coding standards
   - Write tests
   - Update documentation

4. **Submit PRs**
   - Ensure tests pass
   - Include documentation
   - Reference related issues

---

## 📖 Related Resources

### External Links
- [npm packages repository](https://github.com/dr5hn/countrystatecity)
- [API documentation](https://countrystatecity.in)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Poetry documentation](https://python-poetry.org/docs/)
- [PyPI packaging guide](https://packaging.python.org/)

### Internal Links
- [Main README](../README.md)
- [Contributing guidelines](../CONTRIBUTING.md)
- [License](../LICENSE)

---

## ❓ FAQ

### Why Python in addition to npm packages?
- Large Python community needs official packages
- Server-side and data science use cases
- Better integration with Django, Flask, FastAPI
- Avoid outdated/incomplete alternatives

### Why not use the existing npm packages with a bridge?
- Python developers expect native Python packages
- Better performance without JavaScript bridge
- Type safety with Pydantic
- Pythonic API design

### How is data kept in sync?
- Single source of truth: MySQL database
- Automated data generation scripts
- Same JSON structure as npm packages
- CI/CD ensures consistency

### What about other package registries (Conda, etc.)?
- Start with PyPI (most common)
- Can publish to Conda later if demand exists
- Focus on quality over quantity

---

## 📞 Contact

For questions or clarifications about these specifications:

- **Issues:** [GitHub Issues](https://github.com/dr5hn/countries-states-cities-database/issues)
- **Discussions:** [GitHub Discussions](https://github.com/dr5hn/countries-states-cities-database/discussions)
- **Email:** [Contact via API website](https://countrystatecity.in)

---

**Last Updated:** January 2025  
**Status:** Ready for Implementation  
**Next Action:** Begin Phase 1 of Quick Start Guide
