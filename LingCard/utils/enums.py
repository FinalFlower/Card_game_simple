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
    # 剑技类卡牌
    SWORD_ATTACK = "剑技攻击"  # 基础剑技攻击（锐斩、滑刃）
    SWORD_SPECIAL = "剑技特殊"  # 特殊剑技（披荆斩棘、拔刀斩）
    SWORD_SUPPORT = "剑技辅助"  # 剑技辅助（祛痕、剑锋直转、轮斩）
    
    # 重铸系列
    REFORGE = "重铸"  # 重铸系列卡牌
    
    # 解放系列
    LIBERATION = "解放"  # 解放系列卡牌
    
    # 保留原有类型以保持兼容性
    ATTACK = "攻击"
    HEAL = "回血"
    DEFEND = "防御"
    POISON = "毒素"
    SPECIAL = "特殊"

class TeamEffect(Enum):
    """特殊队伍效果枚举"""
    JUN_LIULI = "俊琉璃组合"
    CAFE_XINHE = "Cafe星河组合"
    YANGGUANG_LIULI = "阳光琉璃组合"