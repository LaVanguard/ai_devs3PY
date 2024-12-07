import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from messenger import verify_task, db_query

load_dotenv()

URI = os.getenv("aidevs.neo4j.uri")
AUTH = (os.getenv("aidevs.neo4j.username"), os.getenv("aidevs.neo4j.password"))


def create_graph_users(users_data):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            for user in users_data:
                user_id = user.get("id")
                user_name = user.get("username")
                if user_id and user_name:
                    result = session.run(
                        "CREATE (u:User {user_id: $user_id, user_name: $user_name})",
                        user_id=user_id, user_name=user_name
                    )
    print("Users created in the graph database.")


def create_graph_connections(connections_data):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            for connection in connections_data:
                user1_id = connection.get("user1_id")
                user2_id = connection.get("user2_id")
                if user1_id and user2_id:
                    session.run(
                        """
                        MATCH (u1:User {user_id: $user1_id}), (u2:User {user_id: $user2_id})
                        CREATE (u1)-[:CONNECTED_TO]->(u2)
                        """,
                        user1_id=user1_id, user2_id=user2_id
                    )
    print("Connections created in the graph database.")


def get_user_ids_connecting_rafal_and_barbara():
    URI = os.getenv("aidevs.neo4j.uri")
    AUTH = (os.getenv("aidevs.neo4j.username"), os.getenv("aidevs.neo4j.password"))

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            result = session.run(
                """
                MATCH p = shortestPath((u1:User {user_name: 'Rafał'})-[:CONNECTED_TO*]-(u2:User {user_name: 'Barbara'}))
                RETURN [user IN nodes(p) | user.user_name] AS user_names
                """
            )
            user_names = result.single()["user_names"]
            return ",".join(map(str, user_names))


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

api_url = os.getenv("aidevs.apidb.url")

response = db_query(api_url, "select * from users")
response_data = response.json()['reply']
create_graph_users(response_data)

response = db_query(api_url, "select * from connections")
response_data = response.json()['reply']
create_graph_connections(response_data)
print(response_data)

answer = get_user_ids_connecting_rafal_and_barbara()
print(answer)
response_data = verify_task("connections", answer)
print(response_data)
