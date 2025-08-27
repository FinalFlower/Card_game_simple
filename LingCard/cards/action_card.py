# LingCard/cards/action_card.py
from abc import ABC, abstractmethod
from LingCard.utils.enums import ActionType

class ActionCard(ABC):
    """行动卡基类"""
    def __init__(self, name: str, description: str, action_type: ActionType, energy_cost: int = 0):
        self.name = name
        self.description = description
        self.action_type = action_type
        self.energy_cost = energy_cost  # 电能消耗

    @abstractmethod
    def get_base_value(self) -> int:
        """获取行动卡的基础数值"""
        pass
    
    def can_use(self, character) -> bool:
        """
        检查角色是否可以使用该卡牌
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        return character.can_consume_energy(self.energy_cost)

    def to_dict(self):
        return {
            'class': self.__class__.__name__, 
            'name': self.name,
            'energy_cost': self.energy_cost
        }

    @classmethod
    def from_dict(cls, data, all_card_classes):
        card_class = all_card_classes.get(data['class'])
        if card_class:
            return card_class()
        raise ValueError(f"Unknown card class: {data['class']}")