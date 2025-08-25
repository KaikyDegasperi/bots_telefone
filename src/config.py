# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

def _load_db(prefix: str) -> DBConfig:
    return DBConfig(
        host=os.getenv(f"{prefix}_HOST", "127.0.0.1"),
        port=int(os.getenv(f"{prefix}_PORT", "3306")),
        user=os.getenv(f"{prefix}_USERNAME", "root"),
        password=os.getenv(f"{prefix}_PASSWORD", ""),
        database=os.getenv(f"{prefix}_DATABASE", ""),
    )

DB_MAIN = _load_db("DB")
DB_VENDAS = _load_db("DB_VENDAS")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))
BATCH_LIMIT = int(os.getenv("BATCH_LIMIT", "100"))
SLEEP_EVERY = int(os.getenv("SLEEP_EVERY", "10"))
TIMEOUT_VENDAS_SECONDS = int(os.getenv("TIMEOUT_VENDAS_SECONDS", "5"))
