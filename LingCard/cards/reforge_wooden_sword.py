# LingCard/cards/reforge_wooden_sword.py
from LingCard.cards.reforge_base import ReforgeCard

class ReforgeWoodenSwordCard(ReforgeCard):
    """
    重铸.木刀卡牌 (0cost)
    
    效果：
    - 对目标造成3点伤害
    - 同时在下一自身回合向手中置入一张重铸.粗制铁刃
    - 此卡使用后移出战斗，本场游戏无法再次抽取
    """
    
    def __init__(self):
        super().__init__(
            name="重铸.木刀",
            description="对目标造成3点伤害，下一回合获得重铸.粗制铁刃（使用后移出战斗）",
            energy_cost=0,
            damage=3,
            next_card_name="重铸.粗制铁刃"
        )
    
    def get_next_card_class(self):
        """获取下一级卡牌类"""
        from LingCard.cards.reforge_crude_iron import ReforgeCrudeIronCard
        return ReforgeCrudeIronCard