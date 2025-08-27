# LingCard/core/energy_system.py
from typing import Dict, Any

class EnergySystem:
    """
    电能系统类 - 管理角色的电能和发电等级
    
    核心功能：
    - 管理电能的消耗和回复
    - 跟踪累积伤害量
    - 处理发电等级提升
    - 支持电能上限和行动槽扩展
    """
    
    def __init__(self, base_energy_limit: int = 3, base_action_slots: int = 1):
        """
        初始化电能系统
        
        Args:
            base_energy_limit: 基础电能上限
            base_action_slots: 基础行动槽数量
        """
        self.base_energy_limit = base_energy_limit
        self.base_action_slots = base_action_slots
        
        # 当前状态
        self.current_energy = base_energy_limit
        self.generation_level = 0  # 发电等级
        self.accumulated_damage = 0  # 累积伤害量
        
        # 发电等级配置
        self.damage_per_level = 5  # 每级需要的伤害量
    
    def get_energy_limit(self) -> int:
        """获取当前电能上限"""
        return self.base_energy_limit + self.generation_level
    
    def get_action_slots_count(self) -> int:
        """获取当前行动槽数量"""
        return self.base_action_slots + self.generation_level
    
    def can_consume_energy(self, amount: int) -> bool:
        """检查是否可以消耗指定的电能"""
        return self.current_energy >= amount
    
    def consume_energy(self, amount: int) -> bool:
        """
        消耗电能
        
        Args:
            amount: 要消耗的电能量
            
        Returns:
            bool: 是否成功消耗
        """
        if not self.can_consume_energy(amount):
            return False
        
        self.current_energy -= amount
        return True
    
    def restore_energy(self, amount: int = 1):
        """
        回复电能
        
        Args:
            amount: 要回复的电能量，默认1点
        """
        max_energy = self.get_energy_limit()
        self.current_energy = min(max_energy, self.current_energy + amount)
    
    def add_damage(self, damage: int) -> bool:
        """
        添加累积伤害量，可能触发发电等级提升
        
        Args:
            damage: 造成的伤害量
            
        Returns:
            bool: 是否发电等级提升了
        """
        self.accumulated_damage += damage
        
        # 检查是否可以提升发电等级
        new_level = self.accumulated_damage // self.damage_per_level
        if new_level > self.generation_level:
            old_level = self.generation_level
            self.generation_level = new_level
            
            # 发电等级提升时，当前电能也相应增加
            energy_increase = new_level - old_level
            self.current_energy = min(self.get_energy_limit(), self.current_energy + energy_increase)
            
            return True
        
        return False
    
    def reset_turn(self):
        """回合重置时的电能回复"""
        self.restore_energy(1)
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取电能系统状态信息
        
        Returns:
            Dict: 包含电能系统详细状态的字典
        """
        return {
            'current_energy': self.current_energy,
            'energy_limit': self.get_energy_limit(),
            'generation_level': self.generation_level,
            'accumulated_damage': self.accumulated_damage,
            'action_slots_count': self.get_action_slots_count(),
            'damage_to_next_level': self.damage_per_level - (self.accumulated_damage % self.damage_per_level)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化电能系统状态
        
        Returns:
            Dict: 可序列化的状态字典
        """
        return {
            'base_energy_limit': self.base_energy_limit,
            'base_action_slots': self.base_action_slots,
            'current_energy': self.current_energy,
            'generation_level': self.generation_level,
            'accumulated_damage': self.accumulated_damage,
            'damage_per_level': self.damage_per_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnergySystem':
        """
        从字典数据创建电能系统实例
        
        Args:
            data: 包含电能系统状态的字典
            
        Returns:
            EnergySystem: 电能系统实例
        """
        energy_system = cls(
            base_energy_limit=data.get('base_energy_limit', 3),
            base_action_slots=data.get('base_action_slots', 1)
        )
        energy_system.current_energy = data.get('current_energy', energy_system.base_energy_limit)
        energy_system.generation_level = data.get('generation_level', 0)
        energy_system.accumulated_damage = data.get('accumulated_damage', 0)
        energy_system.damage_per_level = data.get('damage_per_level', 5)
        
        return energy_system
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"电能: {self.current_energy}/{self.get_energy_limit()} | 发电等级: {self.generation_level} | 累积伤害: {self.accumulated_damage}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"EnergySystem(energy={self.current_energy}/{self.get_energy_limit()}, level={self.generation_level}, damage={self.accumulated_damage})"