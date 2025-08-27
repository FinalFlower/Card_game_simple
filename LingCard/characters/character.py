from typing import Dict, Any
from LingCard.core.action_slot import ActionSlot, ActionSlotType

class Character:
    """人物卡基类"""
    def __init__(self, name: str, description: str, max_hp: int = 10):
        self.name = name
        self.description = description
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.defense_buff = 0
        self.is_alive = True
        self.status: Dict[str, Any] = {} # 用于存储各种技能状态
        
        # 行动槽系统
        self.action_slot = ActionSlot(ActionSlotType.BASIC, max_uses=1)

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
        return self.is_alive and self.action_slot.can_use()
    
    def try_use_action_slot(self) -> bool:
        """
        尝试使用行动槽
        
        Returns:
            bool: 如果成功使用行动槽返回True，否则返回False
        """
        if not self.is_alive:
            return False
        return self.action_slot.use_slot()
    
    def get_action_slot_status(self) -> Dict[str, Any]:
        """
        获取行动槽状态信息
        
        Returns:
            Dict: 行动槽状态信息
        """
        return self.action_slot.get_status()

    def reset_turn_status(self):
        """重置回合状态，可在子类中重写"""
        # 重置行动槽
        self.action_slot.reset_turn()
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
            'action_slot': self.action_slot.to_dict(),
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
        
        # 加载行动槽数据（向后兼容）
        if 'action_slot' in data:
            instance.action_slot = ActionSlot.from_dict(data['action_slot'])
        
        return instance

    # --- HOOKS for skills ---
    # 引擎将在特定时机调用这些钩子函数
    
    def on_deal_damage(self, damage: int, game_state) -> int:
        """造成伤害时的钩子，返回调整后的伤害值"""
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