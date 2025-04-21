from db_connection import get_driver
from neo4j import exceptions
from social_network_app import get_current_name
from social_network_app import get_current_username

name = get_current_name()
username = get_current_username()

# View Friends/Connections - A user can see a list of people they are following.
def get_following(tx, name): 
    """
    Handles the query and runs the transaction to return the nodes a user is following.
    """
    query = """MATCH (p:User {name: $name})-[:FOLLOWS]->(f:User) 
        RETURN f"""
    nodes = tx.run(query, name=name)
    return [node["f"]["name"] for node in nodes]

def execute_get_following():
    """
    Manages the DB session, executes the get_following() query, and stylizes the output.
    Call this function in other files to return a user's following.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followed = session.execute_read(get_following, name=name)
            print('\033[1m'"\033[4m" + "Your Following List:" + '\033[0m')
            if len(followed) == 0:
                print("You are currently not following any users.")
            else: 
                for user in followed:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# # View Friends/Connections - A user can see a list of people who follow them.
def get_followers(tx, name):
    """
    Handles the query and runs the transaction to return the nodes that follow a user.
    """
    query = """MATCH (p:User {name: $name})<-[:FOLLOWS]-(f:User) 
        RETURN f"""
    nodes = tx.run(query, name=name)
    return [node["f"]["name"] for node in nodes]

def execute_get_followers():
    """
    Manages the DB session, executes the get_followers() query, and stylizes the output.
    Call this function in other files to return a user's followers.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            followers = session.execute_read(get_followers, name=name)
            print('\033[1m'"\033[4m" + "Your Followers:" + '\033[0m')
            if len(followers) == 0:
                print("You currently have no users following you.")
            else:
                for user in followers:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# View Mutual Connections - A user can see mutual friends (users followed by both parties).
def get_mutuals(tx, name, friend):
    """
        Handles the query and runs the transaction to return the nodes that both the 
        user and the specified friend follows.
    """
    query = """MATCH (p:User {name: $name})-[:FOLLOWS]->(f:User), (p2:User {name: $friend})-[:FOLLOWS]->(f:User)
        RETURN f"""
    nodes = tx.run(query, name=name, friend=friend)
    return [node["f"]["name"] for node in nodes]

def execute_get_mutuals():
    """
    Manages the DB session, executes the get_mutuals() query, and stylizes the output.
    Call this function in other files to return a user's mutuals friends with another user.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            mutuals = session.execute_read(get_mutuals, name=name, friend="Meryl Allison") # substitute for the user's/friend's name later
            # print(f"\033[1m\033[4mMutual Friends with {friend}:\033[0m")
            print('\033[1m'"\033[4m" + "Your Mutual Friends:" + '\033[0m')
            if len(mutuals) == 0:
                print("You have no mutual friends with this user.")
            else:
                for user in mutuals:
                    print(user)
        driver.close()
    except exceptions.Neo4jError as e:
        print(f"Neo4j Error: {e.message}")

# create user on sign up
def create_user(tx, name, username, email, password):
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
            createdAt: datetime()
        })
        RETURN {message: "User created successfully", user: newUser, success: true} AS result',
        'RETURN {message: "Email or username already exists", user: null, success: false} AS result',
        {name: $name, email: $email, username: $username, password: $password}
    ) YIELD value
    RETURN value.result AS result
    """
    
    result = tx.run(query, name=name, username=username, email=email, password=password)
    record = result.single()
    return record["result"]

def execute_create_user(name, username, email, password):
    params = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
    }

    for field in params:
        print(field, params[field], len(params[field]))
        if len(params[field]) == 0:
            return f"Error: {field} cannot be empty", None
    
    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.execute_write(create_user, name, username, email, password)
            return result["message"], result["user"]
    except exceptions.Neo4jError as e:
        return f"Neo4j Error: {e.message}", None