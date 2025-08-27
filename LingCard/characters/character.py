from typing import Dict, Any
from LingCard.core.action_slot import ActionSlot, ActionSlotType, ActionSlotManager
from LingCard.core.energy_system import EnergySystem

class Character:
    """人物卡基类"""
    def __init__(self, name: str, description: str, max_hp: int = 10, 
                 base_energy_limit: int = 3, damage_per_level: int = 5):
        self.name = name
        self.description = description
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.defense_buff = 0
        self.is_alive = True
        self.status: Dict[str, Any] = {} # 用于存储各种技能状态
        
        # 电能系统配置（子类可重写）
        self.base_energy_limit = base_energy_limit
        self.damage_per_level = damage_per_level
        
        # 电能系统
        self.energy_system = EnergySystem(
            base_energy_limit=self.base_energy_limit,
            base_action_slots=1
        )
        self.energy_system.damage_per_level = self.damage_per_level
        
        # 行动槽系统（使用ActionSlotManager管理多个独立行动槽）
        self.action_slot_manager = ActionSlotManager()
        # 初始化一个基础行动槽
        self.action_slot_manager.add_slot(ActionSlot(ActionSlotType.BASIC, max_uses=1))

    def take_damage(self, damage: int) -> int:
        """基础受到伤害逻辑"""
        actual_damage = max(0, damage - self.defense_buff)
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        if self.defense_buff > 0:
            reduced_damage = min(damage, self.defense_buff)
            self.defense_buff = max(0, self.defense_buff - damage)
        
        if self.current_hp <= 0:
            self.is_alive = False
        return actual_damage

    def heal(self, amount: int):
        if not self.is_alive: return
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def add_defense(self, amount: int):
        self.defense_buff += amount
    
    # --- 行动槽相关方法 ---
    
    def can_act(self) -> bool:
        """
        检查角色是否可以行动
        
        Returns:
            bool: 如果角色存活且有可用的行动槽返回True
        """
        return self.is_alive and self.action_slot_manager.has_available_slot()
    
    # --- 电能系统相关方法 ---
    
    def can_consume_energy(self, amount: int) -> bool:
        """
        检查是否可以消耗指定电能
        
        Args:
            amount: 要消耗的电能量
            
        Returns:
            bool: 是否可以消耗
        """
        return self.energy_system.can_consume_energy(amount)
    
    def consume_energy(self, amount: int) -> bool:
        """
        消耗电能
        
        Args:
            amount: 要消耗的电能量
            
        Returns:
            bool: 是否成功消耗
        """
        return self.energy_system.consume_energy(amount)
    
    def get_energy_status(self) -> Dict[str, Any]:
        """
        获取电能系统状态
        
        Returns:
            Dict: 电能系统状态信息
        """
        return self.energy_system.get_status()
    
    def add_damage_to_generation(self, damage: int, game_state=None) -> bool:
        """
        添加累积伤害，可能触发发电等级提升
        
        Args:
            damage: 造成的伤害量
            game_state: 游戏状态（用于记录日志）
            
        Returns:
            bool: 是否发电等级提升了
        """
        level_up = self.energy_system.add_damage(damage)
        if level_up and game_state:
            status = self.energy_system.get_status()
            game_state.add_log(f"{self.name} 发电等级提升到 {status['generation_level']} 级！")
            game_state.add_log(f"电能上限增加到 {status['energy_limit']} 点，行动槽增加到 {status['action_slots_count']} 个")
        return level_up
    
    def update_action_slots_from_energy(self):
        """
        根据电能系统更新行动槽数量
        """
        target_slots = self.energy_system.get_action_slots_count()
        current_slots = len(self.action_slot_manager.action_slots)
        
        # 如果需要更多行动槽
        while current_slots < target_slots:
            new_slot = ActionSlot(ActionSlotType.BASIC, max_uses=1)
            self.action_slot_manager.add_slot(new_slot)
            current_slots += 1
        
        # 如果行动槽太多（理论上不应该发生，但为了安全）
        while current_slots > target_slots:
            if self.action_slot_manager.action_slots:
                self.action_slot_manager.action_slots.pop()
            current_slots -= 1
    
    def try_use_action_slot(self) -> bool:
        """
        尝试使用行动槽
        
        Returns:
            bool: 如果成功使用行动槽返回True，否则返回False
        """
        if not self.is_alive:
            return False
        return self.action_slot_manager.use_any_available_slot()
    
    def get_action_slot_status(self) -> Dict[str, Any]:
        """
        获取行动槽状态信息
        
        Returns:
            Dict: 行动槽状态信息
        """
        all_slots_status = self.action_slot_manager.get_all_status()
        available_count = sum(1 for slot in all_slots_status if slot['can_use'])
        total_count = len(all_slots_status)
        
        return {
            'total_slots': total_count,
            'available_slots': available_count,
            'used_slots': total_count - available_count,
            'slots_detail': all_slots_status
        }

    def reset_turn_status(self):
        """重置回合状态，可在子类中重写"""
        # 电能系统回合重置（每回合回复1点电能）
        self.energy_system.reset_turn()
        
        # 更新行动槽数量（基于发电等级）
        self.update_action_slots_from_energy()
        
        # 重置所有行动槽
        self.action_slot_manager.reset_all_slots()
        # 例子: self.status['first_damage_dealt'] = False
        pass

    def to_dict(self):
        return {
            'class': self.__class__.__name__,
            'name': self.name,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'defense_buff': self.defense_buff,
            'is_alive': self.is_alive,
            'status': self.status,
            'action_slots': [slot.to_dict() for slot in self.action_slot_manager.action_slots],
            'energy_system': self.energy_system.to_dict(),
            'base_energy_limit': self.base_energy_limit,
            'damage_per_level': self.damage_per_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict, all_char_classes: Dict):
        char_class = all_char_classes.get(data['class'])
        if not char_class:
            raise ValueError(f"Unknown character class: {data['class']}")
        
        # 使用空的构造函数创建实例，然后填充属性
        instance = char_class()
        instance.max_hp = data.get('max_hp', instance.max_hp)
        instance.current_hp = data.get('current_hp')
        instance.defense_buff = data.get('defense_buff')
        instance.is_alive = data.get('is_alive')
        instance.status = data.get('status', {})
        
        # 加载电能系统数据（向后兼容）
        if 'energy_system' in data:
            instance.energy_system = EnergySystem.from_dict(data['energy_system'])
        if 'base_energy_limit' in data:
            instance.base_energy_limit = data['base_energy_limit']
        if 'damage_per_level' in data:
            instance.damage_per_level = data['damage_per_level']
        
        # 加载行动槽数据（向后兼容）
        if 'action_slots' in data:
            # 新格式：多个行动槽
            instance.action_slot_manager = ActionSlotManager()
            for slot_data in data['action_slots']:
                slot = ActionSlot.from_dict(slot_data)
                instance.action_slot_manager.add_slot(slot)
        elif 'action_slot' in data:
            # 旧格式：单个行动槽（向后兼容）
            instance.action_slot_manager = ActionSlotManager()
            old_slot = ActionSlot.from_dict(data['action_slot'])
            instance.action_slot_manager.add_slot(old_slot)
        
        return instance

    # --- HOOKS for skills ---
    # 引擎将在特定时机调用这些钩子函数
    
    def on_deal_damage(self, damage: int, game_state) -> int:
        """造成伤害时的钩子，返回调整后的伤害值"""
        # 基类实现：不在这里累积伤害，由GameEngine在实际伤害后处理
        # 子类可以重写这个方法来修改伤害值
        return damage

    def on_take_damage(self, damage: int, attacker, game_state) -> (int, int): # type: ignore
        """受到伤害时的钩子，返回 (调整后的伤害, 对攻击者的反击伤害)"""
        return (damage, 0)
    
    def on_turn_start(self, game_state, player, engine=None):
        """回合开始时的钩子"""
        pass

    def on_turn_end(self, game_state, player, engine=None):
        """回合结束时的钩子"""
        pass