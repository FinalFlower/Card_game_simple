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