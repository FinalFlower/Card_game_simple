# LingCard/buffs/shield.py
from typing import Dict, Any
from LingCard.core.buff_system import Buff, BuffType, BuffCategory

class ShieldBuff(Buff):
    """
    护盾buff类 - 提供伤害吸收
    
    功能：
    - 吸收受到的伤害
    - 护盾值耗尽时自动移除
    - 永久持续直到被消耗完毕
    """
    
    def __init__(self, stacks: int = 1):
        """
        初始化护盾buff
        
        Args:
            stacks: 护盾点数
        """
        super().__init__(
            buff_type=BuffType.SHIELD,
            stacks=stacks,
            duration=-1  # 永久持续直到被消耗
        )
    
    def _get_category(self) -> BuffCategory:
        """护盾属于有益效果类别"""
        return BuffCategory.BENEFICIAL
    
    def apply_effect(self, character, game_state) -> Dict[str, Any]:
        """
        护盾buff不主动产生效果，主要在受到伤害时被动触发
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            Dict: 效果执行结果
        """
        return {
            'type': 'shield_passive',
            'message': f'{character.name} 当前拥有 {self.stacks} 点护盾',
            'shield_amount': self.stacks
        }
    
    def absorb_damage(self, damage: int, game_state=None) -> tuple:
        """
        吸收伤害
        
        Args:
            damage: 受到的伤害
            game_state: 游戏状态
            
        Returns:
            tuple: (剩余伤害, 被吸收的伤害, 是否护盾耗尽)
        """
        if self.stacks <= 0:
            return damage, 0, True
        
        absorbed = min(damage, self.stacks)
        remaining_damage = damage - absorbed
        self.stacks -= absorbed
        
        is_depleted = self.stacks <= 0
        
        if game_state:
            if is_depleted:
                game_state.add_log(f"护盾吸收了 {absorbed} 点伤害，护盾耗尽")
            else:
                game_state.add_log(f"护盾吸收了 {absorbed} 点伤害，剩余护盾: {self.stacks}")
        
        return remaining_damage, absorbed, is_depleted
    
    def can_stack(self, other_buff: 'Buff') -> bool:
        """护盾可以叠加"""
        return self.buff_type == other_buff.buff_type
    
    def tick_duration(self) -> bool:
        """
        护盾不会因时间过期
        
        Returns:
            bool: 始终返回False，护盾只会因为被消耗而移除
        """
        return False
    
    def reduce_stacks(self, stacks: int) -> bool:
        """
        重写减少层数方法
        
        Args:
            stacks: 要减少的层数
            
        Returns:
            bool: 是否应该移除此buff
        """
        self.stacks -= stacks
        return self.stacks <= 0
    
    def get_description(self) -> str:
        """获取护盾的描述信息"""
        return f"护盾 {self.stacks} 点"
    
    def __str__(self) -> str:
        return f"护盾 {self.stacks}"