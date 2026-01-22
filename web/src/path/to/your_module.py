from typing import Any

def process_user_input(data: str) -> Any:
    # Assuming `execute_query` is a function that accepts a query and parameters
    query = "SELECT * FROM users WHERE name = %s"
    return execute_query(query, (data,))