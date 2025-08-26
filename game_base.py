"""
卡牌对战游戏基础类定义
包含卡牌、人物卡、行动卡、玩家、游戏状态等核心类
重构版本：支持从YAML配置文件加载数据
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
import random
from simple_data_loader import game_data


# 向后兼容性：保留原有的枚举类型，但标记为已弃用
class ActionType(Enum):
    """行动卡类型枚举 - 已弃用，保留用于向后兼容"""
    ATTACK = "攻击"
    HEAL = "回血"
    DEFEND = "防御"


class CharacterType(Enum):
    """人物卡类型枚举 - 已弃用，保留用于向后兼容"""
    CAFE = "Cafe"
    XINHE = "星河"
    YANGGUANG = "阳光"
    LIULI = "琉璃"
    JUN = "俊"


class TeamEffect(Enum):
    """特殊队伍效果枚举 - 已弃用，保留用于向后兼容"""
    JUN_LIULI = "俊琉璃组合"
    CAFE_XINHE = "Cafe星河组合"
    YANGGUANG_LIULI = "阳光琉璃组合"


class Card:
    """卡牌基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class ActionCard(Card):
    """行动卡类 - 重构版本，支持从配置创建"""
    def __init__(self, card_id: str, card_data: Optional[Dict[str, Any]] = None):
        self.card_id = card_id
        
        # 从配置数据或数据加载器获取卡牌信息
        if card_data:
            self.card_info = card_data
        else:
            self.card_info = game_data.get_action_card_info(card_id)
            if not self.card_info:
                raise ValueError(f"未找到行动卡配置: {card_id}")
        
        self.display_name = self.card_info.get('display_name', card_id)
        self.description = self.card_info.get('description', '')
        self.target_type = self.card_info.get('target_type', 'enemy')
        self.effect_type = self.card_info.get('effect_type', 'damage')
        self.base_value = self.card_info.get('base_value', 0)
        
        super().__init__(self.display_name, self.description)
        
    def get_base_value(self) -> int:
        """获取行动卡的基础数值"""
        return self.base_value
    
    def can_target_enemy(self) -> bool:
        """是否可以对敌方使用"""
        return self.target_type == 'enemy'
    
    def can_target_ally(self) -> bool:
        """是否可以对己方使用"""
        return self.target_type in ['ally', 'self']


class Character(Card):
    """人物卡类 - 重构版本，支持从配置创建"""
    def __init__(self, char_id: str, char_data: Optional[Dict[str, Any]] = None):
        self.char_id = char_id
        
        # 从配置数据或数据加载器获取角色信息
        if char_data:
            self.char_info = char_data
        else:
            self.char_info = game_data.get_character_info(char_id)
            if not self.char_info:
                raise ValueError(f"未找到角色配置: {char_id}")
        
        self.display_name = self.char_info.get('display_name', char_id)
        self.description = self.char_info.get('description', '')
        self.max_hp = self.char_info.get('max_hp', 15)
        self.skills = self.char_info.get('skills', [])
        
        # 游戏状态
        self.current_hp = self.max_hp
        self.defense_buff = 0  # 防御buff，下次受伤减少的点数
        self.is_alive = True
        
        # 技能状态跟踪
        self.first_damage_dealt = False  # 本回合是否已造成第一次伤害
        self.skill_used_this_turn = False  # 本回合是否使用过技能
        self.damage_taken_count = 0  # 本回合受伤次数
        self.damage_blocked_for_teammate = False  # 本回合是否已为队友承受伤害
        
        super().__init__(self.display_name, self.description)
    
    def take_damage(self, damage: int) -> Tuple[int, bool, int]:
        """
        受到伤害
        返回: (实际受到的伤害, 是否触发反击, 反击伤害)
        """
        if not self.is_alive:
            return 0, False, 0
            
        # 检查琉璃的特殊技能：1-6随机判定
        counter_damage = 0
        counter_triggered = False
        if self.char_id == 'liuli':
            # 查找幸运反击技能
            for skill in self.skills:
                if skill.get('effect') == 'lucky_counter':
                    skill_value = skill.get('value', {})
                    dice_range = skill_value.get('dice_range', [1, 6])
                    lucky_number = skill_value.get('lucky_number', 6)
                    counter_dmg = skill_value.get('counter_damage', 2)
                    
                    roll = random.randint(dice_range[0], dice_range[1])
                    if roll == lucky_number:
                        print(f"{self.name} 琉璃技能触发！判定结果：{roll}，免疫此次攻击并反击{counter_dmg}点！")
                        return 0, True, counter_dmg
                    else:
                        print(f"{self.name} 琉璃技能判定：{roll}，未能免疫攻击")
                    break
        
        # 计算实际伤害
        actual_damage = max(0, damage - self.defense_buff)
        
        # 俊的减伤技能：前两次伤害减1
        if self.char_id == 'jun':
            for skill in self.skills:
                if skill.get('effect') == 'damage_reduction':
                    skill_value = skill.get('value', {})
                    max_times = skill_value.get('max_times', 2)
                    reduction = skill_value.get('reduction', 1)
                    
                    if self.damage_taken_count < max_times:
                        actual_damage = max(0, actual_damage - reduction)
                        print(f"{self.name} 俊技能触发！前{max_times}次伤害减{reduction}，实际伤害：{actual_damage}")
                    break
        
        self.damage_taken_count += 1
        
        # 扣除生命值
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # 重置防御buff
        if self.defense_buff > 0:
            print(f"{self.name} 的防御效果抵挡了 {min(damage, self.defense_buff)} 点伤害")
            self.defense_buff = max(0, self.defense_buff - damage)
        
        # 检查是否死亡
        if self.current_hp <= 0:
            self.is_alive = False
            print(f"{self.name} 已被击倒！")
        
        return actual_damage, counter_triggered, counter_damage
    
    def heal(self, amount: int):
        """回复生命值"""
        if not self.is_alive:
            return
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def add_defense(self, amount: int):
        """增加防御buff"""
        self.defense_buff += amount
    
    def reset_turn_status(self):
        """重置回合状态"""
        self.first_damage_dealt = False
        self.skill_used_this_turn = False
        self.damage_taken_count = 0
        self.damage_blocked_for_teammate = False
    
    def has_skill(self, skill_effect: str) -> bool:
        """检查角色是否有指定效果的技能"""
        for skill in self.skills:
            if skill.get('effect') == skill_effect:
                return True
        return False
    
    def get_skill_value(self, skill_effect: str) -> Any:
        """获取指定技能的数值"""
        for skill in self.skills:
            if skill.get('effect') == skill_effect:
                return skill.get('value')
        return None


