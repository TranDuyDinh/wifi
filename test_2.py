import subprocess
import tempfile
import os
import time

SSID = "T6_4(615-624)"
# PASSWORD = "123456789"
PASSWORD = "113114115"
# SSID = "Nhim"
# PASSWORD = "113114115116"

def check_password_validity(password):
    """Check if the password meets WPA2 requirements."""
    if len(password) < 8 or len(password) > 63:
        return False, "Password must be between 8 and 63 characters long"
    return True, "Password length is valid"

def is_connected_to_ssid(target_ssid):
    """Check if currently connected to the specified SSID."""
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

def check_connection_result(target_ssid, was_connected_before):
    """Determine if the connection attempt was successful and password is correct."""
    currently_connected = is_connected_to_ssid(target_ssid)

    if currently_connected and not was_connected_before:
        return True, "✓ Successfully connected! Password appears to be correct."
    elif currently_connected and was_connected_before:
        return None, "? Already connected to this network. Cannot verify password."
    else:
        return False, "✗ Failed to connect. Password might be incorrect or network unavailable."

# Check password validity
is_valid, message = check_password_validity(PASSWORD)
if not is_valid:
    print(f"Password validation failed: {message}")
    exit(1)

print("Password validation passed.")

wifi_profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{SSID}</name>
    <SSIDConfig>
        <SSID>
            <name>{SSID}</name>
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
                <keyMaterial>{PASSWORD}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""

# Write profile to temp file
with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as f:
    f.write(wifi_profile.encode("utf-8"))
    profile_path = f.name

try:
    # Add Wi-Fi profile
    print("Adding Wi-Fi profile...")
    add_result = subprocess.run(
        ["netsh", "wlan", "add", "profile", f"filename={profile_path}", "user=current"],
        capture_output=True,
        text=True
    )

    print(f"Return code: {add_result.returncode}")
    print(f"STDOUT: {add_result.stdout}STDERR: {add_result.stderr}")

    if add_result.returncode != 0:
        print(f"Failed to add Wi-Fi profile.")
        exit(1)

    # Check if already connected before attempting
    was_connected_before = is_connected_to_ssid(SSID)
    if was_connected_before:
        print(f"Already connected to {SSID}")

    # Connect to Wi-Fi
    print(f"Attempting to connect to Wi-Fi: {SSID}")
    connect_result = subprocess.run(
        ["netsh", "wlan", "connect", f"name={SSID}"],
        capture_output=True,
        text=True
    )

    if connect_result.returncode != 0:
        print(f"Failed to initiate connection to Wi-Fi: {connect_result.stderr}")
        print("This could be due to incorrect password, network unavailable, or insufficient privileges.")
        exit(1)

    # Wait for connection to establish
    print("Waiting for connection to establish...")
    time.sleep(5)

    # Check connection result
    success, message = check_connection_result(SSID, was_connected_before)
    print(message)

    # if success is True:
    #     print("✓ Password verification: CORRECT")
    # elif success is False:
    #     print("✗ Password verification: INCORRECT or network issue")
    # else:
    #     print("? Password verification: INCONCLUSIVE (already connected)")

finally:
    os.remove(profile_path)
