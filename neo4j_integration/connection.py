from neo4j import GraphDatabase
from django.conf import settings

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        if self.driver is not None:
            self.driver.close()
    
    def query(self, query, parameters=None, db=None):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Singleton instance
neo4j_db = Neo4jConnection()
