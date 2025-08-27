# LingCard/cards/heal.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class HealCard(ActionCard):
    def __init__(self):
        super().__init__(
            name="回血",
            description="增加自身2点生命值（消耗２点电能）",
            action_type=ActionType.HEAL,
            energy_cost=2  # 回血卡消耗２点电能
        )

    def get_base_value(self) -> int:
        return 2