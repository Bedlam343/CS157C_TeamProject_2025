from db_connection import get_driver

# View Friends/Connections - A user can see a list of people they are following.
def get_following(tx, name): 
    """
    Handles the query and runs the transaction to return the nodes a user is following.
    """
    query = """MATCH (p:Person {name: $name})-[:FOLLOWS]->(f:Person) 
        RETURN f"""
    nodes = tx.run(query, name=name)
    return [node["f"]["name"] for node in nodes]

def execute_get_following_():
    """
    Manages the DB session, executes the get_following() query, and stylizes the output.
    Call this function in other files to return a user's following.
    """
    driver = get_driver()
    with driver.session() as session:
        followed = session.execute_read(get_following, name="Rachel Lally") # substitute for the user's name later
        print('\033[1m'"\033[4m" + "Your Following List:" + '\033[0m')
        for person in followed:
            print(person)

# # View Friends/Connections - A user can see a list of people who follow them.
def get_followers(tx, name):
    """
    Handles the query and runs the transaction to return the nodes that follow a user.
    """
    query = """MATCH (p:Person {name: $name})<-[:FOLLOWS]-(f:Person) 
        RETURN f"""
    nodes = tx.run(query, name=name)
    return [node["f"]["name"] for node in nodes]

def execute_get_followers():
    """
    Manages the DB session, executes the get_followers() query, and stylizes the output.
    Call this function in other files to return a user's followers.
    """
    driver = get_driver()
    with driver.session() as session:
        followers = session.execute_read(get_followers, name="Ganesh Bisht") # substitute for the user's name later
        print('\033[1m'"\033[4m" + "Your Followers:" + '\033[0m')
        for person in followers:
            print(person)

# # Mutual Connections - A user can see mutual friends (users followed by both parties).
# # def get_mutuals(friend):