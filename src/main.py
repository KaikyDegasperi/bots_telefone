# -*- coding: utf-8 -*-
import os
import time
import pymysql
import logging
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# LOG CONFIG CORRIGIDO — agora SEM ERROS NO DOCKER
# =====================================================

LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)  # garante que não vira diretório errado

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/sync_telefones.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("PhoneSyncLoop")

# =====================================================
# CONFIGURAÇÕES DO BANCO
# =====================================================

DB_MAIN = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
}

DB_VENDAS = {
    "host": os.getenv("DB_VENDAS_HOST"),
    "port": int(os.getenv("DB_VENDAS_PORT", "3306")),
    "user": os.getenv("DB_VENDAS_USERNAME"),
    "password": os.getenv("DB_VENDAS_PASSWORD"),
    "database": os.getenv("DB_VENDAS_DATABASE"),
}

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "180"))

# =====================================================
# QUERIES
# =====================================================

FETCH_CPFS = f"""
    SELECT cpf_cliente
    FROM clientes
    WHERE telefones_completos IS NULL
    LIMIT {BATCH_SIZE}
"""

TEL_QUERY = """
    SELECT CONCAT(cont.ddd, cont.telefone) AS telefone
    FROM tb_clientes cli
    JOIN (
        SELECT id_cliente, MIN(id_contato) AS id_contato
        FROM tb_contatos
        GROUP BY id_cliente
    ) cont_idx ON cont_idx.id_cliente = cli.id_cliente
    JOIN tb_contatos cont ON cont.id_contato = cont_idx.id_contato
    WHERE cli.cpf_cliente = %s
"""

UPDATE_PHONE = """
    UPDATE clientes
    SET telefones_completos = %s
    WHERE cpf_cliente = %s
"""

# =====================================================
# FUNÇÕES
# =====================================================

def connect(cfg):
    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def fetch_cpfs_null():
    try:
        conn = connect(DB_MAIN)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(FETCH_CPFS)
                return cursor.fetchall()
    except Exception as e:
        log.error(f"Erro ao buscar CPFs: {e}")
        return []


def buscar_telefone_vendas(cpf):
    try:
        conn = connect(DB_VENDAS)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(TEL_QUERY, (cpf,))
                return cursor.fetchone()
    except Exception as e:
        log.error(f"Erro ao consultar telefone para {cpf}: {e}")
        return None


def atualizar_telefone_main(cpf, telefone):
    try:
        conn = connect(DB_MAIN)
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(UPDATE_PHONE, (telefone, cpf))
        log.info(f"[UPDATE] {cpf} -> {telefone}")
    except Exception as e:
        log.error(f"Erro ao atualizar telefone do CPF {cpf}: {e}")


# =====================================================
# LOOP PRINCIPAL
# =====================================================

def main_loop():
    log.info("=== Iniciando sincronização contínua de telefones ===")

    while True:
        cpfs = fetch_cpfs_null()

        if not cpfs:
            log.info("Nenhum CPF pendente. Aguardando...")
            time.sleep(SLEEP_SECONDS)
            continue

        log.info(f"{len(cpfs)} CPFs encontrados para processar.")

        for row in cpfs:
            cpf = row["cpf_cliente"]

            tel_row = buscar_telefone_vendas(cpf)
            telefone = tel_row.get("telefone", "SEM TELEFONE") if tel_row else "SEM TELEFONE"
            atualizar_telefone_main(cpf, telefone)

        log.info(f"Ciclo finalizado. Pausando por {SLEEP_SECONDS} segundos.")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main_loop()
