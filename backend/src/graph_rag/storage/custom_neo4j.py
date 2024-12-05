from typing import Dict, List, Optional, Set, Tuple, Any
from neo4j import GraphDatabase
from lightrag.base import BaseGraphStorage
import os

class CustomNeo4JStorage(BaseGraphStorage):
    def __init__(self, namespace: str, global_config: dict, **kwargs):
        super().__init__(namespace, global_config)
        # Initialize Neo4j connection
        self.uri = os.environ.get('NEO4J_URI', "neo4j://neo4j:7687")
        self.username = os.environ.get('NEO4J_USERNAME', "neo4j")
        self.password = os.environ.get('NEO4J_PASSWORD', "atleast8chars")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    async def upsert_node(self, node_id: str, node_data: Dict[str, Any] = None) -> None:
        """Create or update a node with properties"""
        with self.driver.session() as session:
            # Convert node_data to string properties
            properties = {k: str(v) if not isinstance(v, (int, float, bool)) else v 
                         for k, v in (node_data or {}).items()}
            properties['id'] = node_id  # Ensure ID is set in properties
            
            query = (
                "MERGE (n:Node {id: $node_id}) "
                "SET n += $properties "
                "RETURN n"
            )
            session.run(query, node_id=node_id, properties=properties)

    async def upsert_edge(self, src_id: str, tgt_id: str, edge_data: Dict[str, Any] = None) -> None:
        """Create or update an edge between nodes with properties"""
        with self.driver.session() as session:
            # Convert edge_data to string properties
            properties = {k: str(v) if not isinstance(v, (int, float, bool)) else v 
                         for k, v in (edge_data or {}).items()}
            
            query = (
                "MERGE (src:Node {id: $src_id}) "
                "MERGE (tgt:Node {id: $tgt_id}) "
                "MERGE (src)-[r:RELATES_TO]->(tgt) "
                "SET r += $properties "
                "RETURN r"
            )
            session.run(query, src_id=src_id, tgt_id=tgt_id, properties=properties)

    async def delete_node(self, node_id: str) -> None:
        with self.driver.session() as session:
            query = "MATCH (n:Node {id: $node_id}) DETACH DELETE n"
            session.run(query, node_id=node_id)

    async def delete_edge(self, src_id: str, tgt_id: str) -> None:
        with self.driver.session() as session:
            query = (
                "MATCH (src:Node {id: $src_id})-[r:RELATES_TO]->(tgt:Node {id: $tgt_id}) "
                "DELETE r"
            )
            session.run(query, src_id=src_id, tgt_id=tgt_id)

    async def get_node_neighbors(
        self, node_id: str, edge_type: Optional[str] = None
    ) -> Set[str]:
        with self.driver.session() as session:
            query = (
                "MATCH (n:Node {id: $node_id})-[:RELATES_TO]-(neighbor) "
                "RETURN collect(neighbor.id) as neighbors"
            )
            result = session.run(query, node_id=node_id)
            record = result.single()
            return set(record["neighbors"] if record else [])

    async def get_node_data(self, node_id: str) -> Optional[Dict[str, Any]]:
        with self.driver.session() as session:
            query = "MATCH (n:Node {id: $node_id}) RETURN properties(n) as props"
            result = session.run(query, node_id=node_id)
            record = result.single()
            return record["props"] if record else None

    async def get_edge_data(
        self, src_id: str, tgt_id: str
    ) -> Optional[Dict[str, Any]]:
        with self.driver.session() as session:
            query = (
                "MATCH (src:Node {id: $src_id})-[r:RELATES_TO]->(tgt:Node {id: $tgt_id}) "
                "RETURN properties(r) as props"
            )
            result = session.run(query, src_id=src_id, tgt_id=tgt_id)
            record = result.single()
            return record["props"] if record else None

    async def has_node(self, node_id: str) -> bool:
        with self.driver.session() as session:
            query = "MATCH (n:Node {id: $node_id}) RETURN count(n) as count"
            result = session.run(query, node_id=node_id)
            return result.single()["count"] > 0

    async def has_edge(self, src_id: str, tgt_id: str) -> bool:
        with self.driver.session() as session:
            query = (
                "MATCH (src:Node {id: $src_id})-[r:RELATES_TO]->(tgt:Node {id: $tgt_id}) "
                "RETURN count(r) as count"
            )
            result = session.run(query, src_id=src_id, tgt_id=tgt_id)
            return result.single()["count"] > 0

    async def edge_degree(self, src_id: str, tgt_id: str) -> int:
        """Get the combined degree of source and target nodes"""
        src_degree = await self.node_degree(src_id)
        tgt_degree = await self.node_degree(tgt_id)
        return src_degree + tgt_degree

    async def get_all_nodes(self) -> List[str]:
        with self.driver.session() as session:
            query = "MATCH (n:Node) RETURN collect(n.id) as nodes"
            result = session.run(query)
            record = result.single()
            return record["nodes"] if record else []

    async def get_all_edges(self) -> List[Tuple[str, str]]:
        with self.driver.session() as session:
            query = (
                "MATCH (src:Node)-[:RELATES_TO]->(tgt:Node) "
                "RETURN collect([src.id, tgt.id]) as edges"
            )
            result = session.run(query)
            record = result.single()
            return [tuple(edge) for edge in (record["edges"] if record else [])]

    async def index_done_callback(self) -> None:
        # Implement if needed for cleanup or index refreshing
        pass

    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data by ID"""
        with self.driver.session() as session:
            query = (
                "MATCH (n:Node {id: $node_id}) "
                "RETURN n.id as id, properties(n) as props"
            )
            result = session.run(query, node_id=node_id)
            record = result.single()
            if record:
                props = record["props"]
                props["id"] = record["id"]
                return props
            return None

    async def get_nodes(self, node_ids: List[str]) -> List[Optional[Dict[str, Any]]]:
        """Get multiple nodes by IDs"""
        results = []
        for node_id in node_ids:
            node = await self.get_node(node_id)
            results.append(node)
        return results

    async def get_node_embedding(self, node_id: str) -> Optional[List[float]]:
        """Get node embedding if it exists"""
        node_data = await self.get_node(node_id)
        if node_data and "embedding" in node_data:
            return node_data["embedding"]
        return None

    async def node_degree(self, node_id: str) -> int:
        """Get the degree of a node (number of connected edges)"""
        with self.driver.session() as session:
            query = (
                "MATCH (n:Node {id: $node_id})-[r]-() "
                "RETURN COUNT(r) as degree"
            )
            result = session.run(query, node_id=node_id)
            record = result.single()
            return record["degree"] if record else 0

    async def get_node_degrees(self, node_ids: List[str]) -> List[int]:
        """Get degrees for multiple nodes"""
        degrees = []
        for node_id in node_ids:
            degree = await self.node_degree(node_id)
            degrees.append(degree)
        return degrees

    async def get_node_edges(self, node_id: str) -> List[Tuple[str, str]]:
        """Get all edges connected to a node"""
        with self.driver.session() as session:
            # Get outgoing edges
            outgoing_query = (
                "MATCH (src:Node {id: $node_id})-[r:RELATES_TO]->(tgt:Node) "
                "RETURN src.id as src_id, tgt.id as tgt_id"
            )
            # Get incoming edges
            incoming_query = (
                "MATCH (src:Node)-[r:RELATES_TO]->(tgt:Node {id: $node_id}) "
                "RETURN src.id as src_id, tgt.id as tgt_id"
            )
            
            edges = []
            # Process outgoing edges
            result = session.run(outgoing_query, node_id=node_id)
            for record in result:
                edges.append((
                    record["src_id"],
                    record["tgt_id"]
                ))
            
            # Process incoming edges
            result = session.run(incoming_query, node_id=node_id)
            for record in result:
                edges.append((
                    record["src_id"],
                    record["tgt_id"]
                ))
            
        return edges

# Also update the helper method
    async def get_nodes_edges(self, node_ids: List[str]) -> List[List[Tuple[str, str]]]:
        """Get edges for multiple nodes"""
        results = []
        for node_id in node_ids:
            edges = await self.get_node_edges(node_id)
            results.append(edges)
        return results
    
    async def get_edge(self, src_id: str, tgt_id: str) -> Optional[Dict[str, Any]]:
        """Get edge data between two nodes"""
        with self.driver.session() as session:
            query = (
                "MATCH (src:Node {id: $src_id})-[r:RELATES_TO]->(tgt:Node {id: $tgt_id}) "
                "RETURN properties(r) as props"
            )
            result = session.run(query, src_id=src_id, tgt_id=tgt_id)
            record = result.single()
            if record:
                return record["props"]
            return None

    async def get_edges(self, edge_pairs: List[Tuple[str, str]]) -> List[Optional[Dict[str, Any]]]:
        """Get multiple edges data"""
        results = []
        for src_id, tgt_id in edge_pairs:
            edge = await self.get_edge(src_id, tgt_id)
            results.append(edge)
        return results

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.close() 