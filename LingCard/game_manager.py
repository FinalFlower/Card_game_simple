# LingCard/game_manager.py
import yaml
import random
import time
from typing import Dict
from LingCard.utils.enums import GamePhase, ActionType
from LingCard.core.buff_system import BuffType
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
            elif self.phase == GamePhase.LOBBY:
                self._phase_lobby()
            elif self.phase == GamePhase.DECK_BUILDER:
                self._phase_deck_builder()
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
        """初始化阶段 - 检查是否有存档并询问是否继续"""
        # 尝试加载存档文件
        temp_game_state = GameState(self.state_path)
        
        # 检查存档文件是否存在且有效
        if temp_game_state.load(self.all_characters, self.all_cards):
            # 存档存在，检查游戏状态
            if temp_game_state.game_over:
                # 游戏已结束，询问是否开始新游戏
                self.tui.show_message("检测到已完成的游戏存档。")
                if self.tui.confirm("要开始新游戏吗？"):
                    # 删除旧存档，开始新游戏
                    import os
                    if os.path.exists(self.state_path):
                        os.remove(self.state_path)
                    self.game_state = GameState(self.state_path)
                    self.phase = GamePhase.LOBBY
                else:
                    # 用户选择不开始新游戏，退出
                    self.phase = GamePhase.EXIT
            else:
                # 游戏进行中，询问是否继续
                current_round = temp_game_state.current_round
                self.tui.show_message(f"检测到第{current_round}回合的游戏存档。")
                if self.tui.confirm("要继续这局游戏吗？"):
                    # 继续游戏
                    self.game_state = temp_game_state
                    
                    # 根据当前玩家和游戏状态确定下一阶段
                    current_player = self.game_state.get_current_player()
                    
                    # 这里需要从存档中恢复游戏模式信息
                    # 简单判断：如果玩家2的ID是2且没有手动输入痕迹，可能是AI
                    if len(self.game_state.players) >= 2 and self.game_state.players[1].id == 2:
                        # 假设ID为2的玩家是AI（这是一个简化的判断）
                        self.vs_ai = True
                    
                    if self.vs_ai and current_player.id == 2:
                        self.phase = GamePhase.AI_TURN
                    else:
                        self.phase = GamePhase.PLAYER_TURN
                else:
                    # 用户选择不继续，开始新游戏
                    import os
                    if os.path.exists(self.state_path):
                        os.remove(self.state_path)
                    self.game_state = GameState(self.state_path)
                    self.phase = GamePhase.LOBBY
        else:
            # 没有有效存档，开始新游戏
            self.game_state = GameState(self.state_path)
            self.phase = GamePhase.LOBBY

    def _phase_lobby(self):
        """大厅阶段 - 显示主菜单"""
        self.tui.clear_screen()
        
        # 显示游戏标题
        title = "=== LingCard 卡牌对战遊戏 ==="
        self.tui.safe_print(title)
        self.tui.safe_print("")  # 空行
        
        # 主菜单选项
        lobby_options = [
            "开始游戏",
            "配卡界面",
            "退出游戏"
        ]
        
        choice = self.tui.select_from_list("请选择操作", lobby_options)
        
        if choice == 0:  # 开始游戏
            self.phase = GamePhase.MODE_SELECTION
        elif choice == 1:  # 配卡界面
            self.phase = GamePhase.DECK_BUILDER
        elif choice == 2 or choice == -1:  # 退出游戏或ESC
            self.phase = GamePhase.EXIT
    
    def _phase_deck_builder(self):
        """配卡界面阶段 - 实现直观的牌库配置功能"""
        # 创建一个临时玩家用于配卡
        temp_player = Player(1)
        
        # 初始化默认配置（如果玩家没有自定义配置）
        saved_config = self._load_deck_config()
        if saved_config:
            temp_player.set_custom_deck_config(saved_config)
        else:
            default_config = {
                'AttackCard': 3,
                'HealCard': 2,
                'DefendCard': 3,
                'PoisonCard': 1,
                'DrawTestCard': 1
            }
            temp_player.set_custom_deck_config(default_config)
        
        while True:
            self.tui.clear_screen()
            
            # 显示标题
            title = "=== 配卡界面 ==="
            self.tui.safe_print(title)
            self.tui.safe_print("")
            
            # 显示当前牌库配置
            current_config = temp_player.get_deck_config()
            total_cards = sum(current_config.values())
            
            self.tui.safe_print(f"当前牌库（{total_cards}/10张）：")
            if current_config:
                for card_name, count in current_config.items():
                    card_display_name = self._get_card_display_name(card_name)
                    self.tui.safe_print(f"  {card_display_name}: {count}张")
            else:
                self.tui.safe_print("  空")
            
            self.tui.safe_print("")
            
            # 显示所有可用卡牌选项
            self.tui.safe_print("左键点击添加卡牌，右键点击移除卡牌：")
            available_cards = list(self.all_cards.keys())
            card_options = []
            for card_name in available_cards:
                display_name = self._get_card_display_name(card_name)
                current_count = current_config.get(card_name, 0)
                card_options.append(f"{display_name} (当前: {current_count}张)")
            
            # 添加功能按钮
            card_options.extend([
                "--- 功能操作 ---",
                "移除卡牌模式",
                "清空牌库",
                "保存配置",
                "返回大厅"
            ])
            
            choice = self.tui.select_from_list("选择操作", card_options)
            
            if choice == -1:  # ESC
                self.phase = GamePhase.LOBBY
                break
            elif choice < len(available_cards):  # 选择了卡牌
                card_name = available_cards[choice]
                if total_cards < 10:
                    if temp_player.add_card_to_deck_config(card_name, 1):
                        display_name = self._get_card_display_name(card_name)
                        # 不显示成功信息，直接刷新界面
                        pass
                    else:
                        self.tui.show_message("添加失败！")
                else:
                    self.tui.show_message("牌库已满（10/10）！")
            elif choice == len(available_cards) + 1:  # 移除卡牌模式
                self._deck_builder_remove_mode(temp_player)
            elif choice == len(available_cards) + 2:  # 清空牌库
                if self.tui.confirm("确定要清空当前牌库吗？"):
                    temp_player.clear_deck_config()
                    self.tui.show_message("牌库已清空")
            elif choice == len(available_cards) + 3:  # 保存配置
                if total_cards == 10:
                    self._save_deck_config(current_config)
                    self.tui.show_message("配置已保存！将在下次游戏中生效")
                else:
                    self.tui.show_message(f"牌库不完整！还需要 {10 - total_cards} 张卡")
            elif choice == len(available_cards) + 4:  # 返回大厅
                self.phase = GamePhase.LOBBY
                break
    
    def _get_card_display_name(self, card_class_name: str) -> str:
        """获取卡牌的显示名称"""
        display_names = {
            'AttackCard': '攻击卡',
            'HealCard': '治疗卡', 
            'DefendCard': '防御卡',
            'PoisonCard': '混毒卡',
            'DrawTestCard': '抽卡测试'
        }
        return display_names.get(card_class_name, card_class_name)
    
    def _deck_builder_remove_mode(self, player: Player):
        """配卡界面 - 移除卡牌模式"""
        current_config = player.get_deck_config()
        if not current_config:
            self.tui.show_message("牌库为空，无法移除卡牌！")
            return
        
        while True:
            self.tui.clear_screen()
            
            # 显示标题
            title = "=== 移除卡牌模式 ==="
            self.tui.safe_print(title)
            self.tui.safe_print("")
            
            # 显示当前牌库配置
            current_config = player.get_deck_config()
            total_cards = sum(current_config.values())
            
            self.tui.safe_print(f"当前牌库（{total_cards}/10张）：")
            if current_config:
                for card_name, count in current_config.items():
                    card_display_name = self._get_card_display_name(card_name)
                    self.tui.safe_print(f"  {card_display_name}: {count}张")
            else:
                self.tui.safe_print("  空")
            
            self.tui.safe_print("")
            self.tui.safe_print("点击以下卡牌移除一张：")
            
            # 只显示牌库中现有的卡牌
            remove_options = []
            card_names = []
            
            for card_name, count in current_config.items():
                if count > 0:
                    display_name = self._get_card_display_name(card_name)
                    remove_options.append(f"{display_name} (当前: {count}张)")
                    card_names.append(card_name)
            
            remove_options.append("返回上一级")
            
            choice = self.tui.select_from_list("选择要移除的卡牌", remove_options)
            
            if choice == -1 or choice == len(card_names):  # ESC或返回
                break
            elif choice < len(card_names):
                card_name = card_names[choice]
                if player.remove_card_from_deck_config(card_name, 1):
                    # 不显示成功信息，直接刷新界面
                    pass
                else:
                    self.tui.show_message("移除失败！")
    
    def _save_deck_config(self, config: Dict[str, int]):
        """保存牌库配置到文件"""
        # 简化实现：保存到全局变量
        self.global_deck_config = config
    
    def _load_deck_config(self) -> Dict[str, int]:
        """加载保存的牌库配置"""
        return getattr(self, 'global_deck_config', {})

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
        
        # 应用保存的配卡配置到玩家（如果有）
        saved_config = self._load_deck_config()
        if saved_config:
            try:
                # 为玩家1应用配卡配置
                self.game_state.players[0].set_custom_deck_config(saved_config)
                self.tui.show_message("已应用保存的配卡配置")
            except ValueError as e:
                self.tui.show_message(f"配卡配置无效：{e}")
            
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
            if card.action_type == ActionType.ATTACK or card.action_type == ActionType.POISON:
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
                    if card.action_type == ActionType.ATTACK or card.action_type == ActionType.POISON:
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
        
        elif card.action_type == ActionType.POISON:
            # 淬毒优先级：优先对血量高的敌人使用（持续伤害更有价值）
            poison_stacks = card.get_base_value()
            # 检查目标是否已经中毒
            if hasattr(target_char, 'buff_manager') and target_char.has_buff(BuffType.POISON):
                priority += 20  # 叠加中毒层数也有价值，但优先级较低
            else:
                priority += 40  # 新施加中毒优先级较高
            priority += target_char.current_hp * 2  # 血量越高的敌人优先级越高
                
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
        
        # 检查游戏是否在回合结束时结束（例如因buff效果导致的队伍全灭）
        if self.game_state.game_over:
            self.game_state.add_log("回合结束时检测到游戏结束，进入结束阶段")
            self.phase = GamePhase.GAME_OVER
            return
        
        # 游戏继续，切换到下一回合
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