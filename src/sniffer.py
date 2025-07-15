# src/sniffer.py

import pyshark
from PyQt5.QtCore import QThread, pyqtSignal
import psutil
import threading
import asyncio

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

    def __init__(self, interfaces=None): # Changed to accept a list of interfaces
        super().__init__()
        self.interfaces = interfaces if interfaces is not None else []
        self.captures = []
        self.running = True
        self.threads = []

    def run(self):
        print(f"Starting sniffer thread on interfaces: {', '.join(self.interfaces)}")
        bpf_filter = "tcp and not (dst net 192.168.0.0/16 or dst net 10.0.0.0/8 or dst net 172.16.0.0/12)"
        
        for iface in self.interfaces:
            thread = threading.Thread(target=self._sniff_single_interface_blocking, args=(iface, bpf_filter))
            self.threads.append(thread)
            thread.start()
        
        # Keep the main thread alive while sniffer threads are running
        try:
            while self.running:
                self.msleep(100) # Sleep to prevent busy-waiting
        finally:
            pass # No loop to close here

    def _sniff_single_interface_blocking(self, iface_name, bpf_filter):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        capture = None
        try:
            capture = pyshark.LiveCapture(interface=iface_name, bpf_filter=bpf_filter)
            for packet in capture.sniff_continuously(packet_count=None):
                if not self.running:
                    break
                try:
                    src_port = packet.tcp.srcport
                    process_name = get_process_name_from_connection(int(src_port))

                    packet_data = {
                        "dst_ip": packet.ip.dst,
                        "dst_port": packet.tcp.dstport,
                        "length": int(packet.length),
                        "process_name": process_name,
                        "interface": iface_name # Use the passed interface name
                    }
                    self.packet_captured.emit(packet_data)
                except AttributeError:
                    pass # Ignore non-IP/TCP packets
        except Exception as e:
            print(f"Error sniffing on interface {iface_name}: {e}")
        finally:
            if capture:
                capture.close()
            loop.close()

    def stop(self):
        print("Stopping sniffer thread...")
        self.running = False
        for capture in self.captures:
            capture.close()
        for thread in self.threads:
            thread.join(timeout=1) # Give threads a chance to finish
        self.quit()
        self.wait()
