# Code for optimisation of token size per agent
import json


# Add to batch_utils.py
def calculate_batch_size(items: list, max_tokens: int, per_item_overhead: int = 50) -> int:
    """Calculate safe batch size based on token estimates"""
    if not items:
        return 10

    sample = items[0]
    item_tokens = len(json.dumps(sample)) // 4
    return max(1, min(50, max_tokens // (item_tokens + per_item_overhead)))