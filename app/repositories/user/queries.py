CREATE_USER = """
INSERT INTO user_info(first_name)
VALUES ($1)
RETURNING *
"""

AUTH_USER = """
SELECT id, first_name, last_name, third_name
FROM user_info
WHERE login = $1 and password = $2
"""