class Player:
    """玩家类 - 重构版本"""
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.characters: List[Character] = []  # 最多2个角色
        self.hand: List[ActionCard] = []  # 手牌
        self.deck: List[str] = []  # 牌库（存储卡牌ID）
        self.discard_pile: List[str] = []  # 弃牌堆（存储卡牌ID）
        self.team_effects: List[str] = []  # 队伍效果ID列表
        self.opponent_used_attack_last_turn = False  # 阳光技能：对方上回合是否使用攻击卡
        
        # 从配置初始化牌库
        self._initialize_deck()
    
    def _initialize_deck(self):
        """从配置初始化牌库"""
        self.deck = game_data.create_deck_from_config()
        random.shuffle(self.deck)
    
    def draw_cards(self, count: int) -> int:
        """
        抽取卡牌
        返回实际抽取的卡牌数量
        """
        drawn = 0
        for _ in range(count):
            if self.deck:
                card_id = self.deck.pop()
                card = ActionCard(card_id)
                self.hand.append(card)
                drawn += 1
            elif self.discard_pile:
                # 牌库用完，重洗弃牌堆
                print(f"玩家{self.player_id} 的牌库用完，重洗弃牌堆...")
                self.deck = self.discard_pile.copy()
                self.discard_pile = []
                random.shuffle(self.deck)
                if self.deck:
                    card_id = self.deck.pop()
                    card = ActionCard(card_id)
                    self.hand.append(card)
                    drawn += 1
            else:
                break  # 没有卡可抽了
        return drawn
    
    def use_card(self, card_index: int) -> Optional[ActionCard]:
        """使用手牌中的卡牌"""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            # 将卡牌ID加入弃牌堆
            self.discard_pile.append(card.card_id)
            return card
        return None
    
    def add_character(self, character: Character):
        """添加角色到队伍"""
        if len(self.characters) < 2:
            self.characters.append(character)
            self._check_team_effects()
    
    def _check_team_effects(self):
        """检查并激活队伍效果"""
        if len(self.characters) != 2:
            return
            
        char_ids = {char.char_id for char in self.characters}
        team_effects_config = game_data.get_team_effects()
        
        for effect_id, effect_info in team_effects_config.items():
            required_chars = set(effect_info.get('characters', []))
            if required_chars.issubset(char_ids):
                self.team_effects.append(effect_id)
                print(f"队伍效果激活：{effect_info.get('name', effect_id)}")
    
    def get_alive_characters(self) -> List[Character]:
        """获取存活的角色"""
        return [char for char in self.characters if char.is_alive]
    
    def is_defeated(self) -> bool:
        """判断是否被击败（所有角色都死亡）"""
        return len(self.get_alive_characters()) == 0


class GameState:
    """游戏状态管理类 - 重构版本"""
    def __init__(self):
        self.players: List[Player] = [Player(1), Player(2)]
        self.current_player = 0  # 当前行动玩家索引
        self.turn_count = 0
        self.game_over = False
        self.winner = None
        self.available_characters = list(game_data.get_all_characters().keys())  # 可选择的角色ID
    
    def get_current_player(self) -> Player:
        """获取当前行动的玩家"""
        return self.players[self.current_player]
    
    def get_opponent_player(self) -> Player:
        """获取对手玩家"""
        return self.players[1 - self.current_player]
    
    def switch_turn(self):
        """切换回合"""
        # 重置当前玩家所有角色的回合状态
        for char in self.get_current_player().characters:
            char.reset_turn_status()
            
        self.current_player = 1 - self.current_player
        self.turn_count += 1
    
    def check_game_over(self):
        """检查游戏是否结束"""
        for i, player in enumerate(self.players):
            if player.is_defeated():
                self.game_over = True
                self.winner = 1 - i  # 另一个玩家获胜
                break


if __name__ == "__main__":
    # 简单测试
    try:
        game = GameState()
        print("卡牌对战游戏基础类创建成功！")
        print(f"玩家1牌库大小: {len(game.players[0].deck)}")
        print(f"玩家2牌库大小: {len(game.players[1].deck)}")
        print(f"可选角色: {game.available_characters}")
        
        # 测试创建角色
        if game.available_characters:
            char_id = game.available_characters[0]
            test_char = Character(char_id)
            print(f"测试角色: {test_char.display_name} - {test_char.description}")
        
        # 测试创建行动卡
        action_cards = game_data.get_all_action_cards()
        if action_cards:
            card_id = list(action_cards.keys())[0]
            test_card = ActionCard(card_id)
            print(f"测试行动卡: {test_card.display_name} - {test_card.description}")
            
    except Exception as e:
        print(f"测试出错: {e}")
        print("请确保YAML配置文件存在且格式正确")