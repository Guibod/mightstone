from pathlib import Path

from ..models.ability import AbilityList

"""
The MTG ruleset
"""

abilities = AbilityList.model_validate_json(
    Path(__file__).parent.joinpath("abilities.json").read_bytes()
)
