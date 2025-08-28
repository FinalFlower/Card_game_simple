# LingCard/buffs/demonic.py
from typing import Dict, Any
from LingCard.core.buff_system import Buff, BuffType, BuffCategory

class DemonicBuff(Buff):
    """
    堕魔buff类 - 强大但危险的力量标记
    
    功能：
    - 标记角色获得了魔刀的力量
    - 可能在未来版本中产生特殊效果
    - 当前版本主要作为状态标识存在
    - 永久持续，通常只有1层
    """
    
    def __init__(self, stacks: int = 1):
        """
        初始化堕魔buff
        
        Args:
            stacks: 堕魔层数，通常为1层
        """
        super().__init__(
            buff_type=BuffType.DEMONIC,
            stacks=stacks,
            duration=-1  # 永久持续
        )
    
    def _get_category(self) -> BuffCategory:
        """堕魔属于状态效果类别"""
        return BuffCategory.STATUS_EFFECT
    
    def apply_effect(self, character, game_state) -> Dict[str, Any]:
        """
        堕魔buff的效果应用
        
        当前版本：主要作为状态标识，可能在回合开始时记录日志
        未来版本：可能会有额外的效果（如伤害加成、特殊能力等）
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            Dict: 效果执行结果
        """
        # 当前版本只是状态标识，不产生实际效果
        # 未来可以在这里添加堕魔的特殊效果
        return {
            'type': 'demonic_presence',
            'message': f'{character.name} 被魔刀的力量所影响...',
            'demonic_stacks': self.stacks,
            'effect_applied': False  # 当前版本无实际效果
        }
    
    def can_stack(self, other_buff: 'Buff') -> bool:
        """
        堕魔可以叠加，但通常只会有1层
        
        Args:
            other_buff: 另一个buff
            
        Returns:
            bool: 是否可以叠加
        """
        return self.buff_type == other_buff.buff_type
    
    def tick_duration(self) -> bool:
        """
        堕魔永不过期
        
        Returns:
            bool: 始终返回False，表示不会因时间过期而移除
        """
        return False
    
    def is_negative_effect(self) -> bool:
        """
        判断堕魔是否为负面效果
        
        Returns:
            bool: 当前版本返回False，因为还没有负面效果
                  未来版本可能会根据具体实现返回True
        """
        return False  # 当前版本暂时不算负面效果
    
    def get_power_level(self) -> str:
        """
        获取堕魔力量等级描述
        
        Returns:
            str: 力量等级描述
        """
        if self.stacks == 1:
            return "微弱的魔性"
        elif self.stacks <= 3:
            return "明显的魔性"
        elif self.stacks <= 5:
            return "强烈的魔性"
        else:
            return "深度的魔化"
    
    def get_description(self) -> str:
        """获取堕魔的描述信息"""
        power_desc = self.get_power_level()
        return f"堕魔 x{self.stacks} ({power_desc})"
    
    def __str__(self) -> str:
        return f"堕魔 x{self.stacks}"