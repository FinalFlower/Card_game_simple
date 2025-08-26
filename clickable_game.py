"""
卡牌对战游戏 - 鼠标点击版本
使用Tkinter实现真正的鼠标点击操作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import Optional

from game_base import *
from game_engine import GameEngine, GameAI
from simple_data_loader import game_data


class ClickableGameUI:
    """可点击的游戏界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("卡牌对战游戏")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # 游戏核心
        self.game_state = GameState()
        self.engine = GameEngine(self.game_state)
        self.ai = GameAI(self.engine)
        
        # 游戏阶段状态
        self.game_phase = "character_selection"  # "character_selection" 或 "battle"
        self.player_selected_chars = []  # 玩家已选择的角色
        
        # 选择状态
        self.selected_character = None
        self.selected_card = None
        self.selected_card_index: Optional[int] = None
        
        # UI组件
        self.char_buttons = []
        self.card_buttons = []
        self.char_selection_buttons = []
        
        # 创建UI界面
        self._create_ui()
        
        # 开始角色选择
        self._start_character_selection()
        
    def _start_character_selection(self):
        """开始角色选择阶段"""
        print(f"Debug: 开始角色选择, 当前选择的角色: {self.player_selected_chars}")
        self._add_message("🎮 欢迎进入卡牌对战游戏！")
        self._add_message("📝 请选择两个角色组成你的队伍")
        
        # 显示角色选择界面
        self.char_title_label.config(text="🏆 角色选择")
        self.char_selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # 确保战斗面板被隐藏
        try:
            self.char_battle_frame.pack_forget()
        except:
            pass  # 如果还没有pack就忽略
        
        # 隐藏结束回合按钮
        self.end_turn_btn.config(state=tk.DISABLED)
        
        self._create_character_selection_buttons()
        self._update_deck_info()
    
    def _create_character_selection_buttons(self):
        """创建角色选择按钮"""
        print(f"Debug: 创建选择按钮, 当前选择数量: {len(self.player_selected_chars)}")
        # 清空现有按钮
        for widget in self.char_selection_frame.winfo_children():
            widget.destroy()
        
        self.char_selection_buttons = []
        available_chars = game_data.get_all_characters()
        
        # 显示已选择的角色
        if self.player_selected_chars:
            selected_frame = tk.LabelFrame(self.char_selection_frame, text="✅ 已选择的角色", 
                                         font=('Arial', 12), bg='#27ae60', fg='white')
            selected_frame.pack(fill=tk.X, pady=5)
            
            for char_id in self.player_selected_chars:
                char_info = available_chars[char_id]
                char_text = f"{char_info['display_name']}\n{char_info['description']}"
                tk.Label(selected_frame, text=char_text, font=('Arial', 9),
                        bg='#2ecc71', fg='white', relief=tk.RAISED, bd=2).pack(pady=2, padx=5)
        
        # 可选择的角色
        available_frame = tk.LabelFrame(self.char_selection_frame, text="🔵 可选择的角色", 
                                       font=('Arial', 12), bg='#3498db', fg='white')
        available_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for char_id, char_info in available_chars.items():
            if char_id not in self.player_selected_chars:
                btn = self._create_character_selection_button(available_frame, char_id, char_info)
                self.char_selection_buttons.append(btn)
        
        # 显示选择进度
        progress_text = f"选择进度: {len(self.player_selected_chars)}/2"
        if hasattr(self, 'progress_label'):
            self.progress_label.destroy()
        self.progress_label = tk.Label(self.char_selection_frame, text=progress_text, 
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        self.progress_label.pack(pady=10)
        
        # 如果已选择两个角色，显示开始游戏按钮
        if len(self.player_selected_chars) == 2:
            print("Debug: 已选择两个角色，显示开始游戏按钮")
            start_btn = tk.Button(self.char_selection_frame, text="开始游戏", font=('Arial', 14, 'bold'),
                                bg='#e74c3c', fg='white', command=self._start_battle_phase,
                                width=15, height=2)
            start_btn.pack(pady=10)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧 - 角色面板
        self._create_character_panel(main_frame)
        
        # 右侧区域
        right_frame = tk.Frame(main_frame, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 右上 - 历史记录
        self._create_history_panel(right_frame)
        
        # 右下 - 手牌和牙库信息
        bottom_frame = tk.Frame(right_frame, bg='#2c3e50')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        self._create_hand_panel(bottom_frame)
        self._create_deck_info_panel(bottom_frame)
        
        # 控制按钮（在历史记录和手牌之间）
        self._create_control_panel(right_frame)
    
    def _create_character_panel(self, parent):
        """创建角色面板"""
        char_frame = tk.Frame(parent, bg='#34495e', relief=tk.RAISED, bd=2)
        char_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.char_title_label = tk.Label(char_frame, text="🏆 角色选择", font=('Arial', 14, 'bold'), 
                bg='#34495e', fg='white')
        self.char_title_label.pack(pady=10)
        
        # 角色选择区域
        self.char_selection_frame = tk.Frame(char_frame, bg='#34495e')
        self.char_selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 游戏中的角色状态区域
        self.char_battle_frame = tk.Frame(char_frame, bg='#34495e')
        
        # 玩家1区域
        self.player1_frame = tk.LabelFrame(self.char_battle_frame, text="🔵 玩家1", 
                                          font=('Arial', 12), bg='#3498db', fg='white')
        self.player1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 玩家2/AI区域  
        self.player2_frame = tk.LabelFrame(self.char_battle_frame, text="🔴 AI", 
                                          font=('Arial', 12), bg='#e74c3c', fg='white')
        self.player2_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def _create_history_panel(self, parent):
        """创建历史记录面板"""
        history_frame = tk.Frame(parent, bg='#34495e', relief=tk.RAISED, bd=2)
        history_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        tk.Label(history_frame, text="📜 游戏记录", font=('Arial', 14, 'bold'),
                bg='#34495e', fg='white').pack(pady=10)
        
        # 历史记录文本框
        text_frame = tk.Frame(history_frame, bg='#34495e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.history_text = tk.Text(text_frame, bg='#2c3e50', fg='white',
                                   font=('Consolas', 10), state=tk.DISABLED, height=15)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_text.yview)
    
    def _create_hand_panel(self, parent):
        """创建手牌面板"""
        hand_frame = tk.Frame(parent, bg='#34495e', relief=tk.RAISED, bd=2)
        hand_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(hand_frame, text="🎴 手牌", font=('Arial', 14, 'bold'),
                bg='#34495e', fg='white').pack(pady=10)
        
        self.hand_frame = tk.Frame(hand_frame, bg='#34495e')
        self.hand_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _create_deck_info_panel(self, parent):
        """创建牙库信息面板"""
        deck_frame = tk.Frame(parent, bg='#34495e', relief=tk.RAISED, bd=2)
        deck_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        tk.Label(deck_frame, text="📊 牙库信息", font=('Arial', 12, 'bold'),
                bg='#34495e', fg='white').pack(pady=10)
        
        self.deck_info_frame = tk.Frame(deck_frame, bg='#34495e')
        self.deck_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 牙库数量信息标签
        self.deck_count_label = tk.Label(self.deck_info_frame, text="牙库: 30", 
                                        font=('Arial', 10), bg='#2980b9', fg='white', width=12)
        self.deck_count_label.pack(pady=2)
        
        self.hand_count_label = tk.Label(self.deck_info_frame, text="手牌: 0", 
                                        font=('Arial', 10), bg='#27ae60', fg='white', width=12)
        self.hand_count_label.pack(pady=2)
        
        self.discard_count_label = tk.Label(self.deck_info_frame, text="弃牌: 0", 
                                           font=('Arial', 10), bg='#95a5a6', fg='white', width=12)
        self.discard_count_label.pack(pady=2)
    
    def _create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = tk.Frame(parent, bg='#2c3e50')
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 5))
        
        button_frame = tk.Frame(control_frame, bg='#2c3e50')
        button_frame.pack()
        
        self.end_turn_btn = tk.Button(button_frame, text="结束回合", font=('Arial', 12),
                 bg='#f39c12', fg='white', command=self._end_turn,
                 width=12, height=2)
        self.end_turn_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="重新开始", font=('Arial', 12),
                 bg='#95a5a6', fg='white', command=self._restart_game,
                 width=12, height=2).pack(side=tk.LEFT, padx=5)
    
    def _create_character_selection_button(self, parent, char_id, char_info):
        """创建角色选择按钮"""
        def on_select():
            self._on_character_select(char_id)
        
        btn_text = f"{char_info['display_name']}\n{char_info['description']}\nHP: {char_info['max_hp']}"
        btn = tk.Button(parent, text=btn_text, font=('Arial', 9), command=on_select,
                       bg='#2980b9', fg='white', width=25, height=4, wraplength=180)
        btn.pack(pady=2, padx=5, fill=tk.X)
        return btn
    
    def _on_character_select(self, char_id):
        """处理角色选择"""
        if len(self.player_selected_chars) < 2 and char_id not in self.player_selected_chars:
            self.player_selected_chars.append(char_id)
            char_info = game_data.get_character_info(char_id)
            if char_info:
                self._add_message(f"✅ 选择了角色: {char_info['display_name']}")
            
            # 重新创建选择按钮
            self._create_character_selection_buttons()
    
    def _start_battle_phase(self):
        """开始战斗阶段"""
        self.game_phase = "battle"
        
        # 隐藏角色选择界面，显示战斗界面
        self.char_title_label.config(text="🏆 角色状态")
        self.char_selection_frame.pack_forget()
        self.char_battle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 启用结束回合按钮
        self.end_turn_btn.config(state=tk.NORMAL)
        
        self._add_message("⚔️ 进入战斗阶段！")
        
        # 开始游戏
        self._start_game()
    
    def _create_character_button(self, parent, character, player_id, is_opponent=False):
        """创建角色按钮"""
        def on_click():
            self._on_character_click(character, is_opponent)
        
        btn = tk.Button(parent, text=self._get_char_text(character),
                       font=('Arial', 10), command=on_click,
                       bg='#27ae60' if character.is_alive else '#e74c3c',
                       fg='white', width=15, height=3)
        btn.pack(pady=2, padx=5)
        return btn
    
    def _create_card_button(self, parent, card, index):
        """创建卡牌按钮"""
        def on_click():
            self._on_card_click(card, index)
        
        btn = tk.Button(parent, text=f"{card.display_name}\n{card.description}",
                       font=('Arial', 9), command=on_click,
                       bg='#2980b9', fg='white', width=20, height=3)
        btn.pack(side=tk.LEFT, padx=2)
        return btn
    
    def _get_char_text(self, character):
        """获取角色按钮文本"""
        status = "存活" if character.is_alive else "倒下"
        defense = f"\n🛡️{character.defense_buff}" if character.defense_buff > 0 else ""
        selected = "\n👆已选择" if character == self.selected_character else ""
        return f"{character.display_name}\n❤️{character.current_hp}/{character.max_hp}\n{status}{defense}{selected}"
    
    def _on_character_click(self, character, is_opponent):
        """角色点击处理"""
        if self.game_state.current_player != 0:  # 不是玩家回合
            return
        
        if self.selected_card and not is_opponent:  # 选择了卡牌但点击己方角色
            if self.selected_card.can_target_ally():
                self._execute_action(character)
            else:
                self._add_message("⚠️ 此卡牌不能对己方使用！")
        elif self.selected_card and is_opponent:  # 选择了卡牌并点击敌方角色
            if self.selected_card.can_target_enemy():
                self._execute_action(character)
            else:
                self._add_message("⚠️ 此卡牌不能对敌方使用！")
        elif not is_opponent and character.is_alive:  # 选择操作角色
            self.selected_character = character
            self._add_message(f"✋ 选择了角色：{character.display_name}")
            self._update_display()
    
    def _on_card_click(self, card, index):
        """卡牌点击处理"""
        if self.game_state.current_player != 0:  # 不是玩家回合
            return
        
        if not self.selected_character:
            self._add_message("⚠️ 请先选择一个角色！")
            return
        
        self.selected_card = card
        self.selected_card_index = index
        target_type = "敌方角色" if card.can_target_enemy() else "己方角色"
        self._add_message(f"🎯 选择了卡牌：{card.display_name}，请点击{target_type}")
        self._update_display()
    
    def _execute_action(self, target_character):
        """执行行动"""
        if not self.selected_character or not self.selected_card or self.selected_card_index is None:
            return
        
        current_player = self.game_state.get_current_player()
        
        # 检查目标有效性
        targets = self.engine.get_available_targets(current_player, self.selected_card)
        if target_character not in targets:
            self._add_message("⚠️ 无效的目标！")
            return
        
        # 执行行动
        used_card = current_player.use_card(self.selected_card_index)
        if used_card:
            success = self.engine.execute_action(current_player, self.selected_character, used_card, target_character)
            if success:
                target_player = self._find_character_owner(target_character)
                if target_player:
                    target_player_name = "玩家1" if target_player.player_id == 1 else "AI"
                    self._add_message(f"⚡ {self.selected_character.display_name} → {target_character.display_name}({target_player_name}) 使用 {used_card.display_name}！")
                
                # 重置选择
                self.selected_character = None
                self.selected_card = None
                self.selected_card_index = None
                
                self._update_display()
                
                # 检查游戏是否结束
                game_over, winner = self.engine.check_victory_condition()
                if game_over:
                    self._end_game(winner)
    
    def _end_turn(self):
        """结束回合"""
        if self.game_state.current_player == 0 and not self.game_state.game_over:
            self._add_message("🔚 玩家结束回合")
            self._process_turn_end()
    
    def _process_turn_end(self):
        """处理回合结束"""
        current_player = self.game_state.get_current_player()
        
        # 回合结束处理
        self.engine.process_turn_end(current_player)
        
        # 检查胜利条件
        game_over, winner = self.engine.check_victory_condition()
        if game_over:
            self._end_game(winner)
            return
        
        # 切换回合
        self.game_state.switch_turn()
        self.selected_character = None
        self.selected_card = None
        
        # 如果是AI回合，执行AI操作
        if self.game_state.current_player == 1:
            self.root.after(1000, self._ai_turn)
        else:
            self._start_player_turn()
    
    def _ai_turn(self):
        """AI回合"""
        player = self.game_state.get_current_player()
        self._add_message("🤖 AI的回合...")
        
        # 回合开始处理
        self.engine.process_turn_start(player)
        self._update_display()
        
        actions = self.ai.make_decision(player)
        
        if not actions:
            self._add_message("🤖 AI结束回合")
            self.root.after(1000, self._process_turn_end)
        else:
            self._execute_ai_actions(actions, 0)
    
    def _execute_ai_actions(self, actions, index):
        """逐个执行AI行动"""
        if index >= len(actions):
            self.root.after(1000, self._process_turn_end)
            return
        
        user_char, card, target_char = actions[index]
        player = self.game_state.get_current_player()
        
        if card in player.hand:
            card_index = player.hand.index(card)
            used_card = player.use_card(card_index)
            
            if used_card:
                success = self.engine.execute_action(player, user_char, used_card, target_char)
                if success:
                    target_player = self._find_character_owner(target_char)
                    if target_player:
                        target_player_name = "玩家1" if target_player.player_id == 1 else "AI"
                        self._add_message(f"🤖 {user_char.display_name} → {target_char.display_name}({target_player_name}) 使用 {used_card.display_name}！")
                
                self._update_display()
                
                # 检查游戏是否结束
                game_over, winner = self.engine.check_victory_condition()
                if game_over:
                    self._end_game(winner)
                    return
        
        # 继续下一个行动
        self.root.after(1500, lambda: self._execute_ai_actions(actions, index + 1))
    
    def _start_player_turn(self):
        """开始玩家回合"""
        current_player = self.game_state.get_current_player()
        self._add_message("🏃 玩家的回合开始")
        
        # 回合开始处理
        self.engine.process_turn_start(current_player)
        self._update_display()
        
        self._add_message("💡 点击角色选择操作者，然后点击卡牌，最后点击目标")
    
    def _update_display(self):
        """更新显示"""
        # 清空现有按钮
        for widget in self.player1_frame.winfo_children():
            widget.destroy()
        for widget in self.player2_frame.winfo_children():
            widget.destroy()
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        self.char_buttons = []
        self.card_buttons = []
        
        # 更新角色按钮
        for char in self.game_state.players[0].characters:
            btn = self._create_character_button(self.player1_frame, char, 0, False)
            self.char_buttons.append(btn)
        
        for char in self.game_state.players[1].characters:
            btn = self._create_character_button(self.player2_frame, char, 1, True)
            self.char_buttons.append(btn)
        
        # 更新手牌按钮（仅玩家回合显示）
        if self.game_state.current_player == 0:
            current_player = self.game_state.get_current_player()
            for i, card in enumerate(current_player.hand):
                btn = self._create_card_button(self.hand_frame, card, i)
                if card == self.selected_card:
                    btn.config(bg='#f39c12')  # 高亮选中的卡牌
                self.card_buttons.append(btn)
        
        # 更新牙库信息
        self._update_deck_info()
    
    def _add_message(self, message):
        """添加历史消息"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def _find_character_owner(self, character):
        """找到角色的所有者"""
        for player in self.game_state.players:
            if character in player.characters:
                return player
        return None
    
    def _start_game(self):
        """开始游戏"""
        # 玩家1使用已选择的角色
        for char_id in self.player_selected_chars:
            character = self.engine.create_character(char_id)
            self.game_state.players[0].add_character(character)
        
        # AI随机选择角色
        available_chars = list(self.game_state.available_characters)
        # 移除玩家已选择的角色
        for char_id in self.player_selected_chars:
            if char_id in available_chars:
                available_chars.remove(char_id)
        
        random.shuffle(available_chars)
        for i in range(2):
            char_id = available_chars.pop()
            character = self.engine.create_character(char_id)
            self.game_state.players[1].add_character(character)
        
        self._add_message(f"玩家1: {', '.join([c.display_name for c in self.game_state.players[0].characters])}")
        self._add_message(f"AI: {', '.join([c.display_name for c in self.game_state.players[1].characters])}")
        
        # 显示队伍效果
        self._log_team_effects()
        
        # 随机先手
        self.game_state.current_player = random.randint(0, 1)
        first_player = "玩家1" if self.game_state.current_player == 0 else "AI"
        self._add_message(f"🎲 {first_player} 先手！")
        
        self._update_display()
        
        if self.game_state.current_player == 0:
            self._start_player_turn()
        else:
            self.root.after(1000, self._ai_turn)
    
    def _update_deck_info(self):
        """更新牙库信息显示"""
        if self.game_phase == "battle":
            current_player = self.game_state.get_current_player()
            deck_count = len(current_player.deck)
            hand_count = len(current_player.hand)
            discard_count = len(current_player.discard_pile)
            
            self.deck_count_label.config(text=f"牙库: {deck_count}")
            self.hand_count_label.config(text=f"手牌: {hand_count}")
            self.discard_count_label.config(text=f"弃牌: {discard_count}")
        else:
            # 角色选择阶段显示默认信息
            self.deck_count_label.config(text=f"牙库: 30")
            self.hand_count_label.config(text=f"手牌: 0")
            self.discard_count_label.config(text=f"弃牌: 0")
    
    def _log_team_effects(self):
        """记录队伍效果"""
        team_effects_config = game_data.get_team_effects()
        
        for i, player in enumerate(self.game_state.players):
            player_name = f"玩家{i+1}" if i == 0 else "AI"
            if player.team_effects:
                for effect_id in player.team_effects:
                    effect_info = team_effects_config.get(effect_id, {})
                    effect_name = effect_info.get('name', effect_id)
                    self._add_message(f"✨ {player_name} 激活: {effect_name}")
    
    def _end_game(self, winner):
        """结束游戏"""
        self.game_state.game_over = True
        self.game_state.winner = winner
        
        if winner is not None:
            winner_name = "玩家1" if winner == 0 else "AI"
            self._add_message(f"🎉 {winner_name} 获胜！")
            messagebox.showinfo("游戏结束", f"{winner_name} 获胜！")
        else:
            self._add_message("🤝 平局！")
            messagebox.showinfo("游戏结束", "平局！")
    
    def _restart_game(self):
        """重新开始游戏"""
        self.game_state = GameState()
        self.engine = GameEngine(self.game_state)
        self.ai = GameAI(self.engine)
        self.selected_character = None
        self.selected_card = None
        self.selected_card_index = None
        
        # 重置角色选择状态
        self.game_phase = "character_selection"
        self.player_selected_chars = []
        
        # 清空历史记录
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        # 重新开始角色选择
        self._start_character_selection()
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()


def main():
    """主函数"""
    game = ClickableGameUI()
    game.run()


if __name__ == "__main__":
    main()