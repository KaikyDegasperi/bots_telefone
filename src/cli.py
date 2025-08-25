# -*- coding: utf-8 -*-
import argparse
import asyncio
import logging

from .logging_conf import setup_logging
from .config import (
    LOG_LEVEL,
    SYNC_INTERVAL_SECONDS,
    BATCH_LIMIT,
    SLEEP_EVERY,
)
from .phone_sync import run_once, run_loop

def main():
    parser = argparse.ArgumentParser(
        prog="phone-sync",
        description="Atualiza telefones em clientes a partir do DB de vendas."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_once = sub.add_parser("once", help="Executa uma única varredura.")
    p_once.add_argument("--batch-limit", type=int, default=BATCH_LIMIT)
    p_once.add_argument("--sleep-every", type=int, default=SLEEP_EVERY)

    p_loop = sub.add_parser("loop", help="Executa continuamente em intervalos.")
    p_loop.add_argument("--interval", type=int, default=SYNC_INTERVAL_SECONDS)
    p_loop.add_argument("--batch-limit", type=int, default=BATCH_LIMIT)
    p_loop.add_argument("--sleep-every", type=int, default=SLEEP_EVERY)

    args = parser.parse_args()
    setup_logging(LOG_LEVEL)
    logging.getLogger("PhoneSync").info("Iniciando…")

    if args.cmd == "once":
        asyncio.run(run_once(batch_limit=args.batch_limit, sleep_every=args.sleep_every))
    elif args.cmd == "loop":
        asyncio.run(run_loop(
            interval_seconds=args.interval,
            batch_limit=args.batch_limit,
            sleep_every=args.sleep_every
        ))

if __name__ == "__main__":
    main()
