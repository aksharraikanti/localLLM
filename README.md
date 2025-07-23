# localLLM

[![CI](https://github.com/your-org/localLLM/actions/workflows/ci.yml/badge.svg)]()
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)]()

## Local Environment Setup

To simplify local setup on macOS (Apple Silicon), run the provided script:

```bash
bash scripts/setup_local_env.sh
```

## Getting Started

Follow these steps to get the project running locally:

1. Copy the environment template and fill in your credentials:
   ```bash
   cp .env.template .env
   ```
2. Install Python dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Install and run pre-commit hooks:
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```
4. Run the test suite:
   ```bash
   pytest --maxfail=1 --disable-warnings -q
   ```
