# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import List, Dict

from .db import execute_main, execute_vendas
from .config import TIMEOUT_VENDAS_SECONDS

logger = logging.getLogger("PhoneSync")

CPFS_QUERY_TPL = """
    SELECT DISTINCT c.cpf_cliente
    FROM clientes c
    JOIN tarefas t ON t.id = c.tarefa_id
    WHERE t.status IN ('concluido', 'aguardando', 'em_execucao')
      AND c.cpf_cliente IS NOT NULL
    LIMIT {batch_limit}
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

async def fetch_cpfs(batch_limit: int) -> List[Dict]:
    query = CPFS_QUERY_TPL.format(batch_limit=batch_limit)
    return await execute_main(query)

async def update_phone_for_cpf(cpf: str) -> bool:
    try:
        res = await asyncio.wait_for(
            execute_vendas(TEL_QUERY, (cpf,), fetchone=True),
            timeout=TIMEOUT_VENDAS_SECONDS
        )
        if res and res.get("telefone"):
            telefone = res["telefone"]
            await execute_main(UPDATE_PHONE, (telefone, cpf))
            logger.info(f"[OK] Telefone {telefone} atualizado para CPF {cpf}")
            return True
        else:
            logger.debug(f"[SKIP] Nenhum telefone encontrado para CPF {cpf}")
    except asyncio.TimeoutError:
        logger.warning(f"[Timeout] ao buscar telefone para CPF {cpf}")
    except Exception as e:
        logger.warning(f"[Erro] ao atualizar telefone para CPF {cpf}: {e}")
    return False


async def run_once(batch_limit: int = 100, sleep_every: int = 10) -> int:
    cpfs_resultado = await fetch_cpfs(batch_limit)
    logger.info(f"Iniciando atualização de até {len(cpfs_resultado)} CPFs...")
    atualizados = 0

    for i, row in enumerate(cpfs_resultado):
        cpf = row["cpf_cliente"]
        ok = await update_phone_for_cpf(cpf)
        if ok:
            atualizados += 1

        if (i + 1) % sleep_every == 0:
            await asyncio.sleep(1)

    logger.info(f"Atualização finalizada: {atualizados} telefones atualizados.")
    return atualizados

async def run_loop(interval_seconds: int, batch_limit: int, sleep_every: int) -> None:
    logger.info(f"Entrando em modo contínuo (intervalo={interval_seconds}s).")
    while True:
        try:
            await run_once(batch_limit=batch_limit, sleep_every=sleep_every)
        except Exception as e:
            logger.exception(f"Falha na iteração do loop: {e}")
        await asyncio.sleep(interval_seconds)
