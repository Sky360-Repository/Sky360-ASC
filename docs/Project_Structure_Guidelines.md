# Project Structure Guidelines

This document defines what goes inside each top-level folder in the project.  

## `docs/`
Project documentation, design notes, diagrams, and developer guides.

- **What goes here**
  - Architecture diagrams  
  - Markdown documentation (`.md`)  
  - API usage guides  
  - Design decisions (ADR-style if used)  
  - Release notes or changelogs (if not stored elsewhere)

- **Subfolders**
  - `docs/img/`  
    - Images referenced by documentation  
    - Diagrams, flowcharts, screenshots  
    - No code, no binaries, no random exports

- **Rules**
  - Keep documentation in Markdown unless a diagram tool requires otherwise  
  - Use relative links to images inside `docs/img/`  
  - Do not store generated files (e.g., HTML exports) unless explicitly needed
  - No code snippets, no tests, no notebooks - this is not a sandbox.

## `scripts/`
Maintenance and automation scripts used for development, setup, or repo hygiene.

- **What goes here**
  - Environment setup scripts  
    - Example: `setup.sh` (creates environment, installs dependencies)  
  - Build helpers  
  - Code generation scripts  
    - Example: `create_proto_bindings.sh`  
  - Linting / formatting helpers  
  - CI/CD helper scripts (if not stored in `.github/`)

- **Rules**
  - Scripts must be **idempotent** (safe to run multiple times)  
  - Scripts must be **documented at the top** with purpose + usage  
  - No code snippets, no tests, no notebooks - this is not a sandbox.  
  - Use descriptive names (`generate_docs.sh`, `clean_cache.py`, etc.)

## `src/`
All source code for the project — packages, modules, and internal libraries.

- **What goes here**
  - Project-specific Python packages  
  - Internal modules  
  - Submodules included as part of the project  
  - Shared utilities used across packages

- **Structure**
  ```
  src/
  ├── package_a/        # A project-specific package
  ├── package_b/        # Another package
  └── sub_module_x/     # A standalone module or imported submodule
  ```

- **Rules**
  - Each package must contain:
    - `__init__.py`
    - Clean and structured code
    - Internal documentation (`README.md` inside the package is encouraged)
  - Submodules - Version-controlled
  - No code snippets, no scripts, no tests, no notebooks - this is not a sandbox.

- **Naming conventions**
  - Packages: `snake_case`  
  - Modules: `snake_case`  
  - Classes: `PascalCase`  
  - Functions: `snake_case`  
  - Constants: `UPPER_CASE`

## `tests/`
All unit tests, integration tests, and test utilities.

- **What goes here**
  - Test files (`test_*.py`)  
  - Fixtures  
  - Mock data  
  - Integration test helpers  
  - Test-only utilities

- **Rules**
  - Mirror the structure of `src/` when possible  
    ```
    src/package_a/       → tests/package_a/test_*.py
    src/package_b/       → tests/package_b/test_*.py
    ```
  - Tests must be deterministic  
  - Use pytest (unless project specifies otherwise)  
  - No production code  
  - No large binary files (mock data should be small)
