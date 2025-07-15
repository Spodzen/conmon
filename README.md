# Conmon - Host Outbound Network Traffic Monitor

Conmon is a GUI application for Windows that monitors your computer's outbound network traffic. It provides insights into where your data is going, identifying the geographical location, domain names, and network providers of the destinations. It also includes advanced features for controlling internet access and detailed traffic visualization.

## Features

-   **Real-time Traffic Monitoring:** Captures and displays outbound network connections as they happen across multiple network interfaces (e.g., VPN and LAN).
-   **Process Identification:** Shows the name of the application that is generating the network traffic.
-   **Interface Display:** Clearly indicates which network interface (e.g., VPN, Ethernet) each packet is using.
-   **Geolocation:** Resolves destination IP addresses to their physical location (City, Country).
-   **DNS Resolution:** Finds the domain name associated with the destination IP address.
-   **Internet Blocking with LAN Passthrough:** Allows you to block all internet-bound traffic while maintaining full access to your local network. This is controlled via a toggle in the GUI.
-   **Visual Traffic Distinction:** Non-VPN traffic is highlighted (e.g., in yellow text) for easy identification.
-   **Interactive World Map:** Visualizes traffic destinations on a world map with interactive panning.
-   **Filtering and Search:** Provides a filter bar to search and continuously filter connections based on various criteria (e.g., process name, IP address, interface).
-   **Dark Theme UI:** Features a professional, easy-to-read dark theme.
-   **Auto-Sorting:** Automatically sorts the connection list to show the highest traffic nodes at the top.
-   **Dynamic Column Sizing:** Ensures all information in the table is fully visible without being cut off.

## Getting Started

**Prerequisites:**

-   **GeoLite2 Database:** For IP geolocation, you must download the free GeoLite2 City database from MaxMind. 
    1.  Go to the [MaxMind website](https://www.maxmind.com/en/geolite2/signup) and sign up for a free account.
    2.  Once logged in, navigate to the "Download Files" section.
    3.  Download the **GeoLite2-City** database in the `mmdb` format.
    4.  Download the **GeoLite2-ASN** database in the `mmdb` format.
    5.  Place both the `GeoLite2-City.mmdb` and `GeoLite2-ASN.mmdb` files in the root directory of this project.
-   **Wireshark:** You must install [Wireshark](https://www.wireshark.org/download.html). `pyshark` uses its `tshark` component to capture packets.
-   **Npcap:** You must install [Npcap](https://nmap.org/npcap/) for this application to work. During installation, make sure to check the box for **"Install Npcap in WinPcap API-compatible Mode"**.

**Installation:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/conmon.git
    cd conmon
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

**Usage:**

To run the application, you **must** open your terminal or PowerShell as an **Administrator**.

```bash
.\venv\Scripts\python.exe src\main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
