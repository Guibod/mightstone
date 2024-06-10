from pathlib import Path

from ...services.wotc import ComprehensiveRules

"""
The MTG ruleset
"""

rules = ComprehensiveRules.model_validate_json(
    Path(__file__).parent.joinpath("rules.json").read_bytes()
)
