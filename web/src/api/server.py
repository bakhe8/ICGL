from backend.agents.capability_checker import CapabilityChecker
# Other necessary imports...

def run_analysis_task(idea_text: str, ...):
    # Existing code to extract idea text...
    
    # Initialize the CapabilityChecker
    checker = CapabilityChecker()
    
    # Check if the idea mentions creating a new agent
    if 'agent' in idea_text and 'create' in idea_text:
        # Extract proposed capabilities from the idea text
        proposed_capabilities = extract_capabilities_from_idea(idea_text)
        
        # Call the capability checker
        check_result = checker.suggest_agent_creation(proposed_capabilities)
        
        # Add check_result to the analysis metadata
        analysis_metadata['capability_check'] = check_result
        
        # If recommendation is ENHANCE_EXISTING, add warning to analysis
        if check_result == 'ENHANCE_EXISTING':
            analysis_metadata['warnings'].append('Consider enhancing existing agent capabilities.')
    
    # Continue with the rest of the run_analysis_task logic...
    
    # Return capability_check in the response
    return {
        'analysis_metadata': analysis_metadata,
        'capability_check': check_result
    }