CREATE_USER = """
INSERT INTO users(name)
VALUES ($1)
RETURNING *
"""
