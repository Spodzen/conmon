# Development Process

This document outlines the agreed-upon development process for the Conmon project.

## Core Principles

1.  **Virtual Environment:** All Python development, including running scripts and installing packages, will be conducted within a dedicated virtual environment (`venv`). This ensures dependency isolation and project reproducibility.

2.  **Unit Testing:** Unit tests will be created for new functionality. Tests are crucial for verifying correctness and preventing regressions.

3.  **Incremental Testing:** After any incremental code change, the relevant unit tests will be run to ensure the changes have not introduced any issues.

4.  **Structured Planning:** A detailed project plan will be maintained in the `docs` directory. We will follow the steps outlined in the plan, revising it as necessary to adapt to new requirements or discoveries.

5.  **Code Modularity:** To maintain readability and ease of maintenance, the codebase will be split into logical files and modules. This avoids creating large, monolithic files.
6.  **Administrator Privileges:** Due to the low-level network access required for packet sniffing, the application must be run with administrator privileges.

## Data Structures

### `packet_data` (Dictionary emitted by SnifferThread)

This dictionary contains information about each captured packet:

*   `dst_ip` (str): Destination IP address.
*   `dst_port` (int): Destination port.
*   `length` (int): Length of the packet in bytes.
*   `process_name` (str): Name of the process that sent the packet (e.g., "chrome.exe"). Defaults to "Unknown" if not found.
*   `interface` (str): Name of the network interface the packet was sniffed on (e.g., "NordLynx", "Ethernet").

### `connections` (Dictionary in Application class)

This dictionary aggregates data for unique connections. The key for each entry is a composite string: `"{dst_ip}:{dst_port}:{interface}"`. Each value is a dictionary containing:

*   `dst_ip` (str): Destination IP address.
*   `dst_port` (int): Destination port.
*   `volume` (int): Total data volume in bytes for this unique connection.
*   `process_name` (str): The process name associated with this connection. Updated if a non-"Unknown" name is found.

