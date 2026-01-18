import asyncio
from dotenv import load_dotenv
load_dotenv()
from icgl.governance.icgl import ICGL
from icgl.agents.base import Problem

TASKS = [
    ("ADR summary card UI", "Add a dashboard card showing latest ADR status; minimal backend/UI changes"),
    ("API availability alert", "Add simple uptime check + alert hook for ICGL API to reduce MTTR"),
    ("RuntimeGuard startup perf", "Reduce startup latency of RuntimeGuard while preserving checks")
]

async def run_task(title, context):
    icgl = ICGL(enforce_runtime_guard=False)
    problem = Problem(title=title, context=context)
    synth = await icgl.registry.run_and_synthesize(problem, icgl.kb)
    return synth

async def main():
    for title, context in TASKS:
        print("\n=====", title, "=====")
        synth = await run_task(title, context)
        print("Agents:", [r.agent_id for r in synth.individual_results])
        print("Consensus recommendations:")
        for rec in synth.consensus_recommendations:
            print("-", rec)
        print("Concerns:")
        for c in synth.all_concerns:
            print("-", c)
        for res in synth.individual_results:
            print("\n--", res.agent_id, res.role.value, "--")
            print("Conf:", res.confidence)
            print("Analysis:", res.analysis)
            if res.recommendations:
                print("Recs:", res.recommendations)
            if res.concerns:
                print("Concerns:", res.concerns)

asyncio.run(main())
