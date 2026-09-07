# Fabric notebook source: deterministic customer simulator
# Install the fabric-customer-reference wheel in the Fabric environment first.

from pathlib import Path

from fabric_customer.simulator import materialize_scenario, replay_day

DAY = 7
RESET = True
REPLAY_DAY = None
OUTPUT = Path("/lakehouse/default/Files/fabric-customer")

materialize_scenario(OUTPUT, through_day=DAY, clean=RESET)
if REPLAY_DAY is not None:
    replay_day(OUTPUT, REPLAY_DAY)

print(f"customer source scenario materialized at {OUTPUT} through Day {DAY}")
