"""
卡牌对战游戏引擎
实现核心战斗逻辑、技能系统和特殊效果处理
重构版本：适配新的YAML配置系统
"""

from game_base import *
import random
from typing import Tuple, List
from simple_data_loader import game_data


class GameEngine:
    """游戏引擎，处理核心战斗逻辑"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def execute_action(self, player: Player, character: Character, 
                      action_card: ActionCard, target_character: Character) -> bool:
        """
        执行行动卡效果
        返回是否成功执行
        """
        if not character.is_alive or not target_character.is_alive:
            return False
        
        effect_type = action_card.effect_type
        base_value = action_card.get_base_value()
        
        if effect_type == "damage":
            return self._execute_attack(player, character, target_character, base_value)
        elif effect_type == "heal":
            return self._execute_heal(player, character, base_value)
        elif effect_type == "defense":
            return self._execute_defend(character, base_value)
            
        return False
    
    def _execute_attack(self, attacker_player: Player, attacker: Character, 
                       target: Character, base_damage: int) -> bool:
        """执行攻击行动"""
        damage = base_damage
        
        # Cafe技能：每回合第一次造成伤害时伤害加1
        if (attacker.char_id == 'cafe' and 
            not attacker.first_damage_dealt):
            damage += 1
            attacker.first_damage_dealt = True
            print(f"{attacker.name} Cafe技能触发！第一次攻击伤害+1，总伤害：{damage}")
        
        # 俊+琉璃组合效果：每回合第一次攻击加1
        if ('jun_liuli' in attacker_player.team_effects and 
            not attacker.first_damage_dealt):
            damage += 1
            attacker.first_damage_dealt = True
            print(f"队伍效果触发！俊+琉璃组合第一次攻击+1，总伤害：{damage}")
        
        # 阳光+琉璃组合效果：免除第一次伤害
        target_player = self._get_target_player(target)
        first_damage_immunity = False
        if target_player and 'yangguang_liuli' in target_player.team_effects:
            # 检查是否是本回合第一次受到伤害
            total_damage_taken = sum(char.damage_taken_count for char in target_player.characters)
            if total_damage_taken == 0:
                first_damage_immunity = True
                print(f"队伍效果触发！阳光+琉璃组合免除第一次伤害！")
                return True
        
        print(f"{attacker.name} 攻击 {target.name}，造成 {damage} 点伤害")
        
        # 俊技能：帮助队友承受伤害
        final_target = target
        if target_player:
            final_target = self._check_jun_protection(target, target_player)
        
        # 执行伤害
        actual_damage, counter_triggered, counter_damage = final_target.take_damage(damage)
        
        # 处理琉璃反击
        if counter_triggered and counter_damage > 0:
            print(f"{final_target.name} 反击 {attacker.name} {counter_damage} 点伤害！")
            attacker.take_damage(counter_damage)
        
        # 标记攻击者使用了技能（影响星河技能）
        attacker.skill_used_this_turn = True
        
        return True
    
    def _execute_heal(self, player: Player, character: Character, heal_amount: int) -> bool:
        """执行回血行动"""
        if character.current_hp >= character.max_hp:
            print(f"{character.name} 生命值已满，无法回血")
            return False
            
        character.heal(heal_amount)
        print(f"{character.name} 回复了 {heal_amount} 点生命值，当前生命值：{character.current_hp}")
        
        # 标记使用了技能
        character.skill_used_this_turn = True
        
        return True
    
    def _execute_defend(self, character: Character, defense_amount: int) -> bool:
        """执行防御行动"""
        character.add_defense(defense_amount)
        print(f"{character.name} 获得 {defense_amount} 点防御，下次受伤减少")
        
        # 标记使用了技能
        character.skill_used_this_turn = True
        
        return True
    
    def _check_jun_protection(self, original_target: Character, 
                            target_player: Player) -> Character:
        """检查俊是否可以代替队友承受伤害"""
        # 找到队伍中的俊角色
        jun_character = None
        for char in target_player.characters:
            if (char.char_id == 'jun' and 
                char.is_alive and 
                char != original_target and
                not char.damage_blocked_for_teammate):
                jun_character = char
                break
        
        if jun_character:
            print(f"俊技能触发！{jun_character.name} 代替 {original_target.name} 承受伤害")
            jun_character.damage_blocked_for_teammate = True
            return jun_character
        
        return original_target
    
    def _get_target_player(self, target_character: Character) -> Optional[Player]:
        """根据目标角色获取对应的玩家"""
        for player in self.game_state.players:
            if target_character in player.characters:
                return player
        return None
    
    def process_turn_start(self, player: Player):
        """处理回合开始时的效果"""
        # 基础抽卡：每回合抽3张
        cards_to_draw = 3
        
        # Cafe+星河组合效果：额外抽取2张卡
        if 'cafe_xinhe' in player.team_effects:
            cards_to_draw += 2
            print(f"队伍效果触发！Cafe+星河组合额外抽取2张卡")
        
        # 阳光技能：对方上回合没有使用攻击卡时，额外抽取2张卡
        yangguang_char = self._find_character_by_id(player, 'yangguang')
        if (yangguang_char and yangguang_char.is_alive and 
            not player.opponent_used_attack_last_turn):
            cards_to_draw += 2
            print(f"阳光技能触发！对方上回合未使用攻击卡，额外抽取2张卡")
        
        # 执行抽卡
        drawn = player.draw_cards(cards_to_draw)
        print(f"玩家{player.player_id} 抽取了 {drawn} 张卡，手牌数量：{len(player.hand)}")
    
    def process_turn_end(self, player: Player):
        """处理回合结束时的效果"""
        # 星河技能：每回合不使用技能时抽取一个行动卡
        xinhe_char = self._find_character_by_id(player, 'xinhe')
        if xinhe_char and xinhe_char.is_alive and not xinhe_char.skill_used_this_turn:
            drawn = player.draw_cards(1)
            if drawn > 0:
                print(f"星河技能触发！未使用技能，额外抽取1张卡")
        
        # 重置所有角色的回合状态
        for char in player.characters:
            char.reset_turn_status()
    
    def _find_character_by_id(self, player: Player, 
                             char_id: str) -> Optional[Character]:
        """在玩家队伍中查找指定类型的角色"""
        for char in player.characters:
            if char.char_id == char_id:
                return char
        return None
    
    def check_victory_condition(self) -> Tuple[bool, Optional[int]]:
        """检查胜利条件"""
        for i, player in enumerate(self.game_state.players):
            if player.is_defeated():
                return True, 1 - i  # 返回获胜玩家的索引
        return False, None
    
    def get_available_targets(self, player: Player, action_card: ActionCard) -> List[Character]:
        """获取行动卡的可用目标"""
        if action_card.can_target_enemy():
            # 攻击卡只能攻击敌方存活角色
            opponent = self.game_state.players[1 - player.player_id + 1]
            return opponent.get_alive_characters()
        else:
            # 回血和防御只能对己方存活角色使用
            return player.get_alive_characters()
    
    def create_character(self, char_id: str) -> Character:
        """创建指定类型的角色"""
        return Character(char_id)


class GameAI:
    """简单的AI对手"""
    
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine
    
    def make_decision(self, player: Player) -> List[Tuple[Character, ActionCard, Character]]:
        """
        AI决策：返回要执行的行动列表
        每个元组包含：(使用技能的角色, 行动卡, 目标角色)
        """
        actions = []
        
        # 简单策略：优先攻击，其次回血，最后防御
        alive_chars = player.get_alive_characters()
        if not alive_chars or not player.hand:
            return actions
        
        for card in player.hand[:]:  # 使用切片复制，避免修改时出错
            if not player.hand:  # 手牌用完
                break
                
            # 选择使用技能的角色（随机选择存活角色）
            user_char = random.choice(alive_chars)
            
            # 根据卡牌类型选择目标
            targets = self.engine.get_available_targets(player, card)
            if not targets:
                continue
                
            target_char = self._select_target(card, targets, alive_chars)
            if target_char:
                actions.append((user_char, card, target_char))
        
        return actions
    
    def _select_target(self, action_card: ActionCard, available_targets: List[Character],
                      own_chars: List[Character]) -> Optional[Character]:
        """AI选择目标的逻辑"""
        if action_card.can_target_enemy():
            # 攻击：优先攻击血量最少的敌人
            return min(available_targets, key=lambda x: x.current_hp)
        elif action_card.effect_type == "heal":
            # 回血：优先治疗血量最少的己方角色
            injured_chars = [c for c in own_chars if c.current_hp < c.max_hp]
            if injured_chars:
                return min(injured_chars, key=lambda x: x.current_hp)
        elif action_card.effect_type == "defense":
            # 防御：随机选择一个己方角色
            return random.choice(own_chars) if own_chars else None
        
        return None


if __name__ == "__main__":
    # 简单测试
    game_state = GameState()
    engine = GameEngine(game_state)
    ai = GameAI(engine)
    
    # 创建测试角色
    char1 = engine.create_character('cafe')
    char2 = engine.create_character('xinhe')
    
    print("游戏引擎创建成功！")
    print(f"测试角色: {char1.name} (HP: {char1.current_hp})")
    print(f"测试角色: {char2.name} (HP: {char2.current_hp})")