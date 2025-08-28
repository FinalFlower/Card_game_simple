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
        
        # --- 新增：延迟效果系统 ---
        self.delayed_effects: List[Dict[str, Any]] = []  # 延迟效果列表
        self.removed_cards: set = set()  # 已移除的卡牌类型集合

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
    
    # --- 延迟效果系统 ---
    def add_delayed_effect(self, effect: Dict[str, Any]):
        """
        添加延迟效果
        
        Args:
            effect: 延迟效果字典，包含 type, target_player, trigger_turn 等字段
        """
        self.delayed_effects.append(effect)
        self.add_log(f"添加延迟效果: {effect.get('description', '未知效果')}")
    
    def get_next_turn_for_player(self, player_name: str) -> int:
        """
        获取指定玩家的下一回合数
        
        Args:
            player_name: 玩家名称
            
        Returns:
            int: 下一回合数
        """
        # 找到玩家在回合顺序中的位置
        player_idx = None
        for i, player in enumerate(self.players):
            if f"player_{player.id}" == player_name:
                player_idx = i
                break
        
        if player_idx is None:
            return self.current_round + 1  # 默认返回下一回合
        
        # 计算该玩家的下一回合
        if player_idx in self.turn_order:
            current_turn_idx = self.turn_order.index(player_idx)
            if current_turn_idx == self.current_player_idx:
                # 如果是当前玩家，下一回合的计算：
                # 对于双人游戏：玩家1回合 -> 玩家2回合 -> 玩家1下一回合
                # 当前是第N回合，下一个自身回合是第N+2回合
                return self.current_round + len(self.turn_order)
            else:
                # 如果不是当前玩家，计算到下一次轮到该玩家需要多少步
                steps_to_next_turn = (current_turn_idx - self.current_player_idx) % len(self.turn_order)
                if steps_to_next_turn == 0:
                    steps_to_next_turn = len(self.turn_order)
                return self.current_round + steps_to_next_turn
        
        return self.current_round + 1
    
    def process_delayed_effects(self, current_turn: int, current_player_name: str):
        """
        处理当前回合触发的延迟效果
        
        Args:
            current_turn: 当前回合数
            current_player_name: 当前玩家名称
        """
        effects_to_remove = []
        
        for i, effect in enumerate(self.delayed_effects):
            # 检查是否到达触发条件
            if (effect.get('trigger_turn', 0) == current_turn and 
                effect.get('target_player', '') == current_player_name):
                
                # 执行延迟效果
                self._execute_delayed_effect(effect)
                effects_to_remove.append(i)
        
        # 移除已执行的效果（从后往前移除避免索引问题）
        for i in reversed(effects_to_remove):
            self.delayed_effects.pop(i)
    
    def process_turn_end_effects(self, current_turn: int, current_player_name: str):
        """
        处理回合结束时立即触发的延迟效果
        
        Args:
            current_turn: 当前回合数
            current_player_name: 当前玩家名称
        """
        effects_to_remove = []
        
        for i, effect in enumerate(self.delayed_effects):
            # 检查是否为回合结束时触发的效果
            if (effect.get('trigger_type', '') == 'turn_end' and 
                effect.get('trigger_turn', 0) == current_turn and 
                effect.get('target_player', '') == current_player_name):
                
                # 执行延迟效果
                self._execute_delayed_effect(effect)
                effects_to_remove.append(i)
        
        # 移除已执行的效果（从后往前移除避免索引问题）
        for i in reversed(effects_to_remove):
            self.delayed_effects.pop(i)
    
    def _execute_delayed_effect(self, effect: Dict[str, Any]):
        """
        执行具体的延迟效果
        
        Args:
            effect: 延迟效果字典
        """
        effect_type = effect.get('type', '')
        target_player_name = effect.get('target_player', '')
        
        # 找到目标玩家
        target_player = self.get_player_by_name(target_player_name)
        if not target_player:
            self.add_log(f"找不到玩家 {target_player_name}，延迟效果执行失败")
            return
        
        if effect_type == 'draw_card':
            # 抽卡效果
            amount = effect.get('amount', 1)
            # 使用游戏引擎的抽卡方法
            from LingCard.core.game_engine import GameEngine
            game_engine = GameEngine({})
            drawn = game_engine.draw_cards(target_player, amount)
            self.add_log(f"player_{target_player.id} 因延迟效果抽取了 {drawn} 张卡牌")
        
        elif effect_type == 'restore_energy':
            # 恢复电能效果
            amount = effect.get('amount', 1)
            # 对所有存活角色恢复电能
            for char in target_player.get_alive_characters():
                char.energy_system.restore_energy(amount)
            self.add_log(f"player_{target_player.id} 因延迟效果恢复了 {amount} 点电能")
        
        elif effect_type == 'add_card_to_hand':
            # 向手中添加特定卡牌
            card_class = effect.get('card_class')
            if card_class:
                new_card = card_class()
                target_player.hand.append(new_card)
                self.add_log(f"player_{target_player.id} 因延迟效果获得了 {new_card.name}")
        
        else:
            self.add_log(f"未知的延迟效果类型: {effect_type}")
    
    def get_player_by_name(self, player_name: str) -> Optional[Player]:
        """
        根据名称获取玩家
        
        Args:
            player_name: 玩家名称（格式为 "player_{id}"）
            
        Returns:
            Optional[Player]: 玩家对象或None
        """
        for player in self.players:
            if f"player_{player.id}" == player_name:
                return player
        return None

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
            'delayed_effects': self.delayed_effects,  # 新增
            'removed_cards': list(self.removed_cards),  # 新增
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
            
            # 加载延迟效果和移除的卡牌（兼容旧版本）
            self.delayed_effects = data.get('delayed_effects', [])
            self.removed_cards = set(data.get('removed_cards', []))
            return True
        except (FileNotFoundError, KeyError):
            return False