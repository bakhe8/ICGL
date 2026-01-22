"""
Direct test of BuilderAgent to see if it generates file_changes
"""

import asyncio

from backend.agents.base import Problem
from backend.agents.builder import BuilderAgent


async def test_builder():
    builder = BuilderAgent()

    problem = Problem(
        title="Test code generation",
        context="Create a simple Python function that returns 'Hello World'",
        metadata={
            "decision": "Create a simple Python function that returns 'Hello World'",
            "target_files": ["test_output.py"],
            "file_contents": {},
        },
    )

    print("🔧 Running BuilderAgent...")
    result = await builder._analyze(problem, kb=None)

    print("\n📊 Result:")
    print(f"  - Confidence: {result.confidence}")
    print(f"  - Analysis: {result.analysis[:200]}...")
    print(f"  - File changes count: {len(result.file_changes)}")

    if result.file_changes:
        for i, fc in enumerate(result.file_changes):
            print(f"\n  📄 File change {i + 1}:")
            print(f"     Path: {fc.path}")
            print(f"     Mode: {fc.mode}")
            print(f"     Content preview: {fc.content[:100]}...")
    else:
        print("  ⚠️ NO FILE CHANGES GENERATED!")
        print(f"  Concerns: {result.concerns}")
        print(f"  References: {result.references}")


if __name__ == "__main__":
    asyncio.run(test_builder())
