from wifi import wifi
from password import password

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

def get_type():
    """
    Display menu options and get user input for password type as number, letters or both.

    Returns:
        int: User's choice (1, 2, 3 or 4)
    """
    # while True:
    print("\Password as:")
    print("1. Numbers only")
    print("2. Numbers and lowercase letters")
    print("3. Letters only")
    print("4. Numbers and letters")
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
    password = password()

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
            type_pwd = get_type()
            found_pwd = False
            print(f"\nAttempting to find password for '{ssid}'...")
            for pwd in password.generator(type_pwd, limit=3):
                connect, message = wifi.connect_to_wifi(ssid, pwd)
                if connect:
                    print(f"✓ Password found: {pwd}")
                    found_pwd = True
                    break
                elif connect == None:
                    print(message)
                    break
            if not found_pwd:
                print("Can not found any password!")

        elif choice == 4:
            print("Exiting the program. Goodbye!")
            break

        else:
            break
