# LingCard/characters/cafe.py
from .character import Character

class Cafe(Character):
    """Cafe：每回合第一次造成伤害时伤害加1"""
    
    def __init__(self):
        # Cafe的标准发电阈值：5 -> 8 -> 11 -> 14 -> 17
        upgrade_thresholds = [5, 13, 24, 38, 55]
        
        super().__init__(
            name="Cafe",
            description="每回合第一次造成伤害时伤害加1",
            max_hp=10,
            base_energy_limit=3,  # 基础电能上限
            upgrade_thresholds=upgrade_thresholds
        )
        # 初始化技能状态
        self.status['first_damage_dealt_this_turn'] = False

    def reset_turn_status(self):
        """回合结束时，重置"第一次伤害"标记"""
        super().reset_turn_status()  # 调用父类方法以重置行动槽
        self.status['first_damage_dealt_this_turn'] = False
        
    def on_deal_damage(self, damage: int, game_state) -> int:
        """
        重写造成伤害的钩子。
        如果是本回合第一次伤害，则伤害+1并更新状态。
        """
        if not self.status.get('first_damage_dealt_this_turn', False):
            game_state.add_log(f"角色技能[{self.name}]触发：第一次伤害+1！")
            self.status['first_damage_dealt_this_turn'] = True
            return damage + 1
        return damage