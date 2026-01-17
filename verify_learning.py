import asyncio
import shutil
import os
from icgl.agents.base import Agent, AgentRole, Problem
from icgl.memory.qdrant_adapter import QdrantAdapter, Document

class TestAgent(Agent):
    async def _analyze(self, problem, kb):
        # We just want to test _ask_llm logic (which calls recall_lessons)
        # But _ask_llm requires an LLM provider or returns mock.
        # We want to test that 'recall_lessons' finds the data.
        pass
        
    async def test_learning(self):
        print("🧠 Testing Active Learning Recall...")
        lessons = await self.recall_lessons("proposal using XML format")
        if lessons:
            print(f"   ✅ Recalled Valid Lesson: {lessons[0]}")
            return True
        else:
            print("   ❌ Failed to recall lesson.")
            return False

async def run_test():
    # 1. Setup Memory
    mem_path = "data/verify_learning_mem"
    if os.path.exists(mem_path):
        shutil.rmtree(mem_path)
        
    memory = QdrantAdapter(path=mem_path)
    await memory.initialize()
    
    # 2. Plant a Lesson (Mocking an Intervention)
    print("🌱 Planting Lesson: 'Human hates XML'...")
    doc = Document(
        id="lesson-test-1",
        content="Human REJECTED/MODIFIED this proposal: Use XML for configuration. REASON: We prefer JSON/YAML only.",
        metadata={"type": "lesson", "action": "REJECT", "reason": "No XML"}
    )
    await memory.add_document(doc)
    
    # 3. Init Agent
    agent = TestAgent("test-scholar", AgentRole.ARCHITECT)
    agent.memory = memory
    
    # 4. Verify Recall
    found = await agent.test_learning()
    
    # Cleanup
    if hasattr(memory.client, "close"):
        memory.client.close()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
