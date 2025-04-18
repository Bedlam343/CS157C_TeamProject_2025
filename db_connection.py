import dotenv
import os
from neo4j import GraphDatabase

#Load credentials from the txt file
load_status = dotenv.load_dotenv("Neo4j-59c90b3a-Created-2025-04-12.txt")
if load_status is False:
    raise RuntimeError("Environment variables not loaded")
else:
    print("Env variables loaded successfully!")

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

# Create the driver to connect to Neo4j
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    try:
        driver.verify_connectivity()
        print("Connection established")
    except Exception as e:
        print(f"Error verifying driver connection: {e}")

def get_driver():
    return driver