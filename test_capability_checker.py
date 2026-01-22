"""
Test CapabilityChecker functionality
"""

from backend.agents.capability_checker import (
    AgentRecommendation,
    CapabilityChecker,
    check_before_creating_agent,
)


def test_check_existing_capability():
    """Test checking for existing capabilities."""
    checker = CapabilityChecker()

    print("=" * 60)
    print("TEST 1: Check existing capability (code_generation)")
    print("=" * 60)

    result = checker.check_capability_exists("code_generation")

    print(f"Exists: {result.exists}")
    print(f"Agents: {result.agents_with_capability}")
    print(f"Recommendation: {result.recommendation.value}")
    print(f"Target Agent: {result.target_agent}")
    print(f"Rationale: {result.rationale}")
    print()

    assert result.exists == True
    assert "builder" in result.agents_with_capability
    assert result.recommendation == AgentRecommendation.ENHANCE_EXISTING
    print("✅ TEST 1 PASSED\n")


def test_check_non_existing_capability():
    """Test checking for non-existing capability."""
    checker = CapabilityChecker()

    print("=" * 60)
    print("TEST 2: Check non-existing capability (test_generation)")
    print("=" * 60)

    result = checker.check_capability_exists("test_generation")

    print(f"Exists: {result.exists}")
    print(f"Agents: {result.agents_with_capability}")
    print(f"Recommendation: {result.recommendation.value}")
    print(f"Rationale: {result.rationale}")
    print()

    assert result.exists == False
    assert len(result.agents_with_capability) == 0
    assert result.recommendation == AgentRecommendation.CREATE_NEW
    print("✅ TEST 2 PASSED\n")


def test_suggest_testing_agent():
    """Test suggesting TestingAgent creation."""
    checker = CapabilityChecker()

    print("=" * 60)
    print("TEST 3: Suggest TestingAgent (NEW agent)")
    print("=" * 60)

    result = checker.suggest_agent_creation(
        proposed_name="TestingAgent",
        proposed_capabilities=[
            "test_generation",
            "coverage_analysis",
            "pytest_integration",
        ],
    )

    print(f"Recommendation: {result.recommendation.value}")
    print(f"Rationale: {result.rationale}")
    print()

    assert result.recommendation == AgentRecommendation.CREATE_NEW
    print("✅ TEST 3 PASSED: TestingAgent can be created (no overlap)\n")


def test_suggest_performance_agent():
    """Test suggesting PerformanceAgent (should enhance Sentinel)."""
    checker = CapabilityChecker()

    print("=" * 60)
    print("TEST 4: Suggest PerformanceAgent (should enhance Sentinel)")
    print("=" * 60)

    result = checker.suggest_agent_creation(
        proposed_name="PerformanceAgent",
        proposed_capabilities=[
            "performance_monitoring",
            "drift_monitoring",  # Overlap with Sentinel!
        ],
    )

    print(f"Recommendation: {result.recommendation.value}")
    print(f"Target Agent: {result.target_agent}")
    print(f"Rationale: {result.rationale}")
    print()

    # Should suggest enhancing Sentinel
    assert result.target_agent == "sentinel"
    print("✅ TEST 4 PASSED: Correctly suggests enhancing Sentinel\n")


def test_list_gaps():
    """Test listing known gaps."""
    checker = CapabilityChecker()

    print("=" * 60)
    print("TEST 5: List known capability gaps")
    print("=" * 60)

    gaps = checker.list_gaps()

    for gap_name, priority in gaps.items():
        print(f"  - {gap_name}: {priority}")

    assert "test_generation" in gaps
    assert gaps["test_generation"] == "CRITICAL"
    print("\n✅ TEST 5 PASSED: Known gaps listed correctly\n")


def test_convenience_function():
    """Test convenience function."""
    print("=" * 60)
    print("TEST 6: Convenience function check_before_creating_agent")
    print("=" * 60)

    # Test creating agent with unique capabilities
    result = check_before_creating_agent(["refactoring", "code_smells_detection"])

    print(f"Recommendation: {result.recommendation.value}")
    print(f"Rationale: {result.rationale}")
    print()

    assert result.recommendation == AgentRecommendation.CREATE_NEW
    print("✅ TEST 6 PASSED: Convenience function works\n")


if __name__ == "__main__":
    print("\n" + "🧪 " * 30)
    print("TESTING CAPABILITY CHECKER")
    print("🧪 " * 30 + "\n")

    try:
        test_check_existing_capability()
        test_check_non_existing_capability()
        test_suggest_testing_agent()
        test_suggest_performance_agent()
        test_list_gaps()
        test_convenience_function()

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nCapabilityChecker is working correctly and ready to use!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
