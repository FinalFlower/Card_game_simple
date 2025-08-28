# LingCard/cards/reforge_magic_blade.py
from LingCard.cards.reforge_base import ReforgeCard

class ReforgeMagicBladeCard(ReforgeCard):
    """
    重铸.魔刀卡牌 (3cost)
    
    效果：
    - 对目标造成11点伤害
    - 同时在下一自身回合向手中置入一张解放.魔刀
    - 此卡使用后移出战斗，本场游戏无法再次抽取
    """
    
    def __init__(self):
        super().__init__(
            name="重铸.魔刀",
            description="对目标造成11点伤害，本回合结束后获得解放.魔刀（消耗3点电能，使用后移出战斗）",
            energy_cost=3,
            damage=11,
            next_card_name="解放.魔刀"
        )
    
    def get_next_card_class(self):
        """获取下一级卡牌类"""
        from LingCard.cards.liberation_magic_blade import LiberationMagicBladeCard
        return LiberationMagicBladeCard