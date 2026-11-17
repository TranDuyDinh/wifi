import os
import subprocess
import re
import tempfile
import time
import platform


class wifi:
    def __init__(self):
        self.__TIME_WAIT_CONNECT = 5  # seconds
        self._WPA2_MIN_CHARS = 8
        self._WPA2_MAX_CHARS = 63

    def __check_password_validity(self, password):
        """
        Check if the password meets WPA2 requirements.
        """
        if len(password) < self._WPA2_MIN_CHARS or len(password) > self._WPA2_MAX_CHARS:
            return False, "Password must be between 8 and 63 characters long"
        return True, "Password length is valid"

    def _add_wifi_profile(self, profile_xml):
        """
        Add a Wi-Fi profile from the given XML string.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as f:
            f.write(profile_xml.encode("utf-8"))
            profile_path = f.name
        try:
            # print("Adding Wi-Fi profile...")
            add_result = subprocess.run(
                ["netsh", "wlan", "add", "profile", f"filename={profile_path}", "user=current"],
                capture_output=True,
                text=True
            )
            # print(f"Return code: {add_result.returncode}")
            # print(f"STDOUT: {add_result.stdout}STDERR: {add_result.stderr}")
            if add_result.returncode != 0:
                return False, "Failed to add Wi-Fi profile"
            else:
                return True, "Success to add Wi-Fi profile"
        finally:
            os.remove(profile_path)

    def _remove_wifi_profile(self, ssid_target):
        """
        Remove the profile since password is wrong.
        """
        try:
            # print("Removing invalid Wi-Fi profile...")
            delete_result = subprocess.run(
                ["netsh", "wlan", "delete", "profile", f"name={ssid_target}"],
                capture_output=True,
                text=True
            )
            if delete_result.returncode == 0:
                return True, "Wi-Fi profile removed successfully."
            else:
                return False, f"Failed to remove Wi-Fi profile: {delete_result.stderr}"
        except Exception as e:
            return False, f"Error removing Wi-Fi profile: {e}"

    def _is_connected_to_ssid(self, target_ssid):
        """
        Check if currently connected to the specified SSID.
        """
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'SSID' in line and ':' in line:
                    # Look for the line that shows the connected SSID
                    ssid_line = line.split(':', 1)[1].strip()
                    if ssid_line == target_ssid:
                        # Check if the state is "connected"
                        for j in range(i-5, i+5):  # Check surrounding lines for state
                            if j >= 0 and j < len(lines) and 'State' in lines[j]:
                                state_line = lines[j].split(':', 1)[1].strip()
                                if 'connected' in state_line.lower():
                                    return True
            return False
        except subprocess.CalledProcessError:
            return False

    def scan_wifi_ssids(self):
        """
        Retrieves the SSIDs of all available Wi-Fi networks.

        Returns:
            list: A list of SSIDs of available Wi-Fi networks, or an empty list if none found.
        """
        try:
            # Execute the command to get all Wi-Fi networks
            stream = os.popen('netsh wlan show networks')
            output = stream.read()

            # Parse the output to find all SSIDs
            ssids = []
            for line in output.split('\n'):
                if line.strip().startswith('SSID'):
                    parts = line.split(':')
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid and ssid not in ssids:  # Avoid duplicates
                            ssids.append(ssid)
            return ssids
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_wifi_security(self, ssid):
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            encoding="utf-8",
            errors="ignore"
        )

        blocks = result.split("SSID ")
        for block in blocks:
            if block.strip().startswith(":"):
                continue
            if ssid in block:
                auth = re.search(r"Authentication\s*:\s*(.+)", block)
                enc = re.search(r"Encryption\s*:\s*(.+)", block)
                return {
                    "SSID": ssid,
                    "Authentication": auth.group(1).strip() if auth else "Unknown",
                    "Encryption": enc.group(1).strip() if enc else "Unknown"
                }

        return {
            "SSID": ssid,
            "Authentication": "Network not found",
            "Encryption": "Network not found"
        }

    def connect_to_wifi(self, ssid, password):
        """
        Connects to a Wi-Fi network with the given SSID and password.
        Assumes WPA2-PSK security.

        Args:
            ssid (str): The SSID of the Wi-Fi network.
            password (str): The password for the Wi-Fi network.

        Returns:
            True: Password appears to be correct.
            False: Password might be incorrect or network unavailable.
            None: Already connected or network unavailable.
        """
        # Check password validity
        is_valid, message = self.__check_password_validity(password)
        if not is_valid:
            return None, f"Password validation failed: {message}"

        wifi_profile = f"""<?xml version="1.0"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>
        """
        # Add Wi-Fi profile
        add_profile, message = self._add_wifi_profile(wifi_profile)
        if add_profile is False:
            return None, message

        # Check if already connected before attempting
        was_connected_before = self._is_connected_to_ssid(ssid)
        if was_connected_before:
            return None, f"Already connected to {ssid}"

        # Connect to Wi-Fi
        __debug__ and print(f"Attempting to connect to Wi-Fi: {ssid}")
        connect_result = subprocess.run(
            ["netsh", "wlan", "connect", f"name={ssid}"],
            capture_output=True,
            text=True
        )

        if connect_result.returncode != 0:
            return None, f"Failed to initiate connection to Wi-Fi: {connect_result.stderr}"

        # Wait for connection to establish
        __debug__ and print("Waiting for connection to establish...")
        time.sleep(self.__TIME_WAIT_CONNECT)

        # Check connection result
        currently_connected = self._is_connected_to_ssid(ssid)

        if currently_connected is True:
            return True, "Password verification: CORRECT"
        else:
            remove_profile, message = self._remove_wifi_profile(ssid)
            if remove_profile is False:
                print(message)
            return False, "Password verification: INCORRECT"



class extractor:
    """
    Extracts Wi-Fi profile details (SSID, BSSID, Security Type) 
    from the local machine's active connection.
    """

    def __init__(self):
        self.os_type = platform.system()

    def _run_command(self, cmd):
        """Helper to run shell commands."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    def get_windows_profile(self):
        """Extracts Wi-Fi profile from Windows netsh output."""
        output = self._run_command("netsh wlan show interface")
        if "Profile" not in output:
            return None
        
        # Extract SSID
        ssid_match = re.search(r"SSID\s+:\s+(.*)", output)
        ssid = ssid_match.group(1).strip() if ssid_match else "Unknown"
        
        # Extract BSSID (MAC Address)
        bssid_match = re.search(r"BSSID\s+:\s+(.*)", output)
        bssid = bssid_match.group(1).strip() if bssid_match else "Unknown"
        
        # Extract Security Type
        security_match = re.search(r"Authentication\s+:\s+(.*)", output)
        auth = security_match.group(1).strip() if security_match else "Unknown"
        
        security_match2 = re.search(r"Cipher\s+:\s+(.*)", output)
        cipher = security_match2.group(1).strip() if security_match2 else "Unknown"
        
        security_type = f"{auth} / {cipher}" if auth != "Unknown" else "Unknown"

        return {
            "ssid": ssid,
            "bssid": bssid,
            "security": security_type,
            "os": "Windows"
        }

    def get_macos_profile(self):
        """Extracts Wi-Fi profile from macOS airport command."""
        output = self._run_command("/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport -I")
        if not output:
            return None

        ssid = re.search(r"SSID\s+:\s+(.*)", output)
        bssid = re.search(r"bssid\s+:\s+(.*)", output)
        security = re.search(r"security\s+:\s+(.*)", output)

        return {
            "ssid": ssid.group(1).strip() if ssid else "Unknown",
            "bssid": bssid.group(1).strip() if bssid else "Unknown",
            "security": security.group(1).strip() if security else "Unknown",
            "os": "macOS"
        }

    def get_linux_profile(self):
        """Extracts Wi-Fi profile from Linux nmcli or iwctl."""
        # Try nmcli first
        output = self._run_command("nmcli -t -f active,ssid,bssid,sec device wifi list 2>/dev/null | grep '^yes'")
        if not output:
            # Fallback to iwconfig or ip link if nmcli isn't available or no data
            output = self._run_command("iw dev wlan0 link 2>/dev/null || iw dev wlp* link 2>/dev/null")
        
        # Simple parsing for nmcli output format: active:SSID:BSSID:SEC
        if ":" in output:
            parts = output.split(":")
            if len(parts) >= 4:
                return {
                    "ssid": parts[1],
                    "bssid": parts[2],
                    "security": parts[3],
                    "os": "Linux"
                }
        
        # Fallback for iw output
        ssid_match = re.search(r"SSID=(.*)", output)
        bssid_match = re.search(r"addr\s+(:?\w{2}:){5}\w{2}", output)
        
        return {
            "ssid": ssid_match.group(1).strip() if ssid_match else "Unknown",
            "bssid": bssid_match.group(0).split("addr ")[1] if bssid_match else "Unknown",
            "security": "Unknown",
            "os": "Linux"
        }

    def get_profile(self):
        """Returns the current Wi-Fi profile based on OS."""
        if self.os_type == "Windows":
            return self.get_windows_profile()
        elif self.os_type == "Darwin":  # macOS
            return self.get_macos_profile()
        elif self.os_type == "Linux":
            return self.get_linux_profile()
        else:
            return {"error": f"Unsupported OS: {self.os_type}"}

# Example Usage
if __name__ == "__main__":
    extractor = extractor()
    profile = extractor.get_profile()
    
    if profile and "error" not in profile:
        print(f"Connected Wi-Fi Profile:")
        print(f"  SSID:     {profile['ssid']}")
        print(f"  BSSID:    {profile['bssid']}")
        print(f"  Security: {profile['security']}")
        print(f"  OS:       {profile['os']}")
    else:
        print("Could not retrieve Wi-Fi profile.")
