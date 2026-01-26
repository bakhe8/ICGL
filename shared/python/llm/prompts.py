ARCHITECT_SYSTEM_PROMPT = "You are the Architect."
BUILDER_SYSTEM_PROMPT = "You are the Builder."
SENTINEL_SYSTEM_PROMPT = "You are the Sentinel."
POLICY_SYSTEM_PROMPT = "You are the Policy Enforcer."


class JSONParser:
    @staticmethod
    def parse(text: str) -> dict:
        return {}

    @staticmethod
    def parse_architect_output(text: str) -> dict:
        return {
            "analysis": "Stubbed analysis",
            "recommendations": [],
            "risks": [],
            "confidence_score": 1.0,
            "file_changes": [],
        }


def build_architect_user_prompt(*args, **kwargs) -> str:
    return "Stubbed user prompt"


def build_builder_user_prompt(*args, **kwargs) -> str:
    return "Stubbed user prompt"


def build_sentinel_user_prompt(*args, **kwargs) -> str:
    return "Stubbed user prompt"


def build_policy_user_prompt(*args, **kwargs) -> str:
    return "Stubbed user prompt"


# Aliases just in case
build_architect_prompt = build_architect_user_prompt
