from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from apps.config import settings
from clients.qdrant_client import QdrantCodeIndex
from clients.neo4j_client import Neo4jCodeGraph

repo_root = Path("sample_services/checkout_service").resolve()

qdrant = QdrantCodeIndex(settings.qdrant_url, settings.qdrant_collection)
print(qdrant.index_repo(str(repo_root)))

graph = Neo4jCodeGraph(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
print(graph.index_repo(str(repo_root)))
graph.close()
