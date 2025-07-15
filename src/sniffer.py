# src/sniffer.py

import pyshark
from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
import psutil

def get_process_name_from_connection(src_port):
    """Finds a process name by looking up the local port in the connection table."""
    try:
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr.port == src_port and conn.pid is not None:
                return psutil.Process(conn.pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    return "Unknown"

class SnifferThread(QThread):
    packet_captured = pyqtSignal(dict)

    def __init__(self, interface='NordLynx'): # Changed to the VPN interface
        super().__init__()
        self.interface = interface
        self.capture = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print(f"Starting sniffer thread on VPN interface: {self.interface}")
        try:
            # Re-enabling the outbound filter, which should now work correctly.
            bpf_filter = "tcp and not (dst net 192.168.0.0/16 or dst net 10.0.0.0/8 or dst net 172.16.0.0/12)"
            self.capture = pyshark.LiveCapture(interface=self.interface, bpf_filter=bpf_filter)
            
            for packet in self.capture.sniff_continuously():
                try:
                    src_port = packet.tcp.srcport
                    process_name = get_process_name_from_connection(int(src_port))

                    packet_data = {
                        "dst_ip": packet.ip.dst,
                        "dst_port": packet.tcp.dstport,
                        "length": int(packet.length),
                        "process_name": process_name,
                    }
                    self.packet_captured.emit(packet_data)
                except AttributeError:
                    pass # Ignore non-IP/TCP packets
        except Exception as e:
            print(f"An error occurred in the sniffer thread: {e}")

    def stop(self):
        print("Stopping sniffer thread...")
        if self.capture:
            self.capture.close()
        self.quit()
        self.wait()
