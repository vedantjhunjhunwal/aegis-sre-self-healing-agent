from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    env: str = "dev"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_alert_topic: str = "production-alerts"

    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"

    prometheus_url: str = "http://localhost:9090"
    jaeger_url: str = "http://localhost:16686"
    kubeconfig: str = ""

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "aegis_code"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "aegis-password"

    github_token: str = ""
    github_owner: str = ""
    github_repo: str = ""
    github_base_branch: str = "main"
    github_create_real_pr: bool = False

    workspace_dir: str = "workspace"
    max_repair_attempts: int = 5
    enable_k8s_integration: bool = False
    enable_firecracker: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
