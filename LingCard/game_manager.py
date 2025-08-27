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
        
        # 根据先手玩家和游戏模式决定初始回合类型
        current_player = self.game_state.get_current_player()
        if self.vs_ai and current_player.id == 2:
            self.phase = GamePhase.AI_TURN
        else:
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
        
        # 主要AI行动循环
        while True:
            # 检查是否还有可以行动的角色
            can_act_chars = [char for char in player.get_alive_characters() if char.can_act()]
            if not can_act_chars:
                self.tui.render_and_show_message(self.game_state, "AI 的所有角色都已用完行动槽，结束回合。", 2)
                break
            
            # 查找可执行的行动（卡牌+角色组合）
            possible_actions = []
            
            for card_idx, card in enumerate(player.hand):
                for char_idx, char in enumerate(can_act_chars):
                    # 检查角色是否有足够电能使用该卡牌
                    if not char.can_consume_energy(card.energy_cost):
                        continue
                    
                    # 根据卡牌类型找到合适的目标
                    targets = []
                    if card.action_type == ActionType.ATTACK:
                        targets = opponent.get_alive_characters()
                    elif card.action_type == ActionType.HEAL:
                        # 只对受伤的角色使用治疗
                        targets = [c for c in player.get_alive_characters() if c.current_hp < c.max_hp]
                    elif card.action_type == ActionType.DEFEND:
                        targets = player.get_alive_characters()
                    
                    # 为每个可能的目标创建行动选项
                    for target_idx, target in enumerate(targets):
                        action_priority = self._calculate_action_priority(card, char, target, player, opponent)
                        possible_actions.append({
                            'card_idx': card_idx,
                            'user_char': char,
                            'user_char_idx': player.get_alive_characters().index(char),
                            'target_char': target,
                            'target_idx': target_idx,
                            'card': card,
                            'priority': action_priority
                        })
            
            # 如果没有可执行的行动，结束回合
            if not possible_actions:
                reason = "没有足够电能或合适目标" if can_act_chars else "所有角色已用完行动槽"
                self.tui.render_and_show_message(self.game_state, f"AI {reason}，结束回合。", 2)
                break
            
            # 选择优先级最高的行动
            best_action = max(possible_actions, key=lambda x: x['priority'])
            
            # 执行最佳行动
            actions_taken = True
            msg = f"AI 使用 [{best_action['user_char'].name}] 对 [{best_action['target_char'].name}] 打出了 [{best_action['card'].name}]"
            self.tui.render_and_show_message(self.game_state, msg, 2)
            
            self.engine.execute_action(
                self.game_state, 
                best_action['card_idx'], 
                best_action['user_char_idx'], 
                best_action['target_idx']
            )
            self.game_state.save()
            
            if self.game_state.game_over:
                self.phase = GamePhase.GAME_OVER
                return

        if not actions_taken:
            self.tui.render_and_show_message(self.game_state, "AI 选择不出牌，结束回合。", 2)
        
        self.phase = GamePhase.TURN_END
    
    def _calculate_action_priority(self, card, user_char, target_char, player, opponent):
        """
        计算AI行动的优先级
        
        Args:
            card: 要使用的卡牌
            user_char: 使用卡牌的角色
            target_char: 目标角色
            player: AI玩家
            opponent: 对手玩家
            
        Returns:
            float: 行动优先级，数值越高优先级越高
        """
        priority = 0.0
        
        if card.action_type == ActionType.ATTACK:
            # 攻击优先级：优先攻击血量低的敌人，能击杀的优先级更高
            damage = card.get_base_value()
            if target_char.current_hp <= damage:
                priority += 100  # 击杀优先级很高
            else:
                priority += 50 - target_char.current_hp  # 血量越低优先级越高
                
        elif card.action_type == ActionType.HEAL:
            # 治疗优先级：优先治疗血量最低的角色
            heal_amount = card.get_base_value()
            missing_hp = target_char.max_hp - target_char.current_hp
            if missing_hp > 0:
                priority += min(heal_amount, missing_hp) * 10  # 实际治疗量越多优先级越高
                priority += (target_char.max_hp - target_char.current_hp) * 2  # 缺血越多优先级越高
                
        elif card.action_type == ActionType.DEFEND:
            # 防御优先级：优先保护血量低的角色
            if target_char.current_hp < target_char.max_hp * 0.5:
                priority += 30  # 半血以下角色防御优先级较高
            else:
                priority += 10  # 基础防御优先级
        
        # 电能效率考虑：剩余电能较少时，优先使用低耗能卡牌
        energy_ratio = user_char.energy_system.current_energy / user_char.energy_system.get_energy_limit()
        if energy_ratio < 0.5:  # 电能不足一半时
            priority -= card.energy_cost * 5  # 降低高耗能卡牌的优先级
        
        return priority
    # --------------------------------

    def _phase_turn_end(self):
        self.engine.process_turn_end(self.game_state)
        self.game_state.switch_turn()
        self.engine.process_turn_start(self.game_state)
        self.game_state.save()
        
        # 根据游戏模式和当前玩家决定下一个回合类型
        current_player = self.game_state.get_current_player()
        if self.vs_ai and current_player.id == 2:
            self.phase = GamePhase.AI_TURN
        else:
            self.phase = GamePhase.PLAYER_TURN

    def _phase_game_over(self):
        winner_id = self.game_state.winner
        msg = f"游戏结束！玩家 {winner_id} 胜利！"
        self.tui.render_and_show_message(self.game_state, msg, 3)
        
        if self.tui.confirm("要再来一局吗？"):
            self.phase = GamePhase.INITIALIZING
        else:
            self.phase = GamePhase.EXIT