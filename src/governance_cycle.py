from adr_manager import ADRManager
from learning_log import LearningLog

def run_governance_cycle():
    # Initialize ADR Manager and Learning Log
    adr_manager = ADRManager()
    learning_log = LearningLog()

    # Step 1: Review pending ADRs
    pending_adrs = adr_manager.get_pending_adrs()
    for adr in pending_adrs:
        adr_manager.review_adr(adr)

    # Step 2: Generate learning logs
    learning_log.generate_log()

if __name__ == "__main__":
    run_governance_cycle()