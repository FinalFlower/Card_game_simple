# LingCard/buffs/poison.py
from typing import Dict, Any
from LingCard.core.buff_system import Buff, BuffType, BuffCategory

class PoisonBuff(Buff):
    """
    中毒buff - 持续伤害效果
    
    效果：
    - 每回合结束时造成等同于中毒层数的伤害
    - 造成伤害后，中毒层数减少2层
    - 当层数为0或更少时，buff自动移除
    """
    
    def __init__(self, stacks: int = 1, caster=None):
        """
        初始化中毒buff
        
        Args:
            stacks: 中毒层数（默认1层）
            caster: 施加中毒效果的角色（用于发电等级计算）
        """
        # 中毒是永久持续的，直到层数消耗完毕
        super().__init__(BuffType.POISON, stacks, duration=-1)
        self.caster = caster  # 记录施加者，用于发电等级计算
    
    def _get_category(self) -> BuffCategory:
        """获取buff分类"""
        return BuffCategory.DAMAGE_OVER_TIME
    
    def apply_effect(self, character, game_state) -> Dict[str, Any]:
        """
        应用中毒效果
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            Dict: 效果执行结果
        """
        if not character.is_alive:
            return {
                'type': 'poison_damage',
                'damage': 0,
                'target': character.name,
                'message': f"{character.name} 已倒下，中毒无效果"
            }
        
        # 造成等同于中毒层数的伤害
        poison_damage = self.stacks
        actual_damage = character.take_damage(poison_damage)
        
        # 记录日志
        damage_msg = f"{character.name} 受到 {actual_damage} 点中毒伤害"
        if game_state:
            game_state.add_log(damage_msg)
        
        # 将中毒伤害计入施加者的发电等级（如果施加者存在且存活）
        if self.caster and self.caster.is_alive and actual_damage > 0:
            level_up = self.caster.add_damage_to_generation(actual_damage, game_state)
            if level_up:
                game_state.add_log(f"[中毒效果] {self.caster.name} 通过中毒伤害获得发电等级提升！")
        
        # 中毒层数减少2层
        layers_reduced = min(2, self.stacks)
        self.reduce_stacks(layers_reduced)
        
        # 如果还有剩余层数，记录剩余信息
        if self.stacks > 0:
            remaining_msg = f"{character.name} 的中毒层数减少 {layers_reduced} 层，剩余 {self.stacks} 层"
            if game_state:
                game_state.add_log(remaining_msg)
        
        return {
            'type': 'poison_damage',
            'damage': actual_damage,
            'original_damage': poison_damage,
            'target': character.name,
            'stacks_reduced': layers_reduced,
            'remaining_stacks': self.stacks,
            'message': damage_msg,
            'character_alive': character.is_alive
        }
    
    def get_description(self) -> str:
        """获取中毒buff的详细描述"""
        return f"中毒 x{self.stacks} (每回合结束受到{self.stacks}点伤害，然后层数-2)"
    
    def __str__(self) -> str:
        return f"中毒 x{self.stacks}"