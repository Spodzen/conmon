# Development Process

This document outlines the agreed-upon development process for the Conmon project.

## Core Principles

1.  **Virtual Environment:** All Python development, including running scripts and installing packages, will be conducted within a dedicated virtual environment (`venv`). This ensures dependency isolation and project reproducibility.

2.  **Unit Testing:** Unit tests will be created for new functionality. Tests are crucial for verifying correctness and preventing regressions.

3.  **Incremental Testing:** After any incremental code change, the relevant unit tests will be run to ensure the changes have not introduced any issues.

4.  **Structured Planning:** A detailed project plan will be maintained in the `docs` directory. We will follow the steps outlined in the plan, revising it as necessary to adapt to new requirements or discoveries.

5.  **Code Modularity:** To maintain readability and ease of maintenance, the codebase will be split into logical files and modules. This avoids creating large, monolithic files.
6.  **Administrator Privileges:** Due to the low-level network access required for packet sniffing, the application must be run with administrator privileges.
