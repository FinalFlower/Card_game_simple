# LingCard/characters/xinhe.py
from .character import Character

class Xinhe(Character):
    """星河：每回合不使用技能时抽取一个行动卡"""

    def __init__(self):
        # 星河的辅助型发电阈值（均衡）：5 -> 8 -> 11 -> 14 -> 17
        upgrade_thresholds = [5, 13, 24, 38, 55]
        
        super().__init__(
            name="星河",
            description="每回合不使用技能时抽取一个行动卡",
            max_hp=10,
            base_energy_limit=3,  # 基础电能上限
            upgrade_thresholds=upgrade_thresholds
        )
        self.status['used_card_this_turn'] = False

    def reset_turn_status(self):
        """回合结束，重置使用卡牌的标记"""
        super().reset_turn_status()  # 调用父类方法以重置行动槽
        self.status['used_card_this_turn'] = False

    def on_card_played(self, card, game_state):
        """
        当此角色使用卡牌时，引擎会调用此钩子。
        我们在这里设置一个标记。
        """
        self.status['used_card_this_turn'] = True

    def on_turn_end(self, game_state, player, engine=None):
        """
        在回合结束时检查是否使用了卡牌。
        如果没有，则让引擎为玩家抽一张牌。
        """
        if self.is_alive and not self.status.get('used_card_this_turn', False):
            game_state.add_log(f"角色技能[{self.name}]触发：本回合未使用卡牌，额外抽1张牌。")
            if engine:
                engine.draw_cards(player, 1)