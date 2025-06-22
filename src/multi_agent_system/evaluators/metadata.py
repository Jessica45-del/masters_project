"""
Metadata template to describe each case
"""


from typing import TypedDict

class MetadataDict(TypedDict):
    difficulty: str
    type: str

def metadata(difficulty: str, type: str) -> MetadataDict:
    return {"difficulty": difficulty, "type": type}
