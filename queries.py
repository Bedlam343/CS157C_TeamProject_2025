from db_connection import get_driver
from neo4j import exceptions

# View Friends/Connections - A user can see a list of people they are following.
def get_following(tx, currentName): 
    """
    Handles the query and runs the transaction to return the nodes a user is following.
    """
    query = """MATCH (p:User {name: $currentName})-[:FOLLOWS]->(f:User) 
        RETURN f"""
    nodes = tx.run(query, currentName=currentName)
    return [node["f"]["name"] for node in nodes]

def execute_get_following(currentName):
    """
    Manages the DB session, executes the get_following() query, and stylizes the output.
    Call this function in other files to return a user's following.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followed = session.execute_read(get_following, currentName=currentName)
            print('\n\033[1m'"\033[4m" + "Your Following List:" + '\033[0m')
            if len(followed) == 0:
                print("You are currently not following any users.")
            else: 
                for user in followed:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# View Friends/Connections - A user can see a list of people who follow them.
def get_followers(tx, currentName):
    """
    Handles the query and runs the transaction to return the nodes that follow a user.
    """
    query = """MATCH (p:User {name: $currentName})<-[:FOLLOWS]-(f:User) 
        RETURN f"""
    nodes = tx.run(query, currentName=currentName)
    return [node["f"]["name"] for node in nodes]

def execute_get_followers(currentName):
    """
    Manages the DB session, executes the get_followers() query, and stylizes the output.
    Call this function in other files to return a user's followers.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followers = session.execute_read(get_followers, currentName=currentName)
            print('\n\033[1m'"\033[4m" + "Your Followers:" + '\033[0m')
            if len(followers) == 0:
                print("You currently have no users following you.")
            else:
                for user in followers:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# View Mutual Connections - A user can see mutual friends (users followed by both parties).
def get_mutuals(tx, currentName, friendName):
    """
        Handles the query and runs the transaction to return the nodes that both the 
        user and the specified friend follows.
    """
    query = """MATCH (p:User {name: $currentName})-[:FOLLOWS]->(f:User), (p2:User {name: $friendName})-[:FOLLOWS]->(f:User)
        RETURN f"""
    nodes = tx.run(query, name=currentName, friend=friendName)
    return [node["f"]["name"] for node in nodes]

def execute_get_mutuals(currentName, friendName):
    """
    Manages the DB session, executes the get_mutuals() query, and stylizes the output.
    Call this function in other files to return a user's mutuals friends with another user.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            mutuals = session.execute_read(get_mutuals, name=currentName, friend=friendName)
            print('\033[1m'"\033[4m" + "Your Mutual Friends:" + '\033[0m')
            if len(mutuals) == 0:
                print("You have no mutual friends with this user.")
            else:
                for user in mutuals:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# Follow Another User - A user can follow another user, creating a "FOLLOWS" relationship in Neo4j.
def follow(tx, currentName, targetName):
    query = """ 
    MATCH (u:User {name: $currentName})
    MATCH (u2:User {name: $targetName})
    MERGE (u)-[:FOLLOWS]->(u2)
    WHERE u.name <> u2.name
    RETURN u, u2
    """
    result = tx.run(query, currentUser=currentName, targetUser=targetName)
    return result

def execute_follow(currentName, targetName):
    try:
        driver = get_driver()
        with driver.session() as session:
            follow = session.execute_write(follow, currentName=currentName, targetName=targetName)
            print(f"You are now following {targetName}!")
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# Unfollow a User - A user can unfollow another user, removing the "FOLLOWS" relationship.
def unfollow(tx, currentName, targetName):
    query = """ 
    MATCH (u:User {name: $currentName})
    MATCH (u2:User {name: $targetName})
    MATCH (u)-[f:FOLLOWS]->(u2)
    DELETE f
    RETURN COUNT(f) AS deleted
    """
    result = tx.run(query, currentUser=currentName, targetUser=targetName)
    record = result.single()
    if record:
        return record["deleted"] > 0
    else:
        return False

def execute_unfollow(currentName, targetName):
    try:
        driver = get_driver()
        with driver.session() as session:
            unfollow = session.execute_write(unfollow, currentName=currentName, targetName=targetName)
            if unfollow:
                print(f"You unfollowed {targetName}!")
            else:
                print(f"You aren't following {targetName} yet.")
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