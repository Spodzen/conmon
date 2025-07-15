# Project Plan: Conmon

This document outlines the development plan for the Conmon application. It will be updated as the project progresses.

## Phase 1: Project Setup & Core Sniffing (Revised)

-   [x] **1.1: Initialize Project Structure**
    -   [x] Create a `.gitignore` file.
    -   [x] Create a `src` directory for source code.
    -   [x] Create an empty `main.py` file.
-   [x] **1.2: Install Initial Dependencies (Revised)**
    -   [x] Activate the virtual environment.
    -   [x] **Important:** Install [Wireshark](https://www.wireshark.org/download.html).
    -   [x] **Important:** Install [Npcap](https://nmap.org/npcap/) (with "Install Npcap in WinPcap API-compatible Mode" checked).
    -   [x] Install `pyshark` for packet sniffing.
    -   [x] Install `psutil` for process information.
    -   [x] Install `PyQt5` for the GUI.
    -   [x] Generate a `requirements.txt` file.
-   [x] **1.3: Implement Basic Packet Sniffing (Revised)**
    -   [x] In `src/sniffer.py`, create a function to capture outbound TCP packets using `pyshark`.
    -   [x] Use `psutil` to correlate packets with the processes that sent them.

## Phase 2: Basic GUI & Data Display

-   [x] **2.1: Create Main Application Window**
    -   [x] In `src/gui.py`, create the main application window using PyQt5.
    -   [x] Add a `QTableWidget` to display connection data.
    -   [x] Define table headers.
-   [x] **2.2: Integrate Sniffer with GUI**
    -   [x] Use PyQt's signals and slots mechanism to pass data from the sniffer thread to the GUI thread.
    -   [x] Update the table in real-time as new packets are captured.
    -   [x] Implement data aggregation to track data volume per connection.

## Phase 3: Geolocation and DNS Resolution

-   [x] **3.1: Install Geolocation Library**
    -   [x] Install the `geoip2` and `dnspython` libraries.
-   [x] **3.2: Implement IP Geolocation**
    -   [x] Create a module `src/resolver.py`.
    -   [x] Add a function to look up the country/city for a given IP address.
    -   [x] Add a "Location" column to the GUI table.
-   [x] **3.3: Implement Reverse DNS**
    -   [x] Add a function to `src/resolver.py` to perform reverse DNS lookups.
    -   [x] Add "Domain Name" column to the GUI table.

## Phase 4: Data Visualization & Features (Future)

-   [ ] **4.1: World Map Visualization**
    -   [ ] Investigate and select a suitable library for displaying a world map.
    -   [ ] Plot traffic destinations on the map.
-   [ ] **4.2: Add Charts and Graphs**
    -   [ ] Install `matplotlib` or `pyqtgraph`.
    -   [ ] Add charts to visualize data (e.g., pie chart of traffic by country).
-   [ ] **4.3: Implement Search and Filtering**
    -   [ ] Add a search bar to filter the connection list.

## Phase 5: Testing and Packaging (Future)

-   [ ] **5.1: Write Unit Tests**
    -   [ ] Create a `tests` directory.
    -   [ ] Write unit tests for the resolver and data aggregation logic.
-   [ ] **5.2: Package Application**
    -   [ ] Install `pyinstaller`.
    -   [ ] Create a build script to package the application into a distributable executable.