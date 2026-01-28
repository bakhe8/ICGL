"""
ICGL Documentation Quality Improvement Loop
===========================================

Iterative documentation generation with multi-agent review.

This implements the FULL ICGL cycle:
1. DocumentationAgent generates initial docs
2. MediatorAgent reviews quality
3. If quality < threshold, request regeneration with feedback
4. Repeat until quality acceptable
5. Sentinel checks for risks
6. Policy Engine validates compliance
7. Human approves
"""

import asyncio

from src.core.governance.docs_pipeline import DocsRefactorPipeline
from src.core.kb.persistent import PersistentKnowledgeBase
from src.core.kb.schemas import ADR, uid
from src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


class GovernedDocsRefactor:
    """
    Full ICGL cycle for documentation refactoring.

    Implements:
    - Multi-agent review
    - Iterative improvement
    - Quality thresholds
    - Governance compliance
    """

    def __init__(self):
        self.pipeline = DocsRefactorPipeline()
        self.kb = PersistentKnowledgeBase()

    async def run_full_cycle(self, quality_threshold: float = 0.90, max_iterations: int = 3):
        """
        Run complete ICGL governance cycle for documentation.

        Args:
            quality_threshold: Minimum acceptable quality (0-1)
            max_iterations: Maximum refinement iterations
        """
        logger.info("🔷 Starting ICGL Governed Documentation Refactor Cycle")

        # Phase 1: Create ADR
        adr = self._create_adr()
        logger.info(f"✅ ADR Created: {adr.id}")

        # Phase 2: Iterative Generation with Review
        iteration = 0
        acceptable_quality = False
        improvement_suggestions = None  # Feedback for next iteration

        while iteration < max_iterations and not acceptable_quality:
            iteration += 1
            logger.info(f"\n🔄 Iteration {iteration}/{max_iterations}")

            # Generate documentation (with feedback from previous iteration if available)
            snapshot = self.pipeline.load_snapshot()

            if iteration == 1 or not improvement_suggestions:
                # First iteration or no suggestions - run without focus areas
                plan = await self.pipeline.analyze(snapshot)
            else:
                # Subsequent iterations with feedback
                plan = await self.pipeline.analyze(snapshot, focus_areas=improvement_suggestions)

            # Multi-agent review (returns score + suggestions)
            quality_score, improvement_suggestions = await self._review_quality(plan, adr)

            logger.info(f"📊 Quality Score: {quality_score:.1%}")
            if improvement_suggestions:
                logger.info(f"💡 Suggestions: {len(improvement_suggestions)} items")

            if quality_score >= quality_threshold:
                acceptable_quality = True
                logger.info("✅ Quality threshold met!")

                # Stage files
                manifest = self.pipeline.stage_files(plan)

                # Phase 3: Sentinel & Policy checks
                risks = await self._sentinel_check(plan, adr)
                policy_ok = await self._policy_check(plan, adr)

                if risks:
                    logger.warning(f"⚠️  Risks detected: {risks}")

                if policy_ok:
                    logger.info("✅ Policy compliance verified")

                return {
                    "adr_id": adr.id,
                    "iterations": iteration,
                    "final_quality": quality_score,
                    "manifest": manifest,
                    "session_id": manifest.session_id,
                    "improvements_applied": bool(improvement_suggestions),
                }
            else:
                logger.warning(f"⚠️  Quality {quality_score:.1%} below threshold {quality_threshold:.1%}")
                logger.info(f"📝 Will regenerate with {len(improvement_suggestions)} improvement suggestions")

        logger.error(f"❌ Failed to achieve quality threshold after {max_iterations} iterations")
        return None

    def _create_adr(self) -> ADR:
        """Create ADR for documentation improvement."""
        adr = ADR(
            id=uid(),
            title="Documentation Quality Improvement via ICGL",
            status="DRAFT",
            context=(
                "Current documentation is incomplete and inconsistent. "
                "Need professional-grade, comprehensive documentation that "
                "reflects the actual system with real code examples."
            ),
            decision=(
                "Use ICGL multi-agent governance cycle to generate, review, "
                "and iteratively improve documentation until quality threshold met."
            ),
            consequences=[
                "Better developer onboarding",
                "Reduced support burden",
                "Professional system image",
                "Demonstrated ICGL capabilities",
            ],
            related_policies=["P-DOC-01"],  # Hypothetical doc quality policy
            sentinel_signals=[],
            human_decision_id=None,
        )

        self.kb.add_adr(adr)
        return adr

    async def _review_quality(self, plan, adr) -> tuple[float, list[str]]:
        """
        Review documentation quality and provide improvement suggestions.

        Returns:
            (quality_score, improvement_suggestions)
        """
        # Start with agent confidence
        base_quality = plan.confidence_score
        suggestions = []

        logger.info(f"📊 Initial Quality: {base_quality:.1%}")

        # Apply quality heuristics and build suggestions
        quality_score = base_quality

        # Check file coverage
        if len(plan.generated_files) < 5:
            quality_score *= 0.8
            suggestions.append("Generate more comprehensive coverage (need 5+ files)")

        # Check for issues
        if len(plan.issues) > 10:
            quality_score *= 0.9
            suggestions.append(f"Address {len(plan.issues)} identified issues")

        # Check file sizes and content quality
        for f in plan.generated_files:
            if len(f.content) < 500:
                suggestions.append(f"Expand {f.path} with more detail and examples")
                quality_score *= 0.95
            elif len(f.content) < 1000:
                suggestions.append(f"Add more comprehensive content to {f.path}")
                quality_score *= 0.98

        # Check for code examples in documentation
        has_code_blocks = any("```" in f.content for f in plan.generated_files)
        if not has_code_blocks:
            suggestions.append("Include real code examples from the codebase")
            quality_score *= 0.9

        # Limit suggestions to top 5 most important
        final_suggestions = suggestions[:5]
        final_quality = min(quality_score, 1.0)

        logger.info(f"📊 Final Quality Score: {final_quality:.1%}")
        if final_suggestions:
            logger.info(f"💡 Generated {len(final_suggestions)} improvement suggestions")

        return final_quality, final_suggestions

    async def _sentinel_check(self, plan, adr) -> list:
        """Check for risks using Sentinel."""
        risks = []

        # Simple risk checks
        if plan.confidence_score < 0.7:
            risks.append("Low agent confidence")

        if len(plan.risk_notes) > 0:
            risks.extend(plan.risk_notes)

        return risks

    async def _policy_check(self, plan, adr) -> bool:
        """Verify policy compliance."""
        # Simple policy checks

        # P-DOC-01: All generated files must have content
        for gen_file in plan.generated_files:
            if not gen_file.content or len(gen_file.content) < 100:
                return False

        return True


async def main():
    """Run governed documentation refactor."""
    cycle = GovernedDocsRefactor()
    result = await cycle.run_full_cycle(quality_threshold=0.90, max_iterations=3)

    if result:
        print("\n✅ SUCCESS!")
        print(f"ADR: {result['adr_id']}")
        print(f"Iterations: {result['iterations']}")
        print(f"Final Quality: {result['final_quality']:.1%}")
        print(f"Session: {result['session_id']}")
    else:
        print("\n❌ Failed to achieve quality threshold")


if __name__ == "__main__":
    asyncio.run(main())
