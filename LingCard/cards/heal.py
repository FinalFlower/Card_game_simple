# LingCard/cards/heal.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class HealCard(ActionCard):
    def __init__(self):
        super().__init__(
            name="回血",
            description="增加自身2点生命值",
            action_type=ActionType.HEAL
        )

    def get_base_value(self) -> int:
        return 2