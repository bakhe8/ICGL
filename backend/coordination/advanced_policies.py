from . import POLICY_READ_ONLY, ChannelPolicy

def get_policy_registry():
    return [POLICY_READ_ONLY, ChannelPolicy("default")]
