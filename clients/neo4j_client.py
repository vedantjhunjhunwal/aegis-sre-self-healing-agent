from pathlib import Path
from typing import Dict, Any, List
import ast
from neo4j import GraphDatabase


class Neo4jCodeGraph:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def index_repo(self, repo_root: str) -> Dict[str, Any]:
        root = Path(repo_root)
        nodes = []
        edges = []

        for py_file in root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue
            rel = str(py_file.relative_to(root))
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    fn_name = node.name
                    nodes.append({"file": rel, "function": fn_name, "line": node.lineno})
                    for call in self._calls(node):
                        edges.append({"src": fn_name, "dst": call, "file": rel})

        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            for n in nodes:
                session.run(
                    "MERGE (f:File {path: $file}) "
                    "MERGE (fn:Function {name: $function, file: $file}) "
                    "SET fn.line = $line "
                    "MERGE (f)-[:CONTAINS]->(fn)",
                    **n,
                )
            for e in edges:
                session.run(
                    "MATCH (src:Function {name: $src, file: $file}) "
                    "MERGE (dst:Function {name: $dst}) "
                    "MERGE (src)-[:CALLS]->(dst)",
                    **e,
                )

        return {"functions": len(nodes), "calls": len(edges)}

    def find_function(self, name: str) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (fn:Function {name: $name}) "
                "OPTIONAL MATCH (fn)-[:CALLS]->(dst:Function) "
                "RETURN fn.name AS name, fn.file AS file, fn.line AS line, collect(dst.name) AS calls",
                name=name,
            )
            return [dict(r) for r in result]

    def _calls(self, fn: ast.FunctionDef):
        calls = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        return calls
