#!/usr/bin/env python3
"""Phase 2 DevOps agent foundation CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.phase2.mcp_client import MockDevOpsToolClient, RealMcpClient
from agents.phase2.runner import Phase2DevOpsAgent
from agents.phase2.store import AgentStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 2 DevOps agent foundation")
    parser.add_argument(
        "command",
        choices=["alert-cycle", "watch", "prevention-cycle", "store-summary"],
        help="Workflow to run",
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "real"],
        default=os.getenv("PHASE2_AGENT_MODE", "mock"),
        help="Tool adapter mode. Real mode currently requires wiring the RealMcpClient adapter.",
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("PHASE2_AGENT_DB", "agents/.data/phase2_devops_agent.db"),
        help="SQLite database path for persisted investigations and recommendations.",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Mark production-impacting remediation as approved for this run.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Allow the work-item adapter to create external changes when approval allows it.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=int(os.getenv("PHASE2_AGENT_INTERVAL_SECONDS", "300")),
        help="Polling interval for watch mode.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="Number of watch cycles to run. Use 0 to run until interrupted.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = AgentStore(args.db_path)

    if args.command == "store-summary":
        print(json.dumps(store.summary(), indent=2))
        return 0

    tools = MockDevOpsToolClient() if args.mode == "mock" else RealMcpClient()
    agent = Phase2DevOpsAgent(tools=tools, store=store)

    if args.command == "alert-cycle":
        result = agent.run_alert_cycle(auto_approve=args.auto_approve, dry_run=not args.execute)
        print(json.dumps(result, indent=2))
    elif args.command == "prevention-cycle":
        result = agent.run_prevention_cycle()
        print(json.dumps(result, indent=2))
    else:
        run_watch(agent, args)
    return 0


def run_watch(agent: Phase2DevOpsAgent, args: argparse.Namespace) -> None:
    cycle = 0
    while True:
        cycle += 1
        result = agent.run_alert_cycle(auto_approve=args.auto_approve, dry_run=not args.execute)
        print(json.dumps({"cycle": cycle, "result": result}, indent=2))

        if args.cycles and cycle >= args.cycles:
            return
        time.sleep(max(args.interval_seconds, 1))


if __name__ == "__main__":
    raise SystemExit(main())
