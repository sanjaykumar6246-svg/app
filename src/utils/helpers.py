"""Utility functions for data generation."""
import uuid
import random
from typing import List

def generate_id() -> str:
    """Generate UUID similar to Asana's GID format."""
    return str(uuid.uuid4())

def random_color() -> str:
    """Generate random color for projects/tags."""
    colors = [
        'red', 'orange', 'yellow-orange', 'yellow', 'yellow-green',
        'green', 'blue-green', 'aqua', 'blue', 'indigo',
        'purple', 'magenta', 'hot-pink', 'pink', 'cool-gray'
    ]
    return random.choice(colors)

def weighted_choice(choices: List[tuple]) -> any:
    """Make a weighted random choice.
    
    Args:
        choices: List of (item, weight) tuples
    
    Returns:
        Selected item based on weights
    """
    total = sum(weight for item, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]
