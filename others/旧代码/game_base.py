"""
卡牌对战游戏基础类定义
包含卡牌、人物卡、行动卡、玩家、游戏状态等核心类
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
import random


class ActionType(Enum):
    """行动卡类型枚举"""
    ATTACK = "攻击"  # 减少对方3点生命值
    HEAL = "回血"    # 增加自身2点生命值  
    DEFEND = "防御"  # 下一次受到伤害减少1点


class CharacterType(Enum):
    """人物卡类型枚举"""
    CAFE = "Cafe"      # 每回合第一次造成伤害时伤害加1
    XINHE = "星河"     # 每回合不使用技能时抽取一个行动卡
    YANGGUANG = "阳光" # 对方回合没有使用攻击卡时，下回合额外抽取2张卡
    LIULI = "琉璃"     # 受到攻击时1-6随机，6时免疫攻击并反击2点
    JUN = "俊"         # 可以帮队友承受伤害，每回合一次，前两次伤害减1


class TeamEffect(Enum):
    """特殊队伍效果枚举"""
    JUN_LIULI = "俊琉璃组合"    # 每回合第一次攻击加1
    CAFE_XINHE = "Cafe星河组合"  # 每回合额外抽取2张卡
    YANGGUANG_LIULI = "阳光琉璃组合"  # 免除第一次伤害


class Card:
    """卡牌基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class ActionCard(Card):
    """行动卡类"""
    def __init__(self, action_type: ActionType):
        self.action_type = action_type
        descriptions = {
            ActionType.ATTACK: "攻击：减少对方3点生命值",
            ActionType.HEAL: "回血：增加自身2点生命值", 
            ActionType.DEFEND: "防御：下一次受到伤害减少1点"
        }
        super().__init__(action_type.value, descriptions[action_type])
        
    def get_base_value(self) -> int:
        """获取行动卡的基础数值"""
        values = {
            ActionType.ATTACK: 3,
            ActionType.HEAL: 2,
            ActionType.DEFEND: 1
        }
        return values[self.action_type]


class Character(Card):
    """人物卡类"""
    def __init__(self, character_type: CharacterType):
        self.character_type = character_type
        self.max_hp = 15  # 所有角色初始血量为15
        self.current_hp = 15
        self.defense_buff = 0  # 防御buff，下次受伤减少的点数
        self.is_alive = True
        
        # 技能状态跟踪
        self.first_damage_dealt = False  # Cafe技能：本回合是否已造成第一次伤害
        self.skill_used_this_turn = False  # 星河技能：本回合是否使用过技能
        self.damage_taken_count = 0  # 俊技能：本回合受伤次数
        self.damage_blocked_for_teammate = False  # 俊技能：本回合是否已为队友承受伤害
        
        descriptions = {
            CharacterType.CAFE: "Cafe：每回合第一次造成伤害时伤害加1",
            CharacterType.XINHE: "星河：每回合不使用技能时抽取一个行动卡",
            CharacterType.YANGGUANG: "阳光：对方回合没有使用攻击卡时，下回合额外抽取2张卡",
            CharacterType.LIULI: "琉璃：受到攻击时进行1-6随机判定，6时免疫并反击2点",
            CharacterType.JUN: "俊：可以帮队友承受伤害（每回合一次），前两次伤害减1"
        }
        
        super().__init__(character_type.value, descriptions[character_type])
    
    def take_damage(self, damage: int) -> Tuple[int, bool, int]:
        """
        受到伤害
        返回: (实际受到的伤害, 是否触发琉璃反击, 反击伤害)
        """
        if not self.is_alive:
            return 0, False, 0
            
        # 琉璃的特殊技能：1-6随机判定
        counter_damage = 0
        counter_triggered = False
        if self.character_type == CharacterType.LIULI:
            roll = random.randint(1, 6)
            if roll == 6:
                print(f"{self.name} 琉璃技能触发！判定结果：{roll}，免疫此次攻击并反击2点！")
                return 0, True, 2
            else:
                print(f"{self.name} 琉璃技能判定：{roll}，未能免疫攻击")
        
        # 计算实际伤害
        actual_damage = max(0, damage - self.defense_buff)
        
        # 俊的减伤技能：前两次伤害减1
        if self.character_type == CharacterType.JUN and self.damage_taken_count < 2:
            actual_damage = max(0, actual_damage - 1)
            print(f"{self.name} 俊技能触发！前两次伤害减1，实际伤害：{actual_damage}")
        
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


class Player:
    """玩家类"""
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.characters: List[Character] = []  # 最多2个角色
        self.hand: List[ActionCard] = []  # 手牌
        self.deck: List[ActionCard] = []  # 牌库
        self.discard_pile: List[ActionCard] = []  # 弃牌堆
        self.team_effects: List[TeamEffect] = []  # 队伍效果
        self.opponent_used_attack_last_turn = False  # 阳光技能：对方上回合是否使用攻击卡
        
        # 初始化牌库：攻击、防御、回血各10张
        self._initialize_deck()
    
    def _initialize_deck(self):
        """初始化30张行动卡牌库"""
        self.deck = []
        for _ in range(10):
            self.deck.append(ActionCard(ActionType.ATTACK))
            self.deck.append(ActionCard(ActionType.HEAL))
            self.deck.append(ActionCard(ActionType.DEFEND))
        random.shuffle(self.deck)
    
    def draw_cards(self, count: int) -> int:
        """
        抽取卡牌
        返回实际抽取的卡牌数量
        """
        drawn = 0
        for _ in range(count):
            if self.deck:
                card = self.deck.pop()
                self.hand.append(card)
                drawn += 1
            elif self.discard_pile:
                # 牌库用完，重洗弃牌堆
                print(f"玩家{self.player_id} 的牌库用完，重洗弃牌堆...")
                self.deck = self.discard_pile.copy()
                self.discard_pile = []
                random.shuffle(self.deck)
                if self.deck:
                    card = self.deck.pop()
                    self.hand.append(card)
                    drawn += 1
            else:
                break  # 没有卡可抽了
        return drawn
    
    def use_card(self, card_index: int) -> Optional[ActionCard]:
        """使用手牌中的卡牌"""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            self.discard_pile.append(card)
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
            
        char_types = {char.character_type for char in self.characters}
        
        # 俊+琉璃组合
        if CharacterType.JUN in char_types and CharacterType.LIULI in char_types:
            self.team_effects.append(TeamEffect.JUN_LIULI)
            
        # Cafe+星河组合  
        if CharacterType.CAFE in char_types and CharacterType.XINHE in char_types:
            self.team_effects.append(TeamEffect.CAFE_XINHE)
            
        # 阳光+琉璃组合
        if CharacterType.YANGGUANG in char_types and CharacterType.LIULI in char_types:
            self.team_effects.append(TeamEffect.YANGGUANG_LIULI)
    
    def get_alive_characters(self) -> List[Character]:
        """获取存活的角色"""
        return [char for char in self.characters if char.is_alive]
    
    def is_defeated(self) -> bool:
        """判断是否被击败（所有角色都死亡）"""
        return len(self.get_alive_characters()) == 0


class GameState:
    """游戏状态管理类"""
    def __init__(self):
        self.players: List[Player] = [Player(1), Player(2)]
        self.current_player = 0  # 当前行动玩家索引
        self.turn_count = 0
        self.game_over = False
        self.winner = None
        self.available_characters = list(CharacterType)  # 可选择的角色
    
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
    game = GameState()
    print("卡牌对战游戏基础类创建成功！")
    print(f"玩家1牌库大小: {len(game.players[0].deck)}")
    print(f"玩家2牌库大小: {len(game.players[1].deck)}")