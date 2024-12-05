from neo4j import GraphDatabase
import os

def test_neo4j_connection():
    # Get credentials from environment variables
    NEO4J_AUTH = os.environ.get('NEO4J_AUTH')
    if not NEO4J_AUTH:
        raise ValueError("NEO4J_AUTH environment variable not set")
    
    NEO4J_USERNAME, NEO4J_PASSWORD = NEO4J_AUTH.split('/')
    NEO4J_URI = os.environ.get('NEO4J_URI', "neo4j://neo4j:7687")
    
    try:
        # Create a driver instance
        driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        # Verify connectivity
        with driver.session() as session:
            # Simple query to verify connection
            result = session.run("RETURN 1 AS num")
            record = result.single()
            print(f"Successfully connected to Neo4j! Test query result: {record['num']}")
            
            # Optional: Create a test node
            session.run(
                "CREATE (n:TestNode {message: $message}) RETURN n",
                message="Hello from Python!"
            )
            print("Created test node successfully")
            
    except Exception as e:
        print(f"Failed to connect to Neo4j: {str(e)}")
        raise
    finally:
        # Always close the driver
        if 'driver' in locals():
            driver.close()

if __name__ == "__main__":
    test_neo4j_connection() 