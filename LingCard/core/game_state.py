# LingCard/core/game_state.py
import yaml
from typing import List, Dict, Any, Optional
from .player import Player

class GameState:
    def __init__(self, state_file='game_status.yaml'):
        self.state_file = state_file
        # --- 全局信息 ---
        self.turn_order: List[int] = [] # [0, 1] 或 [1, 0]
        # --- 实时信息 ---
        self.current_round: int = 1
        self.current_player_idx: int = 0
        self.players: List[Player] = []
        self.game_over: bool = False
        self.winner: Optional[int] = None
        self.log: List[str] = [] # 游戏日志

    def get_current_player(self) -> Player:
        player_id = self.turn_order[self.current_player_idx]
        return self.players[player_id]

    def get_opponent_player(self) -> Player:
        opponent_idx = 1 - self.current_player_idx
        player_id = self.turn_order[opponent_idx]
        return self.players[player_id]

    def switch_turn(self):
        self.current_player_idx = 1 - self.current_player_idx
        if self.current_player_idx == 0:
            self.current_round += 1

    def add_log(self, message: str):
        self.log.append(message)
        if len(self.log) > 10: # 最多保留10条日志
            self.log.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'global_info': {
                'turn_order': self.turn_order,
                'player_count': len(self.players),
            },
            'live_info': {
                'current_round': self.current_round,
                'current_player_idx': self.current_player_idx,
                'game_over': self.game_over,
                'winner': self.winner,
            },
            'players': [p.to_dict() for p in self.players],
            'log': self.log,
        }

    def save(self):
        """将当前游戏状态保存到YAML文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)

    def load(self, all_char_classes, all_card_classes):
        """从YAML文件加载游戏状态"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.turn_order = data['global_info']['turn_order']
            self.current_round = data['live_info']['current_round']
            self.current_player_idx = data['live_info']['current_player_idx']
            self.game_over = data['live_info']['game_over']
            self.winner = data['live_info']['winner']
            self.players = [Player.from_dict(pd, all_char_classes, all_card_classes) for pd in data['players']]
            self.log = data.get('log', [])
            return True
        except (FileNotFoundError, KeyError):
            return False