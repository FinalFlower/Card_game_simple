# LingCard/cards/poison.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class PoisonCard(ActionCard):
    """
    淬毒卡 - 对敌方施加中毒buff
    
    效果：对目标施加2层中毒buff
    消耗：2点电能
    """
    
    def __init__(self):
        super().__init__(
            name="淬毒",
            description="对敌方施加2层中毒效果（消耗2点电能）",
            action_type=ActionType.POISON,
            energy_cost=2  # 淬毒卡消耗2点电能
        )

    def get_base_value(self) -> int:
        """
        获取基础数值 - 淬毒卡的基础值为施加的中毒层数
        
        Returns:
            int: 施加的中毒层数（2层）
        """
        return 2