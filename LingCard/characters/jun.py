# LingCard/characters/jun.py
from .character import Character
from typing import Tuple

class Jun(Character):
    """俊：可以帮队友承受伤害（每回合一次），前两次伤害减1"""
    
    def __init__(self):
        # 俊的守护型发电阈值（较慢）：6 -> 10 -> 15 -> 21 -> 28
        upgrade_thresholds = [6, 16, 31, 52, 80]
        
        super().__init__(
            name="俊",
            description="可以帮队友承受伤害（每回合一次），前两次伤害减1",
            max_hp=10,
            base_energy_limit=3,  # 基础电能上限
            upgrade_thresholds=upgrade_thresholds
        )
        self.status['damage_taken_count_this_turn'] = 0
        self.status['has_protected_teammate_this_turn'] = False

    def reset_turn_status(self):
        """回合结束，重置受伤次数和保护标记"""
        super().reset_turn_status()  # 调用父类方法以重置行动槽
        self.status['damage_taken_count_this_turn'] = 0
        self.status['has_protected_teammate_this_turn'] = False

    def on_take_damage(self, damage: int, attacker, game_state) -> Tuple[int, int]:
        """
        处理自身受伤时的减伤效果。
        """
        # 无论如何，先记录受伤次数
        self.status['damage_taken_count_this_turn'] += 1
        
        # 前两次伤害减1
        if self.status['damage_taken_count_this_turn'] <= 2:
            game_state.add_log(f"角色技能[{self.name}]触发：前两次伤害减1。")
            damage = max(0, damage - 1)
            
        return (damage, 0) # 返回修改后的伤害，无反击