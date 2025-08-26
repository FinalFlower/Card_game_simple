# LingCard/game_manager.py
import yaml
import random
import time
from LingCard.utils.enums import GamePhase, ActionType
from LingCard.core.game_state import GameState
from LingCard.core.player import Player
from LingCard.core.game_engine import GameEngine
from LingCard.utils.loader import load_characters, load_cards
from LingCard.ui.tui import TUI

class GameManager:
    def __init__(self, config_path='config.yaml', state_path='game_status.yaml'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.tui = TUI()
        self.state_path = state_path
        self.game_state = GameState(self.state_path)
        self.engine = GameEngine(self.config)
        
        self.all_characters = load_characters()
        self.all_cards = load_cards()
        self.phase = GamePhase.INITIALIZING
        self.vs_ai = False

    def run(self):
        """游戏主状态机"""
        while self.phase != GamePhase.EXIT:
            if self.phase == GamePhase.INITIALIZING:
                self._phase_initializing()
            elif self.phase == GamePhase.MODE_SELECTION:
                self._phase_mode_selection()
            elif self.phase == GamePhase.CHARACTER_SELECTION:
                self._phase_character_selection()
            elif self.phase == GamePhase.PLAYER_TURN:
                self._phase_player_turn()
            # --- 新增 AI 回合处理 ---
            elif self.phase == GamePhase.AI_TURN:
                self._phase_ai_turn()
            # ------------------------
            elif self.phase == GamePhase.TURN_END:
                self._phase_turn_end()
            elif self.phase == GamePhase.GAME_OVER:
                self._phase_game_over()
        
        print("游戏已退出。")

    def _phase_initializing(self):
        # 此处可以加入加载存档的逻辑
        self.game_state = GameState(self.state_path)
        self.phase = GamePhase.MODE_SELECTION

    def _phase_mode_selection(self):
        choice = self.tui.select_from_list("请选择游戏模式", ["玩家 vs 玩家", "玩家 vs AI"])
        if choice == 0: self.vs_ai = False
        elif choice == 1: self.vs_ai = True
        self.phase = GamePhase.CHARACTER_SELECTION

    def _phase_character_selection(self):
        self.game_state.players = [Player(1), Player(2)]
        
        # 玩家1选择
        self._select_chars_for_player(self.game_state.players[0], "玩家1")
        # 玩家2/AI选择
        if self.vs_ai:
            self._ai_select_chars(self.game_state.players[1])
        else:
            self._select_chars_for_player(self.game_state.players[1], "玩家2")
            
        # 初始化牌库和队伍效果
        for player in self.game_state.players:
            self.engine.initialize_player_deck(player, self.all_cards)
            self.engine.check_team_effects(player)
        
        # 决定先手
        self.game_state.turn_order = [0, 1]
        random.shuffle(self.game_state.turn_order)
        self.game_state.add_log(f"随机决定，玩家 {self.game_state.turn_order[0]+1} 先手！")
        
        # 回合开始
        self.engine.process_turn_start(self.game_state)
        self.game_state.save()
        self.phase = GamePhase.PLAYER_TURN

    def _select_chars_for_player(self, player, player_name):
        available_chars = list(self.all_characters.values())
        for i in range(self.config['game_settings']['characters_per_player']):
            prompt = f"{player_name} 请选择第 {i+1} 个角色"
            options = [f"{c().name} - {c().description}" for c in available_chars]
            choice_idx = self.tui.select_from_list(prompt, options)
            
            chosen_char_class = available_chars.pop(choice_idx)
            char_instance = chosen_char_class()
            # 从config加载HP
            char_instance.max_hp = self.config['game_settings']['initial_hp']
            char_instance.current_hp = char_instance.max_hp
            player.characters.append(char_instance)

    def _ai_select_chars(self, player):
        available_chars = list(self.all_characters.values())
        random.shuffle(available_chars)
        for i in range(self.config['game_settings']['characters_per_player']):
            chosen_char_class = available_chars.pop(0)
            char_instance = chosen_char_class()
            char_instance.max_hp = self.config['game_settings']['initial_hp']
            char_instance.current_hp = char_instance.max_hp
            player.characters.append(char_instance)
        self.tui.show_message("AI 已选择角色。")

    def _phase_player_turn(self):
        player = self.game_state.get_current_player()
        
        while True:
            options = [f"使用: {card.name}" for card in player.hand] + ["结束回合"]
            card_choice = self.tui.select_from_list("选择你的行动", options, self.game_state)
            
            if card_choice == -1 or card_choice == len(player.hand): # 结束回合
                break
            
            # 使用卡牌
            card = player.hand[card_choice]
            
            # 选择使用者
            user_options = [c.name for c in player.get_alive_characters()]
            user_choice = self.tui.select_from_list("选择使用角色", user_options, self.game_state)
            if user_choice == -1: continue

            # 选择目标
            if card.action_type == ActionType.ATTACK:
                targets = self.game_state.get_opponent_player().get_alive_characters()
            else:
                targets = player.get_alive_characters()
            
            target_options = [c.name for c in targets]
            target_choice = self.tui.select_from_list(f"选择 '{card.name}' 的目标", target_options, self.game_state)
            if target_choice == -1: continue

            # 执行
            self.engine.execute_action(self.game_state, card_choice, user_choice, target_choice)
            self.game_state.save()
            
            if self.game_state.game_over:
                self.phase = GamePhase.GAME_OVER
                return
        
        self.phase = GamePhase.TURN_END

    # --- 新增 AI 回合完整逻辑 ---
    def _phase_ai_turn(self):
        player = self.game_state.get_current_player()
        opponent = self.game_state.get_opponent_player()
        
        self.tui.render_and_show_message(self.game_state, f"AI (玩家 {player.id}) 正在思考...", 1.5)

        actions_taken = False
        # 从后往前遍历手牌，这样在执行动作（pop牌）时不会影响后续遍历的索引
        for card_idx, card in reversed(list(enumerate(player.hand))):
            alive_ai_chars = player.get_alive_characters()
            
            if not alive_ai_chars:
                break # AI没有存活角色，无法行动

            # 简化：总是让第一个存活的角色使用卡牌
            user_char = alive_ai_chars[0]
            user_char_idx = 0
            
            target_char = None
            target_idx = -1

            if card.action_type == ActionType.ATTACK:
                targets = opponent.get_alive_characters()
                if targets:
                    # 攻击血量最少的目标
                    target_char = min(targets, key=lambda c: c.current_hp)
                    target_idx = targets.index(target_char)

            elif card.action_type == ActionType.HEAL:
                targets = player.get_alive_characters()
                # 寻找受伤最严重的角色
                heal_candidates = [c for c in targets if c.current_hp < c.max_hp]
                if heal_candidates:
                    target_char = min(heal_candidates, key=lambda c: c.current_hp)
                    target_idx = targets.index(target_char)
            
            elif card.action_type == ActionType.DEFEND:
                targets = player.get_alive_characters()
                if targets:
                    # 防御血量最少的角色
                    target_char = min(targets, key=lambda c: c.current_hp)
                    target_idx = targets.index(target_char)

            # 如果找到了合法的目标，则执行行动
            if target_char and target_idx != -1:
                actions_taken = True
                msg = f"AI 使用 [{user_char.name}] 对 [{target_char.name}] 打出了 [{card.name}]"
                self.tui.render_and_show_message(self.game_state, msg, 2)
                
                self.engine.execute_action(self.game_state, card_idx, user_char_idx, target_idx)
                self.game_state.save()
                
                if self.game_state.game_over:
                    self.phase = GamePhase.GAME_OVER
                    return

        if not actions_taken:
            self.tui.render_and_show_message(self.game_state, "AI 选择不出牌，结束回合。", 2)
        
        self.phase = GamePhase.TURN_END
    # --------------------------------

    def _phase_turn_end(self):
        self.engine.process_turn_end(self.game_state)
        self.game_state.switch_turn()
        self.engine.process_turn_start(self.game_state)
        self.game_state.save()
        
        # --- 修改 AI 回合切换逻辑 ---
        next_player = self.game_state.get_current_player()
        if self.vs_ai and next_player.id == 2:
            self.phase = GamePhase.AI_TURN
        else:
            self.phase = GamePhase.PLAYER_TURN
        # ---------------------------

    def _phase_game_over(self):
        winner_id = self.game_state.winner
        msg = f"游戏结束！玩家 {winner_id} 胜利！"
        self.tui.render_and_show_message(self.game_state, msg, 3)
        
        if self.tui.confirm("要再来一局吗？"):
            self.phase = GamePhase.INITIALIZING
        else:
            self.phase = GamePhase.EXIT