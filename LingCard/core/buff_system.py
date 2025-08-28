# LingCard/core/buff_system.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum

class BuffType(Enum):
    """Buff类型枚举"""
    # 持续伤害类
    POISON = "中毒"
    BURN = "燃烧"
    
    # 状态效果类
    FREEZE = "冰冻"
    
    # 武器精通类
    SWORD_INTENT = "剑意"  # 新增：剑意系统
    DEMONIC = "堕魔"         # 新增：堕魔状态
    
    # 防护类
    SHIELD = "护盾"
    
    # 恢复类
    REGENERATION = "再生"
    
    # 增益类
    STRENGTH = "力量"
    
    # 负面类
    WEAKNESS = "虚弱"

class BuffCategory(Enum):
    """Buff分类枚举"""
    DAMAGE_OVER_TIME = "持续伤害"  # 如中毒、燃烧
    STATUS_EFFECT = "状态效果"    # 如冰冻、虚弱
    BENEFICIAL = "有益效果"       # 如护盾、再生

class Buff(ABC):
    """
    Buff基类 - 所有buff效果的抽象基类
    
    设计原则：
    - 每个buff都有类型、持续时间、层数等基本属性
    - 通过抽象方法定义buff的具体效果
    - 支持叠加、刷新、移除等操作
    """
    
    def __init__(self, buff_type: BuffType, stacks: int = 1, duration: int = -1):
        """
        初始化buff
        
        Args:
            buff_type: buff类型
            stacks: buff层数
            duration: 持续时间（回合数，-1表示永久）
        """
        self.buff_type = buff_type
        self.stacks = stacks
        self.duration = duration
        self.category = self._get_category()
    
    @abstractmethod
    def _get_category(self) -> BuffCategory:
        """获取buff分类"""
        pass
    
    @abstractmethod
    def apply_effect(self, character, game_state) -> Dict[str, Any]:
        """
        应用buff效果
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            Dict: 效果执行结果
        """
        pass
    
    def can_stack(self, other_buff: 'Buff') -> bool:
        """
        检查是否可以与另一个buff叠加
        
        Args:
            other_buff: 另一个buff
            
        Returns:
            bool: 是否可以叠加
        """
        return self.buff_type == other_buff.buff_type
    
    def add_stacks(self, stacks: int):
        """增加buff层数"""
        self.stacks += stacks
    
    def reduce_stacks(self, stacks: int) -> bool:
        """
        减少buff层数
        
        Args:
            stacks: 要减少的层数
            
        Returns:
            bool: 是否应该移除此buff（层数为0或更少）
        """
        self.stacks -= stacks
        return self.stacks <= 0
    
    def tick_duration(self) -> bool:
        """
        时间推进（通常在回合结束时调用）
        
        Returns:
            bool: 是否应该移除此buff（持续时间结束）
        """
        if self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化buff状态"""
        return {
            'class': self.__class__.__name__,
            'buff_type': self.buff_type.name,
            'stacks': self.stacks,
            'duration': self.duration,
            'category': self.category.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], all_buff_classes: Dict) -> 'Buff':
        """从字典数据创建buff实例"""
        buff_class = all_buff_classes.get(data['class'])
        if not buff_class:
            raise ValueError(f"Unknown buff class: {data['class']}")
        
        buff = buff_class(
            buff_type=BuffType[data['buff_type']],
            stacks=data['stacks'],
            duration=data['duration']
        )
        return buff
    
    def get_description(self) -> str:
        """获取buff的描述信息"""
        if self.duration == -1:
            return f"{self.buff_type.value} x{self.stacks} (永久)"
        else:
            return f"{self.buff_type.value} x{self.stacks} ({self.duration}回合)"
    
    def __str__(self) -> str:
        return self.get_description()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.buff_type.name}, stacks={self.stacks}, duration={self.duration})"


class BuffManager:
    """
    Buff管理器 - 管理角色身上的所有buff效果
    
    功能：
    - 添加、移除、更新buff
    - 处理buff叠加逻辑
    - 执行buff效果
    - buff状态序列化
    """
    
    def __init__(self):
        self.buffs: List[Buff] = []
    
    def add_buff(self, new_buff: Buff, game_state=None) -> bool:
        """
        添加buff，处理叠加逻辑
        
        Args:
            new_buff: 要添加的buff
            game_state: 游戏状态（用于记录日志）
            
        Returns:
            bool: 是否成功添加
        """
        # 查找是否已存在相同类型的buff
        existing_buff = self.get_buff_by_type(new_buff.buff_type)
        
        if existing_buff and existing_buff.can_stack(new_buff):
            # 叠加到现有buff
            existing_buff.add_stacks(new_buff.stacks)
            if game_state:
                game_state.add_log(f"叠加 {new_buff.buff_type.value} (现在 x{existing_buff.stacks})")
            return True
        elif not existing_buff:
            # 添加新buff
            self.buffs.append(new_buff)
            if game_state:
                game_state.add_log(f"获得 {new_buff.get_description()}")
            return True
        
        return False
    
    def remove_buff(self, buff_type: BuffType, game_state=None) -> bool:
        """
        移除指定类型的buff
        
        Args:
            buff_type: 要移除的buff类型
            game_state: 游戏状态（用于记录日志）
            
        Returns:
            bool: 是否成功移除
        """
        buff_to_remove = self.get_buff_by_type(buff_type)
        if buff_to_remove:
            self.buffs.remove(buff_to_remove)
            if game_state:
                game_state.add_log(f"移除 {buff_type.value}")
            return True
        return False
    
    def get_buff_by_type(self, buff_type: BuffType) -> Optional[Buff]:
        """根据类型获取buff"""
        for buff in self.buffs:
            if buff.buff_type == buff_type:
                return buff
        return None
    
    def has_buff(self, buff_type: BuffType) -> bool:
        """检查是否拥有指定类型的buff"""
        return self.get_buff_by_type(buff_type) is not None
    
    def apply_all_buffs(self, character, game_state) -> List[Dict[str, Any]]:
        """
        应用所有buff效果
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
            
        Returns:
            List: 所有buff效果的执行结果
        """
        results = []
        for buff in self.buffs[:]:  # 使用副本避免在迭代时修改列表
            result = buff.apply_effect(character, game_state)
            results.append(result)
        return results
    
    def tick_all_buffs(self, character, game_state):
        """
        处理所有buff的时间推进和清理
        
        Args:
            character: 受影响的角色
            game_state: 游戏状态
        """
        buffs_to_remove = []
        
        for buff in self.buffs:
            # 检查持续时间
            if buff.tick_duration():
                buffs_to_remove.append(buff)
                continue
            
            # 检查层数（某些buff可能在效果中减少层数）
            if buff.stacks <= 0:
                buffs_to_remove.append(buff)
        
        # 移除过期或无效的buff
        for buff in buffs_to_remove:
            self.buffs.remove(buff)
            if game_state:
                game_state.add_log(f"{character.name} 的 {buff.buff_type.value} 效果消失")
    
    def get_all_buffs(self) -> List[Buff]:
        """获取所有buff的副本"""
        return self.buffs.copy()
    
    def clear_all_buffs(self, game_state=None):
        """清除所有buff"""
        if self.buffs and game_state:
            game_state.add_log("清除所有buff效果")
        self.buffs.clear()
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """序列化所有buff状态"""
        return [buff.to_dict() for buff in self.buffs]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]], all_buff_classes: Dict) -> 'BuffManager':
        """从字典数据创建BuffManager实例"""
        manager = cls()
        for buff_data in data:
            buff = Buff.from_dict(buff_data, all_buff_classes)
            manager.buffs.append(buff)
        return manager
    
    def __len__(self) -> int:
        return len(self.buffs)
    
    def __iter__(self):
        return iter(self.buffs)
    
    def __str__(self) -> str:
        if not self.buffs:
            return "无buff效果"
        return " | ".join(str(buff) for buff in self.buffs)