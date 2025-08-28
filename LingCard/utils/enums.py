# LingCard/utils/enums.py
from enum import Enum

class GamePhase(Enum):
    """游戏状态机阶段"""
    INITIALIZING = "初始化"
    LOBBY = "大厅"
    DECK_BUILDER = "配卡界面"
    MODE_SELECTION = "模式选择"
    CHARACTER_SELECTION = "角色选择"
    GAME_LOOP = "游戏主循环"
    PLAYER_TURN = "玩家回合"
    AI_TURN = "AI回合"
    TURN_END = "回合结束"
    GAME_OVER = "游戏结束"
    EXIT = "退出"

class ActionType(Enum):
    """行动卡类型枚举"""
    ATTACK = "攻击"
    HEAL = "回血"
    DEFEND = "防御"
    POISON = "毒素"  # 新增：毒素类型，用于施加中毒等debuff
    SPECIAL = "特殊"  # 新增：特殊类型，用于特殊效果卡牌

class TeamEffect(Enum):
    """特殊队伍效果枚举"""
    JUN_LIULI = "俊琉璃组合"
    CAFE_XINHE = "Cafe星河组合"
    YANGGUANG_LIULI = "阳光琉璃组合"