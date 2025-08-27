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
        
        # 重置所有角色的状态（包括电能和行动槽）
        for char in player.characters:
            if char.is_alive:
                # 调用Character的reset_turn_status方法，它会处理电能和行动槽重置
                char.reset_turn_status()
        
        game_state.add_log(f"玩家{player.id} 的所有角色电能和行动槽已重置")
        
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
        """
        处理回合结束逻辑，包括角色技能、buff效果等
        """
        player = game_state.get_current_player()
        opponent = game_state.get_opponent_player()
        
        # 处理当前玩家的角色技能和状态重置
        for char in player.get_alive_characters():
            char.on_turn_end(game_state, player, self)
            char.reset_turn_status()  # 重置回合状态
        
        # 处理所有玩家角色的buff效果（中毒等持续伤害在回合结束时结算）
        all_players = [player, opponent]
        for p in all_players:
            for char in p.characters:  # 包括死亡角色，因为buff可能在死亡后仍然存在
                if char.is_alive:  # 只对正在生存的角色应用buff效果
                    old_hp = char.current_hp
                    # 应用buff效果（如中毒伤害）
                    buff_results = char.apply_all_buffs(game_state)
                    
                    # 检查buff效果是否导致角色死亡
                    if not char.is_alive and old_hp > 0:
                        game_state.add_log(f"{char.name} 因buff效果而死亡！")
                        # 立即检查是否导致游戏结束
                        self.check_game_over(game_state)
                        if game_state.game_over:
                            # 记录回合结束日志，然后立即返回
                            game_state.add_log(f"玩家{player.id} 回合结束。")
                            return  # 游戏结束，立即返回
                
                # 处理buff的时间推进和清理（包括死亡角色）
                char.tick_buffs(game_state)
        
        game_state.add_log(f"玩家{player.id} 回合结束。")
        
        # 检查游戏是否结束（如果还未结束的话）
        if not game_state.game_over:
            # 在回合结束时进行全面的队伍败北检测
            game_state.add_log("执行回合结束队伍状态检查...")
            self.check_game_over(game_state)

    def execute_action(self, game_state: GameState, card_idx: int, user_char_idx: int, target_char_idx: int):
        player = game_state.get_current_player()
        opponent = game_state.get_opponent_player()

        # 检查角色索引是否有效
        alive_characters = player.get_alive_characters()
        if user_char_idx >= len(alive_characters):
            game_state.add_log(f"错误：无效的角色索引")
            return False
        
        user_char = alive_characters[user_char_idx]
        
        # 检查行动槽是否可用
        if not user_char.can_act():
            if not user_char.is_alive:
                game_state.add_log(f"错误：{user_char.name} 已经死亡，无法行动")
            else:
                game_state.add_log(f"错误：{user_char.name} 的行动槽已用完，无法再次行动")
            return False
        
        # 检查手牌索引是否有效
        if card_idx >= len(player.hand):
            game_state.add_log(f"错误：无效的手牌索引")
            return False

        card = player.hand[card_idx]  # 暂时不移除，等通过所有验证再移除
        
        # 检查电能是否足够
        if not card.can_use(user_char):
            energy_status = user_char.get_energy_status()
            game_state.add_log(f"错误：{user_char.name} 电能不足！当前电能：{energy_status['current_energy']}/{energy_status['energy_limit']}，需要：{card.energy_cost}")
            return False
        
        # 通过所有验证，现在实际执行行动
        card = player.hand.pop(card_idx)
        player.discard_pile.append(card)
        
        # 消耗电能
        if not user_char.consume_energy(card.energy_cost):
            # 这里不应该发生，因为我们已经检查过了
            game_state.add_log(f"内部错误：无法消耗{user_char.name}的电能")
            return False
        
        game_state.add_log(f"{user_char.name} 消耗 {card.energy_cost} 点电能使用 {card.name}")
        
        # 使用行动槽
        if not user_char.try_use_action_slot():
            # 这里不应该发生，因为我们已经检查过了
            game_state.add_log(f"内部错误：无法使用{user_char.name}的行动槽")
            return False
        
        game_state.add_log(f"{user_char.name} 使用了行动槽")

        if card.action_type == ActionType.ATTACK:
            opponent_alive = opponent.get_alive_characters()
            if target_char_idx >= len(opponent_alive):
                game_state.add_log(f"错误：无效的目标角色索引")
                return False
            target_char = opponent_alive[target_char_idx]
            player.status['used_attack_this_turn'] = True  # 标记使用了攻击卡
            self._execute_attack(game_state, player, user_char, card, target_char)
        elif card.action_type == ActionType.HEAL:
            if target_char_idx >= len(alive_characters):
                game_state.add_log(f"错误：无效的目标角色索引")
                return False
            target_char = alive_characters[target_char_idx]
            self._execute_heal(game_state, user_char, card, target_char)
        elif card.action_type == ActionType.DEFEND:
            if target_char_idx >= len(alive_characters):
                game_state.add_log(f"错误：无效的目标角色索引")
                return False
            target_char = alive_characters[target_char_idx]
            self._execute_defend(game_state, user_char, card, target_char)
        elif card.action_type == ActionType.POISON:
            opponent_alive = opponent.get_alive_characters()
            if target_char_idx >= len(opponent_alive):
                game_state.add_log(f"错误：无效的目标角色索引")
                return False
            target_char = opponent_alive[target_char_idx]
            self._execute_poison(game_state, user_char, card, target_char)
            
        self.check_game_over(game_state)
        return True

    def _execute_attack(self, game_state, player, attacker, card, target):
        damage = card.get_base_value()

        # 队伍效果
        # (此处省略了对 first_damage_dealt 状态的检查，实际应在角色状态中维护)
        if TeamEffect.JUN_LIULI in player.team_effects:
            damage += 1
            game_state.add_log("队伍效果[俊琉璃]触发，伤害+1")
        
        # 攻击者技能钩子（但不在这里累积伤害）
        damage = attacker.on_deal_damage(damage, game_state)
        
        # 目标技能钩子
        adjusted_damage, counter_damage = target.on_take_damage(damage, attacker, game_state)
        
        # 造成伤害
        actual_damage = target.take_damage(adjusted_damage)
        game_state.add_log(f"{attacker.name} 对 {target.name} 使用攻击，造成 {actual_damage} 点伤害。")
        
        # 使用实际造成的伤害来累积发电等级（覆盖on_deal_damage中的累积）
        if actual_damage > 0:
            attacker.add_damage_to_generation(actual_damage, game_state)

        if counter_damage > 0:
            counter_actual_damage = attacker.take_damage(counter_damage)
            game_state.add_log(f"{target.name} 反击 {attacker.name}，造成 {counter_damage} 点伤害。")
            # 反击伤害也应该累积到反击者的发电系统
            if counter_actual_damage > 0:
                target.add_damage_to_generation(counter_actual_damage, game_state)

    def _execute_heal(self, game_state, user, card, target):
        heal_amount = card.get_base_value()
        target.heal(heal_amount)
        game_state.add_log(f"{user.name} 对 {target.name} 使用治疗，恢复 {heal_amount} 点生命。")

    def _execute_defend(self, game_state, user, card, target):
        def_amount = card.get_base_value()
        target.add_defense(def_amount)
        game_state.add_log(f"{user.name} 对 {target.name} 使用防御，增加 {def_amount} 点防御。")
    
    def _execute_poison(self, game_state, user, card, target):
        """
        执行毒素卡效果，对目标施加中毒buff
        
        Args:
            game_state: 游戏状态
            user: 使用者
            card: 毒素卡
            target: 目标角色
        """
        from LingCard.buffs.poison import PoisonBuff
        
        poison_stacks = card.get_base_value()  # 获取中毒层数
        poison_buff = PoisonBuff(stacks=poison_stacks, caster=user)  # 传入施加者信息
        
        # 对目标施加中毒buff
        success = target.add_buff(poison_buff, game_state)
        
        if success:
            game_state.add_log(f"{user.name} 对 {target.name} 使用淬毒，施加 {poison_stacks} 层中毒效果。")
        else:
            game_state.add_log(f"{user.name} 对 {target.name} 使用淬毒，但效果施加失败。")

    def check_game_over(self, game_state: GameState):
        """
        检查游戏是否结束：检测双方队伍的被击败情况
        如果有一方成员均被击败，则直接判定比赛结果
        """
        current_player = game_state.get_current_player()
        opponent_player = game_state.get_opponent_player()
        
        # 获取双方存活角色数量
        current_alive = len(current_player.get_alive_characters())
        opponent_alive = len(opponent_player.get_alive_characters())
        
        # 检查当前玩家是否被击败（所有角色死亡）
        if current_player.is_defeated():
            game_state.game_over = True
            game_state.winner = opponent_player.id
            game_state.add_log(f"玩家{current_player.id} 队伍全灭！玩家{opponent_player.id} 获胜！")
            return
        
        # 检查对手玩家是否被击败（所有角色死亡）
        elif opponent_player.is_defeated():
            game_state.game_over = True
            game_state.winner = current_player.id
            game_state.add_log(f"玩家{opponent_player.id} 队伍全灭！玩家{current_player.id} 获胜！")
            return
        
        # 双方都有存活成员，游戏继续
        # 记录当前队伍状态（仅用于调试）
        game_state.add_log(f"队伍状态检查：玩家{current_player.id}({current_alive}存活) vs 玩家{opponent_player.id}({opponent_alive}存活)")