# LingCard/core/action_slot.py
from typing import Dict, Any
from enum import Enum


class ActionSlotType(Enum):
    """行动槽类型枚举"""
    BASIC = "基础行动槽"
    SPECIAL = "特殊行动槽"  # 为未来扩展预留


class ActionSlot:
    """
    行动槽类 - 管理角色在回合中的行动次数
    
    核心功能：
    - 跟踪行动槽的可用状态
    - 提供行动槽的使用和重置接口
    - 支持不同类型的行动槽（为未来扩展预留）
    """
    
    def __init__(self, slot_type: ActionSlotType = ActionSlotType.BASIC, max_uses: int = 1):
        """
        初始化行动槽
        
        Args:
            slot_type: 行动槽类型
            max_uses: 每回合最大使用次数
        """
        self.slot_type = slot_type
        self.max_uses = max_uses
        self.remaining_uses = max_uses
        self.used_this_turn = False
    
    def can_use(self) -> bool:
        """
        检查是否可以使用行动槽
        
        Returns:
            bool: 如果可以使用返回True，否则返回False
        """
        return self.remaining_uses > 0
    
    def use_slot(self) -> bool:
        """
        尝试使用行动槽
        
        Returns:
            bool: 如果成功使用返回True，否则返回False
        """
        if not self.can_use():
            return False
        
        self.remaining_uses -= 1
        # 只要使用过一次就标记为True，但不影响后续使用
        self.used_this_turn = True
        return True
    
    def reset_turn(self):
        """
        重置行动槽状态（回合结束时调用）
        """
        self.remaining_uses = self.max_uses
        self.used_this_turn = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取行动槽状态信息
        
        Returns:
            Dict: 包含行动槽详细状态的字典
        """
        return {
            'slot_type': self.slot_type.value,
            'max_uses': self.max_uses,
            'remaining_uses': self.remaining_uses,
            'used_this_turn': self.used_this_turn,
            'can_use': self.can_use()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化行动槽状态
        
        Returns:
            Dict: 可序列化的状态字典
        """
        return {
            'slot_type': self.slot_type.name,
            'max_uses': self.max_uses,
            'remaining_uses': self.remaining_uses,
            'used_this_turn': self.used_this_turn
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionSlot':
        """
        从字典数据创建行动槽实例
        
        Args:
            data: 包含行动槽状态的字典
            
        Returns:
            ActionSlot: 行动槽实例
        """
        slot = cls(
            slot_type=ActionSlotType[data['slot_type']],
            max_uses=data['max_uses']
        )
        slot.remaining_uses = data['remaining_uses']
        slot.used_this_turn = data['used_this_turn']
        return slot
    
    def __str__(self) -> str:
        """字符串表示"""
        status = "可用" if self.can_use() else "已用完"
        return f"{self.slot_type.value}({self.remaining_uses}/{self.max_uses}, {status})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"ActionSlot(type={self.slot_type.name}, remaining={self.remaining_uses}, max={self.max_uses}, used={self.used_this_turn})"


class ActionSlotManager:
    """
    行动槽管理器 - 为未来的复杂行动槽系统预留
    
    可用于管理多个行动槽、特殊行动槽规则等
    """
    
    def __init__(self):
        self.action_slots = []
    
    def add_slot(self, slot: ActionSlot):
        """添加行动槽"""
        self.action_slots.append(slot)
    
    def has_available_slot(self) -> bool:
        """检查是否有可用的行动槽"""
        return any(slot.can_use() for slot in self.action_slots)
    
    def use_any_available_slot(self) -> bool:
        """使用任意一个可用的行动槽"""
        for slot in self.action_slots:
            if slot.use_slot():
                return True
        return False
    
    def reset_all_slots(self):
        """重置所有行动槽"""
        for slot in self.action_slots:
            slot.reset_turn()
    
    def get_all_status(self) -> list:
        """获取所有行动槽状态"""
        return [slot.get_status() for slot in self.action_slots]