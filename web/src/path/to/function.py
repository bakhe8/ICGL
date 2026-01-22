def process_user_input(data):
    query = "SELECT * FROM users WHERE name = %s"
    return execute_query(query, (data,))