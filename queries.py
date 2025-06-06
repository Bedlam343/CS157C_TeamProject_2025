from db_connection import get_driver
from neo4j import exceptions
from helpers import blue_text, orange_text, bold_underline, print_error, print_success

# View Profile - A user can view their own profile information
def get_profile(tx, username):
    """
    Handles the query and runs the transaction to return a user's profile information.
    """
    query = """MATCH (u:User {username: $username}) 
        RETURN u"""
    result = tx.run(query, username=username)
    record = result.single()
    return record["u"] if record else None

def execute_get_profile(username):
    """
    Manages the DB session, executes the get_profile() query, and stylizes the output.
    Call this function in other files to display a user's profile information.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            profile = session.execute_read(get_profile, username=username)
            if profile:
                print(f"\n{bold_underline('Profile Information:')}") 
                print(f"{blue_text('Name')}: {profile['name']}")
                print(f"{blue_text('Username')}: {profile['username']}")
                print(f"{blue_text('Email')}: {profile['email']}")
                if 'bio' in profile and profile['bio']:
                    print(f"{blue_text('Bio')}: {profile['bio']}")
                if 'location' in profile and profile['location']:
                    print(f"{blue_text('Location')}: {profile['location']}")
                return profile
            else:
                print_error(f"User with username '{username}' not found.")
                return None
        driver.close()
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return None

# View Friends/Connections - A user can see a list of people they are following.
def get_following(tx, username): 
    """
    Handles the query and runs the transaction to return the nodes a user is following.
    """
    query = """MATCH (p:User {username: $username})-[:FOLLOWS]->(f:User) 
        RETURN f"""
    nodes = tx.run(query, username=username)
    return [node["f"] for node in nodes]

def execute_get_following(username):
    """
    Manages the DB session, executes the get_following() query, and stylizes the output.
    Call this function in other files to return a user's following.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followed = session.execute_read(get_following, username=username)
            print('\n\033[1m'"\033[4m" + "Your Following List:" + '\033[0m')
            if len(followed) == 0:
                print("You are currently not following any users.")
            else: 
                for user in followed:
                    print(f"{user['name']} - {user['username']}")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# View Friends/Connections - A user can see a list of people who follow them.
def get_followers(tx, username):
    """
    Handles the query and runs the transaction to return the nodes that follow a user.
    """
    query = """MATCH (p:User {username: $username})<-[:FOLLOWS]-(f:User) 
        RETURN f"""
    nodes = tx.run(query, username=username)
    return [node["f"] for node in nodes]

def execute_get_followers(username):
    """
    Manages the DB session, executes the get_followers() query, and stylizes the output.
    Call this function in other files to return a user's followers.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followers = session.execute_read(get_followers, username=username)
            print('\n\033[1m'"\033[4m" + "Your Followers:" + '\033[0m')
            if len(followers) == 0:
                print("You currently have no users following you.")
            else:
                for user in followers:
                    print(f"{user['name']} - {user['username']}")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# View Mutual Connections - A user can see mutual friends (users followed by both parties).
def get_mutuals(tx, currentUsername, friendUsername):
    """
        Handles the query and runs the transaction to return the nodes that both the 
        user and the specified friend follows.
    """
    query = """
        MATCH (p:User {username: $currentUsername})-[:FOLLOWS]->(f:User), (p2:User {username: $friendUsername})-[:FOLLOWS]->(f:User)
        RETURN f
    """
    nodes = tx.run(query, currentUsername=currentUsername, friendUsername=friendUsername)
    return [node["f"] for node in nodes]

def execute_get_mutuals(currentUsername, friendUsername):
    """
    Manages the DB session, executes the get_mutuals() query, and stylizes the output.
    Call this function in other files to return a user's mutuals friends with another user.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            mutuals = session.execute_read(get_mutuals, currentUsername=currentUsername, friendUsername=friendUsername)
            print(bold_underline("\nYour Mutual Friends:"))

            if len(mutuals) == 0:
                print("\nYou have no mutual friends with this user.")
            else:
                for user in mutuals:
                    print(f"{user['name']} - {user['username']}")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# Follow Another User - A user can follow another user, creating a "FOLLOWS" relationship in Neo4j.
def follow(tx, currentUsername, targetUsername):
    check_query = """ 
    MATCH (u:User {username: $currentUsername})
    OPTIONAL MATCH (u2:User {username: $targetUsername})
    OPTIONAL MATCH (u)-[r:FOLLOWS]->(u2)
    WITH u, u2, r WHERE u.username <> u2.username
    RETURN u2, r IS NOT NULL as alreadyFollowed
    """
    result = tx.run(check_query, currentUsername=currentUsername, targetUsername=targetUsername)
    record = result.single()
    if not record or not record["u2"]:
        return None
    elif record["alreadyFollowed"]:
        return "alreadyFollowed"
    else:
        follow_query = """
        MATCH (u:User {username: $currentUsername})
        OPTIONAL MATCH (u2:User {username: $targetUsername})
        WITH u, u2 WHERE u.username <> u2.username
        MERGE (u)-[:FOLLOWS]->(u2)
        RETURN u, u2
        """
        result = tx.run(follow_query, currentUsername=currentUsername, targetUsername=targetUsername)
        record = result.single()
        return record["u2"]["username"]

