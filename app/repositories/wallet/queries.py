CREATE_WALLET = """
INSERT INTO wallet(user_id, address, private)
VALUES ($1, $2, $3)
"""
