import os

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

    curr_user['username'] = username
    curr_user['password'] = password

    return True

    # verify credentials
    valid_credentials = False
    if valid_credentials:
        print("Login successful!\n")
        return True
    else:
        print("Invalid credentials. Please try again.\n")
        return False

def show_menu():
    print("User Management")
    print("1. View Profile")
    print("2. Edit Profile")

    print("\nSocial Graph")
    print("3. Follow a User")
    print("4. Unfollow a User")
    print("5. View Friends/Connections")
    print("6. Mutual Connections")
    print("7. Friend Recommendations")

    print("\nSearch & Exploration")
    print("8. Search Users")
    print("9. Explore Popular Users")

    print("\n10. Exit")

def main():

    authenticated = False

    while not authenticated:
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
        os.system("cls")
        print("\n=== Social Network App ===\n")
        show_menu()

        choice = input("Choose an option (1-10): ")

        if choice == "1":
            pass
        elif choice == "2":
            pass
        elif choice == "10":
            print("Thank you, come again!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
