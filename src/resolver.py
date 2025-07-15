# src/resolver.py

import geoip2.database
from PyQt5.QtCore import QThread, pyqtSignal

DB_CITY_PATH = 'GeoLite2-City.mmdb'
DB_ASN_PATH = 'GeoLite2-ASN.mmdb'

class ResolverThread(QThread):
    resolved = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.city_reader = None
        self.asn_reader = None
        self.ips_to_resolve = []
        self.is_running = True

    def run(self):
        try:
            self.city_reader = geoip2.database.Reader(DB_CITY_PATH)
            self.asn_reader = geoip2.database.Reader(DB_ASN_PATH)
        except FileNotFoundError as e:
            print(f"ERROR: Database not found: {e.filename}")
            return

        while self.is_running:
            if self.ips_to_resolve:
                ip = self.ips_to_resolve.pop(0)
                location_data = self._get_location(ip)
                network = self._get_network(ip)
                self.resolved.emit({
                    "ip": ip, 
                    "location_str": location_data['str'], 
                    "lat": location_data['lat'],
                    "lon": location_data['lon'],
                    "network": network
                })
            else:
                self.msleep(100)

    def resolve(self, ip_address):
        if ip_address not in self.ips_to_resolve:
            self.ips_to_resolve.append(ip_address)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

    def _get_location(self, ip):
        default_response = {"str": "N/A", "lat": None, "lon": None}
        if self._is_private_ip(ip) or not self.city_reader:
            return default_response
        try:
            response = self.city_reader.city(ip)
            city = response.city.name or "Unknown"
            country = response.country.name or "Unknown"
            return {
                "str": f"{city}, {country}",
                "lat": response.location.latitude,
                "lon": response.location.longitude
            }
        except (geoip2.errors.AddressNotFoundError, TypeError):
            return default_response
        except Exception:
            return {"str": "Error", "lat": None, "lon": None}

    def _get_network(self, ip):
        if self._is_private_ip(ip) or not self.asn_reader:
            return "N/A"
        try:
            response = self.asn_reader.asn(ip)
            return response.autonomous_system_organization
        except geoip2.errors.AddressNotFoundError:
            return "N/A"
        except Exception:
            return "Error"

    def _is_private_ip(self, ip):
        return ip.startswith(('192.168.', '10.', '172.16.'))