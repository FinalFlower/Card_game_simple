# LingCard/cards/attack.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class AttackCard(ActionCard):
    def __init__(self):
        super().__init__(
            name="攻击",
            description="减少对方3点生命值",
            action_type=ActionType.ATTACK
        )

    def get_base_value(self) -> int:
        return 3