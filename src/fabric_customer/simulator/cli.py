"""Command-line interface for deterministic source scenario generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .engine import materialize_scenario, replay_day, reset_scenario, verify_scenario
from .scenarios import scenario_catalog


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fabric-customer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List deterministic scenario days")

    materialize = sub.add_parser(
        "materialize",
        help="Generate source deliveries and expected truth",
    )
    materialize.add_argument("--output", default="build/customer-scenario")
    materialize.add_argument("--through-day", type=int, default=7)
    materialize.add_argument("--no-clean", action="store_true")

    reset = sub.add_parser("reset", help="Remove and recreate generated scenario output")
    reset.add_argument("--output", default="build/customer-scenario")

    replay = sub.add_parser("replay", help="Replay the exact delivery for one day")
    replay.add_argument("day", type=int)
    replay.add_argument("--output", default="build/customer-scenario")

    verify = sub.add_parser("verify", help="Verify frozen scenario checksums")
    verify.add_argument("--output", default="build/customer-scenario")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "list":
        for step in scenario_catalog():
            print(f"{step.day}: {step.slug} - {step.description}")
        return 0
    if args.command == "materialize":
        root = materialize_scenario(
            Path(args.output),
            through_day=args.through_day,
            clean=not args.no_clean,
        )
        workload = verify_scenario(root)
        print(f"{root}\nworkload_digest={workload['workload_digest']}")
        return 0
    if args.command == "reset":
        print(reset_scenario(Path(args.output)))
        return 0
    if args.command == "replay":
        print(replay_day(Path(args.output), args.day))
        return 0
    if args.command == "verify":
        workload = verify_scenario(Path(args.output))
        print(f"workload_digest={workload['workload_digest']}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
