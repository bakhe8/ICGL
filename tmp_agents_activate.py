import asyncio
from dotenv import load_dotenv
load_dotenv()
from icgl.governance.icgl import ICGL
from icgl.agents.base import Problem

async def main():
    icgl = ICGL(enforce_runtime_guard=False)
    problem = Problem(
        title="Increase agent activation",
        context="Have all agents propose quick improvements in their domain to boost system throughput"
    )
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
