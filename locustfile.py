from locust import User, task, between
from neo4j import GraphDatabase
import os
import random


class BoltUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password")),
        )
        self.session = self.driver.session()
        self.cypher_queries = [
            "MATCH (n) RETURN count(n)",
            "MATCH (u:User)-[:LIKES]->(m:Movie) RETURN u.name, m.title LIMIT 10",
            "MATCH (p:Product) WHERE p.price > 100 RETURN p.name, p.price LIMIT 20",
            "MATCH ()-[r:RELATED_TO]->() RETURN type(r) LIMIT 30",
        ]

    def on_stop(self):
        self.session.close()
        self.driver.close()

    @task
    def run_random_query(self):
        query = random.choice(self.cypher_queries)
        try:
            self.session.run(query).consume()
        except Exception as e:
            print(f"Query failed: {query}\nError: {e}")
