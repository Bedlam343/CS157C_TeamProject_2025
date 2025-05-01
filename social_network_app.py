import os
import sys
import queries
from helpers import blue_text, bold_text, bold_underline, print_error

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
        curr_user["bio"] = new_user["bio"]
        curr_user["location"] = new_user["location"]
        curr_user["password"] = new_user["password"]
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
        curr_user["bio"] = u["bio"]
        curr_user["location"] = u["location"]
        curr_user["password"] = u["password"]
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

def show_edit_user_menu():
    print(bold_underline("Editing User:"))
    print(f"1. Edit Name ({blue_text(curr_user['name'])})")
    print(f"2. Edit Username ({blue_text(curr_user['username'])})")
    print(f"3. Edit Password ({blue_text(curr_user['password'])})")
    print(f"4. Edit Bio ({blue_text(curr_user['bio'])})")
    print(f"5. Edit Location ({blue_text(curr_user['location'])})")
    print("\n6. Main Menu")

def main():
    os.system("cls")
    global curr_user
    authenticated = False

    while not authenticated:
        print(f"\n{bold_underline('=== Social Network App ===')}\n")
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
            print_error("\nInvalid choice. Please try again.\n")

    # Show main menu after successful login
    while True:
        os.system("cls")
        print(f"\n{bold_underline('=== Social Network App ===')}\n")

        print(f"Welcome, {curr_user['name']}!\n")

        show_menu()

        choice = input("Choose an option (1-10): ")

        if choice == "1":
           pass
            
        elif choice == "2":
            # edit user profile
            while True:
                os.system("cls")
                show_edit_user_menu()
                edit_choice = input(f"\n{bold_text('Choose action (1-6): ')}")

                if edit_choice == "1":
                    # edit name
                    print("\n" + blue_text("Current Name: ") + curr_user["name"])
                    new_name = input(bold_text("Enter new name: "))

                    success = queries.execute_update_name(curr_user["email"], new_name)

                    # update name locally if update successful
                    if success:
                        curr_user['name'] = new_name

                elif edit_choice == "2":
                    # edit username
                    print("\n" + blue_text("Current Username: ") + curr_user["username"])
                    new_username = input(bold_text("Enter new username: "))

                    success = queries.execute_update_username(curr_user["email"], new_username)

                    # update username locally if update successful
                    if success:
                        curr_user['username'] = new_username

                elif edit_choice == "3":
                    # change password
                    print("\n" + blue_text("Current Password: ") + curr_user["password"])
                    new_password = input(bold_text("Enter new password: "))

                    success = queries.execute_update_password(curr_user["email"], new_password)

                    # update password locally if update successful
                    if success:
                        curr_user['password'] = new_password
                
                elif edit_choice == "4":
                    # edit bio
                    print("\n" + blue_text("Current Bio: ") + curr_user["bio"])
                    new_bio = input(bold_text("Enter new bio: "))

                    success = queries.execute_update_bio(curr_user["email"], new_bio)

                    # update bio locally if update successful
                    if success:
                        curr_user['bio'] = new_bio

                elif edit_choice == "5":
                    # edit location
                    print("\n" + blue_text("Current Location: ") + curr_user["location"])
                    new_location = input(bold_text("Enter new location: "))

                    success = queries.execute_update_location(curr_user["email"], new_location)

                    # update location locally if update successful
                    if success:
                        curr_user['location'] = new_location
                    
                elif edit_choice == "6":
                    break
                else:
                    print_error("\nInvalid choice! Please try again...")
                
                input("\nPress Enter to continue...")
        elif choice == "3":
            # follow another user
            target_username = input(bold_text("\nEnter the username of the user you'd like to follow: "))
            if len(target_username) == 0:
                print_error("Error: Username cannot be empty!")
            else:
                queries.execute_follow(currentUsername=curr_user["username"], targetUsername=target_username)

        elif choice == "4":
            # unfollow another user
            target_username = input(bold_text("\nEnter the username of the user you'd like to unfollow: "))
            if len(target_username) == 0:
                print_error("Username cannot be empty!")
            else:
                queries.execute_unfollow(currentUsername=curr_user["username"], targetUsername=target_username)

        elif choice == "5":
            # get following anf followers
            queries.execute_get_followers(username=curr_user["username"])
            queries.execute_get_following(username=curr_user["username"])

        elif choice == "6":
            # see mutuals with a connection
            target_username = input("\n" + bold_text("Enter your friend's username to see mutuals: "))
            if len(target_username) == 0:
                 print_error("Username cannot be empty!")
            else:
                queries.execute_get_mutuals(currentUsername=curr_user["username"], friendUsername=target_username)

        elif choice == "7":
            # friend recommendations
            pass

        elif choice == "8":
            # search users
            target = input("\n" + bold_text("Search users by name or username: "))
            if len(target) == 0:
                print_error("\nInput cannot be empty!")
            else:
                queries.execute_search_users(target=target) 

        elif choice == "9":
            # explore popular users
            pass

        elif choice == "10":
            print("Thank you, come again!")
            break

        else:
            print_error("\nInvalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
