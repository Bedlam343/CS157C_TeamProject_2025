curr_user = {}

def signup():
    print("\n=== Sign Up ===")
    
    name = input("Name: ")
    username = input("Choose a username: ")
    email = input("Email: ")
    password = input("Choose a password: ")

    # verify that unique username and email
    
    print("Signup successful! You can now log in.\n")
    return True

def login():
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")

    # verify credentials
    valid_credentials = False
    if valid_credentials:
        print("Login successful!\n")
        return True
    else:
        print("Invalid credentials. Please try again.\n")
        return False

def show_menu():
    print("\n=== Social Network App ===")
    print("1. Option A")
    print("2. Option B")
    print("3. Exit")

def main():
    authenticated = False

    while not authenticated:
        print("=== Social Network App ===")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            authenticated = login()
        elif choice == "2":
            signup()
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.\n")

    # Show main menu after successful login
    while True:
        show_menu()
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            break
        elif choice == "2":
            break
        elif choice == "3":
            print("Thank you, come again!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
