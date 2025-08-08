from locust import User, task, between
from neo4j import GraphDatabase
import os
import random
import time


class BoltUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost")
        self.driver = GraphDatabase.driver(
            f"bolt://{neo4j_uri}:7687",
            auth=(os.getenv("neo4j_username", "neo4j"), os.getenv("neo4j_password", "password")),
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
        start_time = time.time()
        try:
            self.session.run(query).consume()
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="Cypher",  # 자유롭게 정의 가능
                name=query.split()[0],  # 예: MATCH
                response_time=total_time,
                response_length=0,
                exception=None,
                context={},
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="Cypher",
                name="FAILED",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={},
            )
