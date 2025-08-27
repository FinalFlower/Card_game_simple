# LingCard/characters/liuli.py
import random
from .character import Character
from typing import Tuple

class Liuli(Character):
    """琉璃：受到攻击时1-6随机，6时免疫攻击并反击2点"""

    def __init__(self):
        # 琉璃的反击型发电阈值（较快）：4 -> 7 -> 11 -> 16 -> 22
        upgrade_thresholds = [4, 11, 22, 38, 60]
        
        super().__init__(
            name="琉璃",
            description="受到攻击时1-6随机判定，6时免疫并反击2点",
            max_hp=10,
            base_energy_limit=3,  # 基础电能上限
            upgrade_thresholds=upgrade_thresholds
        )

    def on_take_damage(self, damage: int, attacker, game_state) -> Tuple[int, int]:
        """
        重写受到伤害的钩子，实现随机判定。
        返回 (最终受到的伤害, 对攻击者的反击伤害)。
        """
        roll = random.randint(1, 6)
        game_state.add_log(f"角色技能[{self.name}]触发：进行随机判定... 结果是 {roll}！")
        
        if roll == 6:
            game_state.add_log(f"[{self.name}] 判定成功！免疫本次伤害并反击2点！")
            return (0, 2)  # 0点伤害, 2点反击
        else:
            game_state.add_log(f"[{self.name}] 判定失败，正常受到伤害。")
            return (damage, 0) # 正常伤害, 0点反击