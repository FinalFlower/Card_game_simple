# LingCard/core/player.py
from typing import List, Optional, Dict, Any
from LingCard.cards.action_card import ActionCard
from LingCard.characters.character import Character
from LingCard.utils.enums import TeamEffect

class Player:
    def __init__(self, player_id: int):
        self.id = player_id
        self.characters: List[Character] = []
        self.hand: List[ActionCard] = []
        self.deck: List[ActionCard] = []
        self.discard_pile: List[ActionCard] = []
        self.team_effects: List[TeamEffect] = []
        self.status: Dict[str, Any] = {}  # 用于存储玩家状态信息

    def is_defeated(self) -> bool:
        return all(not char.is_alive for char in self.characters)

    def get_alive_characters(self) -> List[Character]:
        return [char for char in self.characters if char.is_alive]
    
    # --- 行动槽管理相关方法 ---
    
    def get_characters_with_available_action_slots(self) -> List[Character]:
        """
        获取所有可以行动的角色（存活且有可用行动槽）
        
        Returns:
            List[Character]: 可以行动的角色列表
        """
        return [char for char in self.characters if char.can_act()]
    
    def has_any_available_action_slots(self) -> bool:
        """
        检查是否有任意角色可以行动
        
        Returns:
            bool: 如果有任意角色可以行动返回True
        """
        return len(self.get_characters_with_available_action_slots()) > 0
    
    def reset_all_action_slots(self):
        """
        重置所有角色的行动槽
        """
        for char in self.characters:
            if char.is_alive:
                # 使用新的ActionSlotManager系统
                if hasattr(char, 'action_slot_manager'):
                    char.action_slot_manager.reset_all_slots()
    
    def get_action_slots_summary(self) -> Dict[str, Any]:
        """
        获取所有角色的行动槽状态总结
        
        Returns:
            Dict: 包含行动槽状态信息的字典
        """
        summary = {
            'total_characters': len(self.characters),
            'alive_characters': len(self.get_alive_characters()),
            'characters_with_action_slots': len(self.get_characters_with_available_action_slots()),
            'character_details': []
        }
        
        for char in self.characters:
            char_info = {
                'name': char.name,
                'is_alive': char.is_alive,
                'action_slot_status': None
            }
            
            if char.is_alive:
                # 使用新的get_action_slot_status方法
                char_info['action_slot_status'] = char.get_action_slot_status()
            
            summary['character_details'].append(char_info)
        
        return summary

    def to_dict(self):
        return {
            'id': self.id,
            'characters': [char.to_dict() for char in self.characters],
            'hand': [card.to_dict() for card in self.hand],
            'deck': [card.to_dict() for card in self.deck],
            'discard_pile': [card.to_dict() for card in self.discard_pile],
            'team_effects': [effect.name for effect in self.team_effects],
            'status': self.status,
        }

    @classmethod
    def from_dict(cls, data, all_char_classes, all_card_classes):
        player = cls(data['id'])
        player.characters = [Character.from_dict(cd, all_char_classes) for cd in data['characters']]
        player.hand = [ActionCard.from_dict(cd, all_card_classes) for cd in data['hand']]
        player.deck = [ActionCard.from_dict(cd, all_card_classes) for cd in data['deck']]
        player.discard_pile = [ActionCard.from_dict(cd, all_card_classes) for cd in data['discard_pile']]
        player.team_effects = [TeamEffect[name] for name in data['team_effects']]
        player.status = data.get('status', {})
        return player