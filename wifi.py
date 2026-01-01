import os
import subprocess
import re

def scan_wifi_ssids():
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

def get_wifi_security(ssid):
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


if __name__ == "__main__":
    ssid = "Nhim"
    security_info = get_wifi_security(ssid)
    print(security_info)

    # ssids = scan_wifi_ssids()
    # if ssids:
    #     print("Available Wi-Fi SSIDs:")
    #     for ssid in ssids:
    #         print(f"- {ssid}")
    # else:
    #     print("No Wi-Fi networks found.")