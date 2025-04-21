import os
import queries

curr_user = {}

def signup():
    print("\n=== Sign Up ===")
    
    name = input("Name: ")
    username = input("Choose a username: ")
    email = input("Email: ")
    password = input("Choose a password: ")

    message, user = queries.execute_create_user(name, username, email, password)
    print('\n', message)

    if user is not None:
        curr_user["name"] = name
        curr_user["username"] = username
        curr_user["email"] = email
        return True

    return False

def login():
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")

    curr_user['username'] = username
    curr_user['password'] = password

    return False

def get_current_name():
    return curr_user['name']

def get_current_username():
    return curr_user['username']

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
    os.system("cls")
    global curr_user
    authenticated = False

    while not authenticated:
        print("\n=== Social Network App ===\n")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            authenticated = login()
        elif choice == "2":
            authenticated = signup()
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.\n")

    # Show main menu after successful login
    while True:
        os.system("cls")
        print("\n=== Social Network App ===\n")

        print(f"Welcome, {curr_user['name']}!\n")

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
