# LingCard/cards/defend.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class DefendCard(ActionCard):
    def __init__(self):
        super().__init__(
            name="防御",
            description="下一次受到伤害减少1点",
            action_type=ActionType.DEFEND
        )

    def get_base_value(self) -> int:
        return 1