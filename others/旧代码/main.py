"""
卡牌对战游戏主程序
实现完整的游戏流程、用户界面和交互逻辑
"""

from game_base import *
from game_engine import GameEngine, GameAI
import random


class CardBattleGame:
    """卡牌对战游戏主类"""
    
    def __init__(self):
        self.game_state = GameState()
        self.engine = GameEngine(self.game_state)
        self.ai = GameAI(self.engine)
        self.vs_ai = False  # 是否对战AI
    
    def start_game(self):
        """开始游戏"""
        print("=" * 50)
        print("欢迎来到卡牌对战游戏！")
        print("=" * 50)
        
        # 选择游戏模式
        self._select_game_mode()
        
        # 角色选择阶段
        self._character_selection_phase()
        
        # 显示队伍效果
        self._display_team_effects()
        
        # 游戏主循环
        self._game_main_loop()
        
        # 游戏结束
        self._display_game_result()
    
    def _select_game_mode(self):
        """选择游戏模式"""
        while True:
            print("\n请选择游戏模式：")
            print("1. 双人对战")
            print("2. 对战AI")
            
            choice = input("请输入选择 (1-2): ").strip()
            if choice == "1":
                self.vs_ai = False
                break
            elif choice == "2":
                self.vs_ai = True
                break
            else:
                print("无效选择，请重新输入！")
    
    def _character_selection_phase(self):
        """角色选择阶段"""
        print("\n" + "=" * 30)
        print("角色选择阶段")
        print("=" * 30)
        
        # 显示可选角色
        self._display_available_characters()
        
        # 玩家1选择角色
        if not self.vs_ai:
            print("\n玩家1 选择角色：")
        else:
            print("\n玩家 选择角色：")
        self._player_select_characters(self.game_state.players[0])
        
        # 玩家2选择角色
        if not self.vs_ai:
            print("\n玩家2 选择角色：")
            self._player_select_characters(self.game_state.players[1])
        else:
            print("\nAI 随机选择角色...")
            self._ai_select_characters(self.game_state.players[1])
    
    def _display_available_characters(self):
        """显示可选角色信息"""
        print("\n可选角色：")
        for i, char_type in enumerate(CharacterType, 1):
            char = Character(char_type)
            print(f"{i}. {char.name} - {char.description}")
    
    def _player_select_characters(self, player: Player):
        """玩家选择角色"""
        available_chars = list(CharacterType)
        
        for i in range(2):  # 选择2个角色
            while True:
                print(f"\n选择第{i+1}个角色：")
                for j, char_type in enumerate(available_chars, 1):
                    print(f"{j}. {char_type.value}")
                
                try:
                    choice = int(input("请输入选择 (数字): ")) - 1
                    if 0 <= choice < len(available_chars):
                        selected_type = available_chars.pop(choice)
                        character = self.engine.create_character(selected_type)
                        player.add_character(character)
                        print(f"已选择: {character.name}")
                        break
                    else:
                        print("无效选择，请重新输入！")
                except ValueError:
                    print("请输入有效数字！")
    
    def _ai_select_characters(self, player: Player):
        """AI随机选择角色"""
        available_chars = list(CharacterType)
        random.shuffle(available_chars)
        
        for i in range(2):
            selected_type = available_chars.pop()
            character = self.engine.create_character(selected_type)
            player.add_character(character)
            print(f"AI选择了: {character.name}")
    
    def _display_team_effects(self):
        """显示队伍效果"""
        print("\n" + "=" * 30)
        print("队伍效果检测")
        print("=" * 30)
        
        for i, player in enumerate(self.game_state.players, 1):
            player_name = f"玩家{i}" if not self.vs_ai or i == 1 else "AI"
            print(f"\n{player_name} 队伍:")
            for char in player.characters:
                print(f"  - {char.name}")
            
            if player.team_effects:
                print("  队伍效果:")
                for effect in player.team_effects:
                    effect_desc = {
                        TeamEffect.JUN_LIULI: "俊+琉璃组合：每回合第一次攻击+1",
                        TeamEffect.CAFE_XINHE: "Cafe+星河组合：每回合额外抽取2张卡",
                        TeamEffect.YANGGUANG_LIULI: "阳光+琉璃组合：免除第一次伤害"
                    }
                    print(f"    * {effect_desc[effect]}")
            else:
                print("  无特殊队伍效果")
    
    def _game_main_loop(self):
        """游戏主循环"""
        print("\n" + "=" * 30)
        print("游戏开始！")
        print("=" * 30)
        
        # 随机选择先手
        self.game_state.current_player = random.randint(0, 1)
        first_player_name = "玩家1" if self.game_state.current_player == 0 else ("玩家2" if not self.vs_ai else "AI")
        print(f"\n{first_player_name} 先手！")
        
        while not self.game_state.game_over:
            current_player = self.game_state.get_current_player()
            player_name = self._get_player_name(self.game_state.current_player)
            
            print(f"\n{'='*20} {player_name} 的回合 {'='*20}")
            
            # 回合开始处理
            self.engine.process_turn_start(current_player)
            
            # 显示当前状态
            self._display_game_status()
            
            # 玩家行动
            if not self.vs_ai or self.game_state.current_player == 0:
                self._player_turn(current_player)
            else:
                self._ai_turn(current_player)
            
            # 回合结束处理
            self.engine.process_turn_end(current_player)
            
            # 检查胜利条件
            game_over, winner = self.engine.check_victory_condition()
            if game_over:
                self.game_state.game_over = True
                self.game_state.winner = winner
                break
            
            # 切换回合
            self.game_state.switch_turn()
    
    def _get_player_name(self, player_index: int) -> str:
        """获取玩家名称"""
        if not self.vs_ai:
            return f"玩家{player_index + 1}"
        else:
            return "玩家" if player_index == 0 else "AI"
    
    def _display_game_status(self):
        """显示当前游戏状态"""
        print("\n当前状态:")
        for i, player in enumerate(self.game_state.players):
            player_name = self._get_player_name(i)
            print(f"\n{player_name}:")
            for char in player.characters:
                status = "存活" if char.is_alive else "倒下"
                defense_info = f" (防御:{char.defense_buff})" if char.defense_buff > 0 else ""
                print(f"  {char.name}: {char.current_hp}/{char.max_hp} HP - {status}{defense_info}")
        
        # 显示当前玩家手牌
        current_player = self.game_state.get_current_player()
        if not self.vs_ai or self.game_state.current_player == 0:
            print(f"\n手牌 ({len(current_player.hand)}张):")
            for i, card in enumerate(current_player.hand, 1):
                print(f"  {i}. {card.name}")
    
    def _player_turn(self, player: Player):
        """玩家回合"""
        print(f"\n{self._get_player_name(player.player_id - 1)} 的行动阶段")
        
        while True:
            if not player.hand:
                print("没有手牌可用！")
                break
            
            print("\n选择行动:")
            print("1. 使用卡牌")
            print("2. 结束回合")
            
            choice = input("请输入选择 (1-2): ").strip()
            
            if choice == "1":
                if self._use_card_interactive(player):
                    # 检查是否有角色倒下
                    game_over, winner = self.engine.check_victory_condition()
                    if game_over:
                        self.game_state.game_over = True
                        self.game_state.winner = winner
                        break
                else:
                    continue
            elif choice == "2":
                print("结束回合")
                break
            else:
                print("无效选择，请重新输入！")
    
    def _use_card_interactive(self, player: Player) -> bool:
        """交互式使用卡牌"""
        # 选择手牌
        print("\n选择要使用的卡牌:")
        for i, card in enumerate(player.hand, 1):
            print(f"{i}. {card.name}")
        print("0. 返回")
        
        try:
            card_choice = int(input("请输入卡牌编号: "))
            if card_choice == 0:
                return False
            if not (1 <= card_choice <= len(player.hand)):
                print("无效选择！")
                return False
            
            selected_card = player.hand[card_choice - 1]
        except ValueError:
            print("请输入有效数字！")
            return False
        
        # 选择使用卡牌的角色
        alive_chars = player.get_alive_characters()
        if not alive_chars:
            print("没有存活的角色！")
            return False
        
        print("\n选择使用卡牌的角色:")
        for i, char in enumerate(alive_chars, 1):
            print(f"{i}. {char.name} (HP: {char.current_hp}/{char.max_hp})")
        
        try:
            char_choice = int(input("请输入角色编号: ")) - 1
            if not (0 <= char_choice < len(alive_chars)):
                print("无效选择！")
                return False
            
            user_char = alive_chars[char_choice]
        except ValueError:
            print("请输入有效数字！")
            return False
        
        # 选择目标
        targets = self.engine.get_available_targets(player, selected_card.action_type)
        if not targets:
            print("没有可用的目标！")
            return False
        
        print(f"\n选择 {selected_card.name} 的目标:")
        for i, target in enumerate(targets, 1):
            target_player = self._find_character_owner(target)
            if target_player:
                target_player_name = self._get_player_name(target_player.player_id - 1)
            else:
                target_player_name = "未知"
            print(f"{i}. {target.name} ({target_player_name}) (HP: {target.current_hp}/{target.max_hp})")
        
        try:
            target_choice = int(input("请输入目标编号: ")) - 1
            if not (0 <= target_choice < len(targets)):
                print("无效选择！")
                return False
            
            target_char = targets[target_choice]
        except ValueError:
            print("请输入有效数字！")
            return False
        
        # 执行行动
        card_index = player.hand.index(selected_card)
        used_card = player.use_card(card_index)
        
        if used_card:
            success = self.engine.execute_action(player, user_char, used_card, target_char)
            if success:
                print(f"\n{user_char.name} 使用了 {used_card.name}！")
                return True
            else:
                print("行动失败！")
        
        return False
    
    def _ai_turn(self, player: Player):
        """AI回合"""
        print(f"\nAI 思考中...")
        
        # AI决策
        actions = self.ai.make_decision(player)
        
        if not actions:
            print("AI 选择结束回合")
            return
        
        # 执行AI选择的行动
        for user_char, card, target_char in actions:
            if card not in player.hand:
                continue
                
            card_index = player.hand.index(card)
            used_card = player.use_card(card_index)
            
            if used_card:
                success = self.engine.execute_action(player, user_char, used_card, target_char)
                if success:
                    target_player = self._find_character_owner(target_char)
                    if target_player:
                        target_player_name = self._get_player_name(target_player.player_id - 1)
                    else:
                        target_player_name = "未知"
                    print(f"AI: {user_char.name} 对 {target_char.name} ({target_player_name}) 使用了 {used_card.name}！")
                
                # 检查游戏是否结束
                game_over, winner = self.engine.check_victory_condition()
                if game_over:
                    self.game_state.game_over = True
                    self.game_state.winner = winner
                    break
    
    def _find_character_owner(self, character: Character) -> Optional[Player]:
        """找到角色的所有者"""
        for player in self.game_state.players:
            if character in player.characters:
                return player
        return None
    
    def _display_game_result(self):
        """显示游戏结果"""
        print("\n" + "=" * 50)
        print("游戏结束！")
        print("=" * 50)
        
        if self.game_state.winner is not None:
            winner_name = self._get_player_name(self.game_state.winner)
            print(f"🎉 {winner_name} 获胜！🎉")
        else:
            print("游戏平局！")
        
        print(f"\n总回合数: {self.game_state.turn_count}")
        
        # 显示最终状态
        print("\n最终状态:")
        for i, player in enumerate(self.game_state.players):
            player_name = self._get_player_name(i)
            print(f"\n{player_name}:")
            for char in player.characters:
                status = "存活" if char.is_alive else "倒下"
                print(f"  {char.name}: {char.current_hp}/{char.max_hp} HP - {status}")


def main():
    """主函数"""
    try:
        game = CardBattleGame()
        game.start_game()
        
        # 询问是否再来一局
        while True:
            play_again = input("\n是否再来一局？(y/n): ").strip().lower()
            if play_again in ['y', 'yes', '是', '是的']:
                print("\n" + "=" * 50)
                game = CardBattleGame()
                game.start_game()
            elif play_again in ['n', 'no', '不', '不了']:
                print("\n谢谢游戏！再见！")
                break
            else:
                print("请输入 y/n 或 是/不")
                
    except KeyboardInterrupt:
        print("\n\n游戏被中断，再见！")
    except Exception as e:
        print(f"\n游戏出现错误: {e}")
        print("请重新启动游戏")


if __name__ == "__main__":
    main()