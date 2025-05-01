import os
import sys
import queries

curr_user = {}



def signup():
    print("\n=== Sign Up ===")
    new_user = {}
    
    new_user["name"] = input("Name: ")
    new_user["username"] = input("Choose a username: ")
    new_user["email"] = input("Email: ")
    new_user["password"] = input("Choose a password: ")
    new_user["bio"] = input("Add a bio (optional): ")
    new_user["location"] = input("Add a location (optional): ")    

    message, res_user = queries.execute_create_user(new_user)
    print('\n', message)

    if res_user is not None:
        curr_user["name"] = new_user["name"]
        curr_user["username"] = new_user["username"]
        curr_user["email"] = new_user["email"]
        return True

    return False

def login():
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")

    message, u = queries.execute_login(username, password)
    print('\n', message)

    if u is not None:
        curr_user['name'] = u['name']
        curr_user['username'] = u['username']
        curr_user['email'] = u['email']
        return True

    return False

def show_menu():
    print("\033[1m" + "User Management" + "\033[0m")
    print("1. View Profile")
    print("2. Edit Profile")

    print("\n\033[1m" + "Social Graph" + "\033[0m")
    print("3. Follow a User")
    print("4. Unfollow a User")
    print("5. View Friends/Connections")
    print("6. Mutual Connections")
    print("7. Friend Recommendations")

    print("\n\033[1m" + "Search & Exploration" + "\033[0m")
    print("8. Search Users")
    print("9. Explore Popular Users")

    print("\n10. Exit")

def main():
    os.system("cls")
    global curr_user
    authenticated = False

    while not authenticated:
        print('\033[1m'"\033[4m" + "=== Social Network App ===" + '\033[0m\n')
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
        print('\n\033[1m'"\033[4m" + "=== Social Network App ===" + '\033[0m\n')

        print(f"Welcome, {curr_user['name']}!\n")

        show_menu()

        choice = input("Choose an option (1-10): ")

        if choice == "1":
            pass
        elif choice == "2":
            pass
        elif choice == "3":
            target_username = input("Enter the username of the user you'd like to follow: ")
            queries.execute_follow(currentName=curr_user["name"], targetUsername=target_username)
        elif choice == "4":
            target_username = input("Enter the username of the user you'd like to unfollow: ")
            queries.execute_unfollow(currentName=curr_user["name"], targetUsername=target_username)
        elif choice == "5":
            queries.execute_get_followers(username=curr_user["username"])
            queries.execute_get_following(username=curr_user["username"])
        elif choice == "6":
            target_username = input("Enter your friend's username to see mutuals: ")
            queries.execute_get_mutuals(currentName=curr_user["name"], friendUsername=target_username)
        elif choice == "8":
            target = input("Search users by name or username: ")
            queries.execute_search_users(target=target)
        elif choice == "10":
            print("Thank you, come again!")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
