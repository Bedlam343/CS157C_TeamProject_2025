from db_connection import get_driver
from neo4j import exceptions
import helpers

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
            print(helpers.bold_underline("\nYour Mutual Friends:"))

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
    query = """ 
    MATCH (u:User {username: $currentUsername})
    OPTIONAL MATCH (u2:User {username: $targetUsername})
    WITH u, u2 WHERE u.username <> u2.username
    MERGE (u)-[:FOLLOWS]->(u2)
    RETURN u, u2
    """
    result = tx.run(query, currentUsername=currentUsername, targetUsername=targetUsername)
    record = result.single()
    if record and record["u2"]:
        return record["u2"]["username"]
    else:
        return None

# TODO: What if already following targetUsername?
def execute_follow(currentUsername, targetUsername):
    try:
        driver = get_driver()
        with driver.session() as session:
            follow_result = session.execute_write(follow, currentUsername=currentUsername, targetUsername=targetUsername)
            if follow_result is None or len(follow_result) == 0:
                helpers.print_error("The user doesn't exist in the system. Please try again.")
            else:
                helpers.print_success(f"You are now following {targetUsername}!")
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
                helpers.print_success(f"You unfollowed {targetUsername}!")
            else:
                helpers.print_error(f"Error: You don't follow {targetUsername}")
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
            print(f"\n{helpers.bold_underline(f'Results for {target}: ')}")

            if len(users) == 0:
                print("No users matched your search")
            else:
                for user in users:
                    output = f"{helpers.blue_text('Name')}: {user['name']} - {helpers.blue_text('Username')}: {user['username']}"
                    if len(user["bio"]) > 0:
                        output += f" - {helpers.blue_text('Bio')}: {user['bio']}"
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
        helpers.print_success("\nUsername updated successfully!")
        return True
    else:
        helpers.print_error("\nError: Username already taken!")
        return False

def execute_update_username(current_email, new_username):
    if len(new_username) == 0:
        helpers.print_error("Error: Username cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_username, current_email, new_username)
            return success
    except exceptions.Neo4jError as e:
        helpers.print_error(f"Neo4j Error: {e.message}")
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
        helpers.print_success("\nName updated successfully!")
        return True
    else:
        helpers.print_error("\nAn error occurred")
        return False

def execute_update_name(current_email, new_name):
    if len(new_name) == 0:
        helpers.print_error("Error: Name cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_name, current_email, new_name)
            return success
    except exceptions.Neo4jError as e:
        helpers.print_error(f"Neo4j Error: {e.message}")
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
        helpers.print_success("\nPassword updated successfully!")
        return True
    else:
        helpers.print_error("\nAn error occurred")
        return False

def execute_update_password(current_email, new_password):
    if len(new_password) == 0:
        helpers.print_error("Error: Password cannot be empty!")
        return False
    
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_password, current_email, new_password)
            return success
    except exceptions.Neo4jError as e:
        helpers.print_error(f"Neo4j Error: {e.message}")
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
        helpers.print_success("\nBio updated successfully!")
        return True
    else:
        helpers.print_error("\nAn error occurred")
        return False
def execute_update_bio(current_email, new_bio):
    try:
        driver = get_driver()
        with driver.session() as session:
            success = session.execute_write(update_bio, current_email, new_bio)
            return success
    except exceptions.Neo4jError as e:
        helpers.print_error(f"Neo4j Error: {e.message}")
        return False