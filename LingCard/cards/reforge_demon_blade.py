# LingCard/cards/reforge_demon_blade.py
from LingCard.cards.reforge_base import ReforgeCard

class ReforgeDemonBladeCard(ReforgeCard):
    """
    重铸.妖刀卡牌 (2cost)
    
    效果：
    - 对目标造成9点伤害
    - 同时在下一自身回合向手中置入一张重铸.魔刀
    - 此卡使用后移出战斗，本场游戏无法再次抽取
    """
    
    def __init__(self):
        super().__init__(
            name="重铸.妖刀",
            description="对目标造成9点伤害，本回合结束后获得重铸.魔刀（消耗2点电能，使用后移出战斗）",
            energy_cost=2,
            damage=9,
            next_card_name="重铸.魔刀"
        )
    
    def get_next_card_class(self):
        """获取下一级卡牌类"""
        from LingCard.cards.reforge_magic_blade import ReforgeMagicBladeCard
        return ReforgeMagicBladeCard