def execute_follow(currentUsername, targetUsername):
    try:
        driver = get_driver()
        with driver.session() as session:
            follow_result = session.execute_write(follow, currentUsername=currentUsername, targetUsername=targetUsername)
            if follow_result is None or len(follow_result) == 0:
                print_error("The user doesn't exist in the system. Please try again.")
            elif follow_result == "alreadyFollowed":
                print_error("You are already following this user.")
            else:
                print_success(f"You are now following {targetUsername}!")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# Unfollow a User - A user can unfollow another user, removing the "FOLLOWS" relationship.
def unfollow(tx, currentUsername, targetUsername):
    query = """ 
    MATCH (u:User {username: $currentUsername})
    MATCH (u2:User {username: $targetUsername})
    MATCH (u)-[f:FOLLOWS]->(u2)
    DELETE f
    RETURN COUNT(f) AS deleted
    """
    result = tx.run(query, currentUsername=currentUsername, targetUsername=targetUsername)
    record = result.single()
    if record:
        return record["deleted"] > 0
    else:
        return False

def execute_unfollow(currentUsername, targetUsername):
    try:
        driver = get_driver()
        with driver.session() as session:
            unfollow_result = session.execute_write(unfollow, currentUsername=currentUsername, targetUsername=targetUsername)
            if unfollow_result:
                print_success(f"You unfollowed {targetUsername}!")
            else:
                print_error(f"Error: You don't follow {targetUsername}")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# Search Users - A user can search for other users by name or username. The system returns a list of matching users.
def search_users(tx, target):
    query = """
    MATCH (u:User) WHERE u.name = $target OR u.username = $target
    RETURN u
    """
    result = tx.run(query, target=target)
    return [node["u"] for node in result]

def execute_search_users(target):
    try:
        driver = get_driver()
        with driver.session() as session:
            users = session.execute_read(search_users, target=target)
            print(f"\n{bold_underline(f'Results for {target}: ')}")

            if len(users) == 0:
                print("No users matched your search")
            else:
                for user in users:
                    output = f"{blue_text('Name')}: {user['name']} - {blue_text('Username')}: {user['username']}"
                    if len(user["bio"]) > 0:
                        output += f" - {blue_text('Bio')}: {user['bio']}"
                    print(output)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# create user on sign up
def create_user(tx, new_user):
    query = """
     MATCH (u:User)
    WHERE u.email = $email OR u.username = $username
    WITH count(u) AS existingCount
    CALL apoc.do.when(
        existingCount = 0,
        'CREATE (newUser:User {
            name: $name, 
            email: $email, 
            username: $username, 
            password: $password,
            bio: $bio,
            location: $location,
            createdAt: datetime()
        })
        RETURN {message: "User created successfully", user: newUser, success: true} AS result',
        'RETURN {message: "Email or username already exists", user: null, success: false} AS result',
        {name: $name, email: $email, username: $username, password: $password, bio: $bio, location: $location}
    ) YIELD value
    RETURN value.result AS result
    """
    
    result = tx.run(query, name=new_user["name"], username=new_user["username"], email=new_user["email"], password=new_user["password"], bio=new_user["bio"], location=new_user["location"])
    record = result.single()
    return record["result"]

def execute_create_user(new_user):
    required_fields = ["name", "username", "email", "password"]

    for field in required_fields:
        if len(new_user[field]) == 0:
            return f"Error: {field} cannot be empty", None
    
    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.execute_write(create_user, new_user)
            driver.close()
            return result["message"], result["user"]
    except exceptions.Neo4jError as e:
        return f"Neo4j Error: {e.message}", None
    
def login(tx, username, password):
    query = """
    MATCH (u:User {username: $username})
    WHERE u.password = $password
    RETURN 
        CASE 
            WHEN u IS NOT NULL THEN 
                {message: "Login successful", user: u, success: true}
            ELSE 
                {message: "Invalid username or password", user: null, success: false}
        END AS result
    """

    result = tx.run(query, username=username, password=password)
    record = result.single()
    if record and record['result']:
        return record['result']
    else:
        return { "message": "Invalid username or password", "user": None }

def execute_login(username, password):
    if len(username) == 0 or len(password) == 0:
        return f"Error: username or password cannot be empty", None
    
    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.execute_read(login, username, password)
            driver.close()
            return result["message"], result["user"]
    except exceptions.Neo4jError as e:
        return f"Neo4j Error: {e.message}", None
    

