# LingCard/characters/yangguang.py
from .character import Character

class Yangguang(Character):
    """阳光：对方回合没有使用攻击卡时，下回合额外抽取2张卡"""

    def __init__(self):
        # 阳光的辅助型发电阈值（均衡）：5 -> 8 -> 11 -> 14 -> 17
        upgrade_thresholds = [5, 13, 24, 38, 55]
        
        super().__init__(
            name="阳光",
            description="对方回合没有使用攻击卡时，下回合额外抽取2张卡",
            max_hp=10,
            base_energy_limit=3,  # 基础电能上限
            upgrade_thresholds=upgrade_thresholds
        )
    
    def on_turn_start(self, game_state, player, engine=None):
        """
        在自己回合开始时检查对方上一回合的状态。
        这个状态 'opponent_used_attack_last_turn' 需要由 GameEngine 在对方回合结束时设置。
        """
        if self.is_alive and not game_state.get_opponent_player().status.get('used_attack_this_turn', False):
            game_state.add_log(f"角色技能[{self.name}]触发：对手上回合未攻击，额外抽2张牌。")
            if engine:
                engine.draw_cards(player, 2)