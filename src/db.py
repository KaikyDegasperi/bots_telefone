# -*- coding: utf-8 -*-
import asyncio
import pymysql
from typing import Any, Optional

from .config import DB_MAIN, DB_VENDAS

def _connect(db_cfg):
    return pymysql.connect(
        host=db_cfg.host,
        port=db_cfg.port,
        user=db_cfg.user,
        password=db_cfg.password,
        database=db_cfg.database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

async def execute_main(query: str, params: Optional[tuple] = None, fetchone: bool = False) -> Any:
    def _inner():
        conn = _connect(DB_MAIN)
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone() if fetchone else cursor.fetchall()
        finally:
            conn.commit()
            conn.close()
    return await asyncio.to_thread(_inner)

async def execute_vendas(query: str, params: Optional[tuple] = None, fetchone: bool = False) -> Any:
    def _inner():
        conn = _connect(DB_VENDAS)
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone() if fetchone else cursor.fetchall()
        finally:
            conn.commit()
            conn.close()
    return await asyncio.to_thread(_inner)

def execute_main_sync(query: str, params: Optional[tuple] = None, fetchone: bool = False) -> Any:
    return asyncio.run(execute_main(query, params, fetchone))

def execute_vendas_sync(query: str, params: Optional[tuple] = None, fetchone: bool = False) -> Any:
    return asyncio.run(execute_vendas(query, params, fetchone))
