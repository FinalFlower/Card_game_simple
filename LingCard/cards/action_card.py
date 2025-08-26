# LingCard/cards/action_card.py
from abc import ABC, abstractmethod
from LingCard.utils.enums import ActionType

class ActionCard(ABC):
    """行动卡基类"""
    def __init__(self, name: str, description: str, action_type: ActionType):
        self.name = name
        self.description = description
        self.action_type = action_type

    @abstractmethod
    def get_base_value(self) -> int:
        """获取行动卡的基础数值"""
        pass

    def to_dict(self):
        return {'class': self.__class__.__name__, 'name': self.name}

    @classmethod
    def from_dict(cls, data, all_card_classes):
        card_class = all_card_classes.get(data['class'])
        if card_class:
            return card_class()
        raise ValueError(f"Unknown card class: {data['class']}")