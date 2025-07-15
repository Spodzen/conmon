import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow
from sniffer import SnifferThread
from resolver import ResolverThread
from map_generator import MapGenerator
from firewall_manager import FirewallManager
import psutil
import socket

def get_lan_interface():
    """Attempts to find the primary non-loopback, non-VPN LAN interface, prioritizing 'Ethernet'."""
    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    potential_interfaces = []
    ethernet_interface = None

    for iface_name, iface_addrs in addresses.items():
        print(f"Considering interface: {iface_name}")
        if iface_name == 'NordLynx':  # Skip the VPN interface
            print(f"  Skipping {iface_name}: VPN interface.")
            continue

        if iface_name not in stats or not stats[iface_name].isup:
            print(f"  Skipping {iface_name}: Not up or no stats.")
            continue  # Skip inactive interfaces

        has_ipv4 = False
        for snicaddr in iface_addrs:
            if snicaddr.family == socket.AF_INET:  # Look for IPv4 addresses
                has_ipv4 = True
                # Exclude loopback and APIPA addresses
                if not snicaddr.address.startswith(('127.', '169.254.')):
                    print(f"  Found potential LAN IPv4 for {iface_name}: {snicaddr.address}")
                    if iface_name == 'Ethernet':
                        ethernet_interface = iface_name
                    else:
                        potential_interfaces.append(iface_name)
                    break # Found a valid IPv4, move to next interface
        
        if not has_ipv4:
            print(f"  Skipping {iface_name}: No IPv4 address.")

    if ethernet_interface:
        print(f"Selected LAN interface: {ethernet_interface} (Prioritized Ethernet)")
        return ethernet_interface
    elif potential_interfaces:
        print(f"Selected LAN interface: {potential_interfaces[0]} (First available)")
        return potential_interfaces[0]
    
    print("No suitable LAN interface found.")
    return None

# Authoritative Dark Theme Stylesheet
DARK_STYLESHEET = """
QWidget {
    background-color: #1e1e1e;
    color: #4dff4d;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #333333;
    color: #4dff4d;
    padding: 4px;
    border: 1px solid #555555;
}
QTableWidget {
    gridline-color: #555555;
    border: 1px solid #555555;
}
QTableWidget::item {
    border-bottom: 1px solid #555555;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #333333;
    border: 1px solid #555555;
    width: 15px;
    height: 15px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #555555;
    min-height: 20px;
    min-width: 20px;
}
QSplitter::handle {
    background-color: #555555;
}
"""

class Application(QApplication):
    def __init__(self, sys_argv):
        super(Application, self).__init__(sys_argv)
        # Apply the theme globally and definitively.
        self.setStyleSheet(DARK_STYLESHEET)

        self.firewall_manager = FirewallManager()

        self.main_window = MainWindow()
        self.main_window.location_selected.connect(self.main_window.pan_map_to)
        self.main_window.firewall_toggle_changed.connect(self.handle_firewall_toggle)
        self.main_window.show()

        self.map_generator = MapGenerator()
        self.map_generator.save_map()
        self.main_window.set_map_name(self.map_generator.map.get_name())

        self.resolver_thread = ResolverThread()
        self.resolver_thread.resolved.connect(self.handle_resolved)
        self.resolver_thread.start()

        # Determine interfaces to sniff
        interfaces_to_sniff = ['NordLynx']
        lan_iface = get_lan_interface()
        if lan_iface and lan_iface not in interfaces_to_sniff:
            interfaces_to_sniff.append(lan_iface)
        print(f"Interfaces to sniff: {interfaces_to_sniff}") # Debug print
        self.sniffer_thread = SnifferThread(interfaces=interfaces_to_sniff)
        self.sniffer_thread.packet_captured.connect(self.handle_packet)
        self.sniffer_thread.start()

        self.connections = {}

    def handle_firewall_toggle(self, is_checked):
        if is_checked:
            self.firewall_manager.enable_block()
        else:
            self.firewall_manager.disable_block()

    def handle_packet(self, packet_data):
        print(f"Received packet_data in main.py: {packet_data}") # Debug print
        connection_key = f"{packet_data['dst_ip']}:{packet_data['dst_port']}:{packet_data['interface']}"

        if connection_key not in self.connections:
            self.connections[connection_key] = {
                "dst_ip": packet_data['dst_ip'],
                "dst_port": packet_data['dst_port'],
                "volume": 0,
                "process_name": packet_data["process_name"],
                "interface": packet_data["interface"],
            }
            self.resolver_thread.resolve(packet_data['dst_ip'])
        
        self.connections[connection_key]["volume"] += packet_data["length"]
        if packet_data["process_name"] != "Unknown":
            self.connections[connection_key]["process_name"] = packet_data["process_name"]

        self.main_window.add_or_update_connection(connection_key, self.connections[connection_key])

    def handle_resolved(self, resolved_data):
        if resolved_data["lat"] is not None and resolved_data["lon"] is not None:
            popup = f"{resolved_data['ip']}\n{resolved_data['network']}"
            self.map_generator.add_location(resolved_data["lat"], resolved_data["lon"], popup)
            self.map_generator.save_map()
            self.main_window.refresh_map()

        self.main_window.update_resolved_info(
            resolved_data["ip"],
            resolved_data["location_str"],
            resolved_data["network"],
            resolved_data.get("lat"),
            resolved_data.get("lon")
        )

    def exec_(self):
        exit_code = super(Application, self).exec_()
        self.sniffer_thread.stop()
        self.resolver_thread.stop()
        self.firewall_manager.cleanup()
        return exit_code

if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())