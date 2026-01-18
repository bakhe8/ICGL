import asyncio
from dotenv import load_dotenv
load_dotenv()
from icgl.governance.icgl import ICGL
from icgl.agents.base import Problem

async def main():
    print('starting...')
    icgl = ICGL(enforce_runtime_guard=False)
    if icgl.memory:
        await icgl.memory.initialize()
        await icgl._bootstrap_memory()
    problem = Problem(title="Boost agent activity", context="Each agent proposes quick wins for their domain")
    synth = await icgl.registry.run_and_synthesize(problem, icgl.kb)
    print("Agents run:", [r.agent_id for r in synth.individual_results])
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
