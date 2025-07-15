
import subprocess
import psutil

class FirewallManager:
    RULE_NAME_BLOCK = "ConmonBlockInternet"
    RULE_NAME_ALLOW_LAN = "ConmonAllowLAN"

    def __init__(self):
        self._cleanup_rules() # Clean up any old rules on startup
        self._create_rules()

    def _run_command(self, command):
        """Helper to run shell commands with admin rights, suppressing output."""
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_lan_subnets(self):
        """Identifies local IPv4 subnets to allow."""
        subnets = ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12'] # Standard private ranges
        # Add currently connected subnets for more specific rules
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    continue # Skip MAC addresses
                if psutil.AF_INET and hasattr(addr, 'netmask') and addr.netmask:
                    # Create a network object and add its string representation
                    import ipaddress
                    network = ipaddress.ip_network(f'{addr.address}/{addr.netmask}', strict=False)
                    subnets.append(str(network))
        return ",".join(sorted(list(set(subnets)))) # Return unique, sorted list

    def _create_rules(self):
        lan_subnets = self._get_lan_subnets()
        # Rule 1: Block all outbound traffic (initially disabled)
        block_command = (
            f'netsh advfirewall firewall add rule name="{self.RULE_NAME_BLOCK}" dir=out action=block enable=no'
        )
        # Rule 2: Allow outbound traffic to local subnets (always enabled, but only works when block is active)
        allow_command = (
            f'netsh advfirewall firewall add rule name="{self.RULE_NAME_ALLOW_LAN}" dir=out action=allow remoteip={lan_subnets} enable=yes'
        )
        self._run_command(block_command)
        self._run_command(allow_command)

    def enable_block(self):
        """Enables the internet block."""
        command = f'netsh advfirewall firewall set rule name="{self.RULE_NAME_BLOCK}" new enable=yes'
        return self._run_command(command)

    def disable_block(self):
        """Disables the internet block."""
        command = f'netsh advfirewall firewall set rule name="{self.RULE_NAME_BLOCK}" new enable=no'
        return self._run_command(command)

    def _cleanup_rules(self):
        """Removes the firewall rules."""
        self._run_command(f'netsh advfirewall firewall delete rule name="{self.RULE_NAME_BLOCK}"')
        self._run_command(f'netsh advfirewall firewall delete rule name="{self.RULE_NAME_ALLOW_LAN}"')

    def cleanup(self):
        """Public method to be called on application exit."""
        self.disable_block() # Ensure block is off before deleting
        self._cleanup_rules()
