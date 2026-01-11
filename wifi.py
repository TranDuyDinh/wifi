import os
import subprocess
import re
import tempfile
import time

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
        print(f"Attempting to connect to Wi-Fi: {ssid}")
        connect_result = subprocess.run(
            ["netsh", "wlan", "connect", f"name={ssid}"],
            capture_output=True,
            text=True
        )

        if connect_result.returncode != 0:
            return None, f"Failed to initiate connection to Wi-Fi: {connect_result.stderr}"

        # Wait for connection to establish
        print("Waiting for connection to establish...")
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