def update_username(tx, current_email, new_username):
    query = """
    OPTIONAL MATCH (existing:User {username: $new_username})
    WITH existing
    WHERE existing IS NULL
    MATCH (u:User {email: $current_email})
    SET u.username = $new_username
    RETURN u
    """

    result = tx.run(query, current_email=current_email, new_username=new_username)
    record = result.single()

    if record and record["u"]:
        print_success("\nUsername updated successfully!")
        return True
    else:
        print_error("\nError: Username already taken!")
        return False

def execute_update_username(current_email, new_username):
    if len(new_username) == 0:
        print_error("Error: Username cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_username, current_email, new_username)
            driver.close()
            return success
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return False
    

def update_name(tx, current_email, new_name):
    query = """
    MATCH (u:User {email: $current_email})
    SET u.name = $new_name
    RETURN u
    """

    result = tx.run(query, current_email=current_email, new_name=new_name)
    record = result.single()

    if record and record["u"]:
        print_success("\nName updated successfully!")
        return True
    else:
        print_error("\nAn error occurred")
        return False

def execute_update_name(current_email, new_name):
    if len(new_name) == 0:
        print_error("Error: Name cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_name, current_email, new_name)
            driver.close()
            return success
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return False
    

def update_password(tx, current_email, new_password):
    query = """
    MATCH (u:User {email: $current_email})
    SET u.password = $new_password
    RETURN u
    """

    result = tx.run(query, current_email=current_email, new_password=new_password)
    record = result.single()

    if record and record["u"]:
        print_success("\nPassword updated successfully!")
        return True
    else:
        print_error("\nAn error occurred")
        return False

def execute_update_password(current_email, new_password):
    if len(new_password) == 0:
        print_error("Error: Password cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_password, current_email, new_password)
            driver.close()
            return success
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return False
    
def update_bio(tx, current_email, new_bio):
    query = """
    MATCH (u:User {email: $current_email})
    SET u.bio = $new_bio
    RETURN u
    """

    result = tx.run(query, current_email=current_email, new_bio=new_bio)
    record = result.single()

    if record and record["u"]:
        print_success("\nBio updated successfully!")
        return True
    else:
        print_error("\nAn error occurred")
        return False
def execute_update_bio(current_email, new_bio):
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_bio, current_email, new_bio)
            driver.close()
            return success
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return False
    
def update_location(tx, current_email, new_location):
    query = """
    MATCH (u:User {email: $current_email})
    SET u.location = $new_location
    RETURN u
    """

    result = tx.run(query, current_email=current_email, new_location=new_location)
    record = result.single()

    if record and record["u"]:
        print_success("\nLocation updated successfully!")
        return True
    else:
        print_error("\nAn error occurred")
        return False
def execute_update_location(current_email, new_location):
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_location, current_email, new_location)
            driver.close()
            return success
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return False
    
def get_recommendations(tx, current_username):
    query = """
    MATCH (me:User {username: $current_username})-[:FOLLOWS]-(friend)-[:FOLLOWS]-(suggestion:User)
    WHERE NOT (me)-[:FOLLOWS]-(suggestion)
    AND me <> suggestion
    RETURN DISTINCT suggestion, count(friend) AS mutualConnections
    ORDER BY mutualConnections DESC
    LIMIT 10
    """

    result = tx.run(query, current_username=current_username)
    return [node["suggestion"] for node in result]

def execute_get_recommendations(current_username):
    if len(current_username) == 0:
        print_error("Username cannot be empty!")
        return
    
    try:
        driver = get_driver()
        with driver.session() as session:
            recommendations = session.execute_read(get_recommendations, current_username)

            print(f"\n{bold_underline(f'Recommendations: ')}")

            if len(recommendations) == 0:
                print("No recommendations found.")
            else:
                for user in recommendations:
                    output = f"{blue_text('Name')}: {user['name']} - {blue_text('Username')}: {user['username']}"
                    if len(user["bio"]) > 0:
                        output += f" - {blue_text('Bio')}: {user['bio']}"
                    print(output)
        driver.close()
    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return
    
def get_most_followed(tx):
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
    RETURN u {.*, password: null, id: null} AS user, count(follower) AS followersCount
    ORDER BY followersCount DESC
    LIMIT 10
    """

    result = tx.run(query)
    return [{ "user": node["user"], "num_followers": node["followersCount"] } for node in result]

def execute_get_most_followed():
    try:
        driver = get_driver()
        with driver.session() as session:
            most_followed = session.execute_read(get_most_followed)
            
            print(f"\n{bold_underline(f'Top 10 most followed users: ')}")

            if len(most_followed) == 0:
                 print("No users found.")
            else:
                count = 1
                for item in most_followed:
                    user = item['user']
                    num_followers = item['num_followers']
                    output = ''
                    i = 0
                   
                    print(orange_text(f"{count}. {num_followers} followers"))

                    for key in user:
                        if user[key] is not None:
                            if i > 0:
                                output += " - "
                            output += f"{blue_text(key)}: {user[key]}"
                            i += 1

                    print(output)
                    print()
                    count += 1

            driver.close()

    except exceptions.Neo4jError as e:
        print_error(f"Neo4j Error: {e.message}")
        return