# Infer target path
target_path = problem.metadata.get('target_file')
if not target_path:
    # Extract from context or use convention
    if 'test' in problem.title.lower():
        target_path = 'tests/test_generated.py'
    else:
        target_path = 'backend/generated_code.py'