# LingCard/cards/reforge_crude_iron.py
from LingCard.cards.reforge_base import ReforgeCard

class ReforgeCrudeIronCard(ReforgeCard):
    """
    重铸.粗制铁刃卡牌 (0cost)
    
    效果：
    - 对目标造成5点伤害
    - 同时在下一自身回合向手中置入一张重铸.名刀
    - 此卡使用后移出战斗，本场游戏无法再次抽取
    """
    
    def __init__(self):
        super().__init__(
            name="重铸.粗制铁刃",
            description="对目标造成5点伤害，本回合结束后获得重铸.名刀（使用后移出战斗）",
            energy_cost=0,
            damage=5,
            next_card_name="重铸.名刀"
        )
    
    def get_next_card_class(self):
        """获取下一级卡牌类"""
        from LingCard.cards.reforge_famous_blade import ReforgeFamousBladeCard
        return ReforgeFamousBladeCard