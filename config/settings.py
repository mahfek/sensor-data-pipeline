import yaml
from pathlib import Path

class Settings:
    def __init__(self, config_file: str = None):
        config_file = config_file or Path(__file__).parent / "settings.yaml"
        with open(config_file, "r") as f:
            cfg = yaml.safe_load(f)

        db_cfg = cfg["database"]

        self.DB_USER = db_cfg["user"]
        self.DB_PASS = db_cfg["password"]
        self.DB_HOST = db_cfg.get("host", "localhost")
        self.DB_PORT = db_cfg.get("port", 5432)
        self.DB_NAME = db_cfg["name"]
        self.DB_POOL_SIZE = db_cfg.get("pool_size", 20)
        self.DB_MAX_OVERFLOW = db_cfg.get("max_overflow", 5)

    @property
    def sqlalchemy_uri(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
