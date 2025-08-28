# LingCard/buffs/sword_intent.py
from typing import Dict, Any
from LingCard.core.buff_system import Buff, BuffType, BuffCategory

class SwordIntentBuff(Buff):
    """
    剑意buff类 - 剑技系统的核心buff
    
    功能：
    - 可无限叠加的层数系统
    - 永久持续（不会随时间消失）
    - 为特定剑技提供使用条件（如拔刀斩需要5层剑意）
    - 某些技能消耗时会减少层数
    """
    
    def __init__(self, stacks: int = 1):
        """
        初始化剑意buff
        
        Args:
            stacks: 剑意层数，默认1层
        """
        super().__init__(
            buff_type=BuffType.SWORD_INTENT,
            stacks=stacks,
            duration=-1  # 永久持续
        )
    
    def _get_category(self) -> BuffCategory:
        """剑意属于有益效果类别"""
        return BuffCategory.BENEFICIAL
    
    def apply_effect(self, character, game_state) -> Dict[str, Any]:
        """
        剑意buff不主动产生效果，主要作为条件和资源存在
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            Dict: 效果执行结果
        """
        # 剑意本身不产生主动效果，只作为资源存在
        return {
            'type': 'sword_intent_passive',
            'message': f'{character.name} 当前拥有 {self.stacks} 层剑意',
            'sword_intent_stacks': self.stacks
        }
    
    def can_stack(self, other_buff: 'Buff') -> bool:
        """剑意可以无限叠加"""
        return self.buff_type == other_buff.buff_type
    
    def consume_stacks(self, amount: int) -> bool:
        """
        消耗剑意层数
        
        Args:
            amount: 要消耗的层数
            
        Returns:
            bool: 是否有足够的层数消耗（但不会因消耗而移除buff）
        """
        if self.stacks >= amount:
            self.stacks -= amount
            return True
        return False
    
    def has_enough_stacks(self, required: int) -> bool:
        """
        检查是否有足够的剑意层数
        
        Args:
            required: 需要的层数
            
        Returns:
            bool: 是否有足够层数
        """
        return self.stacks >= required
    
    def tick_duration(self) -> bool:
        """
        剑意永不过期，重写此方法确保永不被时间移除
        
        Returns:
            bool: 始终返回False，表示不会因时间过期而移除
        """
        return False
    
    def reduce_stacks(self, stacks: int) -> bool:
        """
        重写减少层数方法，确保剑意不会因层数为0而被移除
        
        Args:
            stacks: 要减少的层数
            
        Returns:
            bool: 始终返回False，确保剑意buff不会被移除
        """
        self.stacks = max(0, self.stacks - stacks)
        return False  # 即使层数为0也不移除buff
    
    def get_description(self) -> str:
        """获取剑意的描述信息"""
        return f"剑意 x{self.stacks}"
    
    def __str__(self) -> str:
        return f"剑意 x{self.stacks}"