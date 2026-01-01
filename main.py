from wifi import wifi

if __name__ == "__main__":
    ssid = "Nhim"
    password = "your_password_here"
    # Create an object of the wifi class
    wifi = wifi(ssid, password)
    security_info = wifi.get_wifi_security()
    print(security_info)

    ssids = wifi.scan_wifi_ssids()
    if ssids:
        print("Available Wi-Fi SSIDs:")
        for ssid in ssids:
            print(f"- {ssid}")
    else:
        print("No Wi-Fi networks found.")