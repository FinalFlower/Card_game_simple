# LingCard/core/game_engine.py
import random
from .game_state import GameState
from LingCard.cards.action_card import ActionCard
from LingCard.characters.character import Character
from LingCard.utils.enums import ActionType, TeamEffect

class GameEngine:
    def __init__(self, config):
        self.config = config

    def initialize_player_deck(self, player, card_classes):
        """根据配置初始化牌库"""
        deck = []
        for card_name, count in self.config['game_settings']['deck_composition'].items():
            card_class = card_classes[card_name]
            for _ in range(count):
                deck.append(card_class())
        random.shuffle(deck)
        player.deck = deck

    def draw_cards(self, player, count):
        """为玩家抽牌"""
        for _ in range(count):
            if not player.deck and player.discard_pile:
                player.deck = player.discard_pile
                player.discard_pile = []
                random.shuffle(player.deck)

            if player.deck:
                player.hand.append(player.deck.pop())
    
    def check_team_effects(self, player):
        char_names = {char.__class__.__name__ for char in player.characters}
        for effect_info in self.config['team_effects']:
            if all(c in char_names for c in effect_info['characters']):
                 player.team_effects.append(TeamEffect[effect_info['effect']])

    def process_turn_start(self, game_state: GameState):
        player = game_state.get_current_player()
        
        # 重置回合状态
        player.status['used_attack_this_turn'] = False
        
        # 基础抽卡
        cards_to_draw = self.config['game_settings']['initial_hand_size']
        
        # 队伍效果
        if TeamEffect.CAFE_XINHE in player.team_effects:
            cards_to_draw += 2
            game_state.add_log("队伍效果[Cafe星河]触发，额外抽2张牌")
        
        # 角色技能
        for char in player.get_alive_characters():
            char.on_turn_start(game_state, player, self)

        self.draw_cards(player, cards_to_draw)
        game_state.add_log(f"玩家{player.id} 回合开始，抽了{cards_to_draw}张牌。")

    def process_turn_end(self, game_state: GameState):
        player = game_state.get_current_player()
        for char in player.get_alive_characters():
            char.on_turn_end(game_state, player, self)
            char.reset_turn_status() # 重置回合状态
        
        game_state.add_log(f"玩家{player.id} 回合结束。")

    def execute_action(self, game_state: GameState, card_idx: int, user_char_idx: int, target_char_idx: int):
        player = game_state.get_current_player()
        opponent = game_state.get_opponent_player()

        card = player.hand.pop(card_idx)
        player.discard_pile.append(card)
        user_char = player.get_alive_characters()[user_char_idx]

        if card.action_type == ActionType.ATTACK:
            target_char = opponent.get_alive_characters()[target_char_idx]
            player.status['used_attack_this_turn'] = True  # 标记使用了攻击卡
            self._execute_attack(game_state, player, user_char, card, target_char)
        elif card.action_type == ActionType.HEAL:
            target_char = player.get_alive_characters()[target_char_idx]
            self._execute_heal(game_state, user_char, card, target_char)
        elif card.action_type == ActionType.DEFEND:
            target_char = player.get_alive_characters()[target_char_idx]
            self._execute_defend(game_state, user_char, card, target_char)
            
        self.check_game_over(game_state)

    def _execute_attack(self, game_state, player, attacker, card, target):
        damage = card.get_base_value()

        # 队伍效果
        # (此处省略了对 first_damage_dealt 状态的检查，实际应在角色状态中维护)
        if TeamEffect.JUN_LIULI in player.team_effects:
            damage += 1
            game_state.add_log("队伍效果[俊琉璃]触发，伤害+1")
        
        # 攻击者技能钩子
        damage = attacker.on_deal_damage(damage, game_state)
        
        # 目标技能钩子
        adjusted_damage, counter_damage = target.on_take_damage(damage, attacker, game_state)
        
        # 造成伤害
        actual_damage = target.take_damage(adjusted_damage)
        game_state.add_log(f"{attacker.name} 对 {target.name} 使用攻击，造成 {actual_damage} 点伤害。")

        if counter_damage > 0:
            attacker.take_damage(counter_damage)
            game_state.add_log(f"{target.name} 反击 {attacker.name}，造成 {counter_damage} 点伤害。")

    def _execute_heal(self, game_state, user, card, target):
        heal_amount = card.get_base_value()
        target.heal(heal_amount)
        game_state.add_log(f"{user.name} 对 {target.name} 使用治疗，恢复 {heal_amount} 点生命。")

    def _execute_defend(self, game_state, user, card, target):
        def_amount = card.get_base_value()
        target.add_defense(def_amount)
        game_state.add_log(f"{user.name} 对 {target.name} 使用防御，增加 {def_amount} 点防御。")

    def check_game_over(self, game_state: GameState):
        if game_state.get_current_player().is_defeated():
            game_state.game_over = True
            game_state.winner = game_state.get_opponent_player().id
        elif game_state.get_opponent_player().is_defeated():
            game_state.game_over = True
            game_state.winner = game_state.get_current_player().id