GET_BONE_BY_ID = """
SELECT id, kind, owner_id, size
FROM bones
WHERE id = $1
"""

ADD_BONE = """
INSERT INTO bones(kind, owner_id, size) VALUES ($1, $2, $3)
RETURNING
    id
"""
