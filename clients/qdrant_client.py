from pathlib import Path
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib
import math


def cheap_embedding(text: str, dims: int = 64) -> List[float]:
    vec = [0.0] * dims
    for token in text.lower().split():
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class QdrantCodeIndex:
    def __init__(self, url: str, collection: str):
        self.url = url
        self.collection = collection
        self.client = QdrantClient(url=url)

    def ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=64, distance=Distance.COSINE),
            )

    def index_repo(self, repo_root: str) -> Dict[str, Any]:
        self.ensure_collection()
        root = Path(repo_root)
        points = []
        idx = 1
        for file in root.rglob("*.py"):
            if "__pycache__" in str(file) or ".venv" in str(file):
                continue
            text = file.read_text(encoding="utf-8", errors="ignore")
            rel = str(file.relative_to(root))
            points.append(PointStruct(
                id=idx,
                vector=cheap_embedding(text),
                payload={"file": rel, "text": text[:3000]},
            ))
            idx += 1
        if points:
            self.client.upsert(collection_name=self.collection, points=points)
        return {"indexed_files": len(points), "collection": self.collection}

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        self.ensure_collection()
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=cheap_embedding(query),
            limit=limit,
        )
        return [
            {
                "score": hit.score,
                "file": hit.payload.get("file"),
                "preview": hit.payload.get("text", "")[:500],
            }
            for hit in hits
        ]
