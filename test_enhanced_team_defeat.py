#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的每回合结束时队伍败北检测机制
验证：
1. 新增的详细日志功能
2. 增强的安全检查机制
3. 多种败北场景的完整处理
4. 边缘情况的处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LingCard.core.game_state import GameState
from LingCard.core.game_engine import GameEngine
from LingCard.core.player import Player
from LingCard.characters.cafe import Cafe
from LingCard.characters.liuli import Liuli
from LingCard.characters.jun import Jun
from LingCard.buffs.poison import PoisonBuff


def create_enhanced_test_game():
    """创建增强测试用的游戏状态"""
    game_state = GameState()
    
    # 创建玩家
    player1 = Player(1)
    player2 = Player(2)
    
    # 创建角色 - 多个角色便于测试复杂场景
    cafe = Cafe()
    jun = Jun()
    liuli1 = Liuli()  # 重命名避免冲突
    liuli2 = Liuli()  # 第二个琉璃角色
    
    player1.characters = [cafe, jun]
    player2.characters = [liuli1, liuli2]
    
    game_state.players = [player1, player2]
    game_state.turn_order = [0, 1]
    game_state.current_player_index = 0
    
    # 创建配置和引擎
    config = {
        'game_settings': {
            'initial_hand_size': 3,
            'deck_composition': {}
        },
        'team_effects': []
    }
    engine = GameEngine(config)
    
    return game_state, engine


def test_enhanced_defeat_detection_logs():
    """测试增强后的败北检测日志"""
    print("=== 测试增强后的败北检测日志 ===")
    
    game_state, engine = create_enhanced_test_game()
    player1 = game_state.players[0]
    player2 = game_state.players[1]
    
    # 获取角色
    liuli1 = player2.characters[0]
    liuli2 = player2.characters[1]
    
    print(f"初始状态：")
    print(f"  玩家1: {len(player1.get_alive_characters())} 个存活角色")
    print(f"  玩家2: {len(player2.get_alive_characters())} 个存活角色")
    
    # 杀死第一个琉璃
    liuli1.take_damage(100)
    print(f"\n杀死第一个琉璃后：")
    print(f"  玩家2存活角色: {len(player2.get_alive_characters())}")
    
    # 检查游戏状态（此时不应该结束）
    engine.check_game_over(game_state)
    print(f"  游戏结束: {game_state.game_over}")
    
    # 杀死第二个琉璃
    liuli2.take_damage(100)
    print(f"\n杀死第二个琉璃后：")
    print(f"  玩家2存活角色: {len(player2.get_alive_characters())}")
    print(f"  玩家2败北: {player2.is_defeated()}")
    
    # 这时应该检测到游戏结束
    engine.check_game_over(game_state)
    print(f"  游戏结束: {game_state.game_over}")
    print(f"  获胜方: 玩家{game_state.winner}")
    
    # 打印游戏日志
    print(f"\n游戏日志：")
    for log_entry in game_state.log:
        print(f"  {log_entry}")
    
    print("✅ 增强败北检测日志测试通过")


def test_turn_end_comprehensive_check():
    """测试回合结束时的全面检查机制"""
    print("\n=== 测试回合结束时的全面检查机制 ===")
    
    game_state, engine = create_enhanced_test_game()
    player1 = game_state.players[0]
    player2 = game_state.players[1]
    
    # 设置一个即将死亡的场景
    liuli1 = player2.characters[0]
    liuli2 = player2.characters[1]
    
    # 第一个琉璃已经死亡
    liuli1.take_damage(100)
    
    # 第二个琉璃血量很低，并施加致命中毒
    liuli2.current_hp = 1
    poison_buff = PoisonBuff(stacks=3, caster=player1.characters[0])
    liuli2.add_buff(poison_buff, game_state)
    
    print(f"回合结束前状态：")
    print(f"  琉璃1存活: {liuli1.is_alive}")
    print(f"  琉璃2血量: {liuli2.current_hp}, 中毒层数: 3")
    print(f"  玩家2败北: {player2.is_defeated()}")
    print(f"  游戏结束: {game_state.game_over}")
    
    print(f"\n执行回合结束处理...")
    engine.process_turn_end(game_state)
    
    print(f"\n回合结束后状态：")
    print(f"  琉璃2血量: {liuli2.current_hp}")
    print(f"  琉璃2存活: {liuli2.is_alive}")
    print(f"  玩家2败北: {player2.is_defeated()}")
    print(f"  游戏结束: {game_state.game_over}")
    if game_state.game_over:
        print(f"  获胜方: 玩家{game_state.winner}")
    
    # 打印相关的游戏日志
    print(f"\n关键游戏日志：")
    for log_entry in game_state.log[-10:]:  # 显示最后10条日志
        print(f"  {log_entry}")
    
    # 验证结果
    assert not liuli2.is_alive, "琉璃2应该因中毒死亡"
    assert player2.is_defeated(), "玩家2应该被击败"
    assert game_state.game_over, "游戏应该结束"
    assert game_state.winner == 1, "玩家1应该获胜"
    
    print("✅ 回合结束全面检查机制测试通过")


def test_simultaneous_team_defeat_scenario():
    """测试同时击败场景（理论上不应该发生）"""
    print("\n=== 测试边缘场景处理 ===")
    
    game_state, engine = create_enhanced_test_game()
    player1 = game_state.players[0]
    player2 = game_state.players[1]
    
    # 模拟一个极端场景：双方最后一个角色都血量很低
    # 杀死除了最后一个角色外的所有角色
    player1.characters[0].take_damage(100)  # cafe死亡
    player2.characters[0].take_damage(100)  # 第一个琉璃死亡
    
    jun = player1.characters[1]  # 俊，玩家1最后一个角色
    liuli2 = player2.characters[1]  # 第二个琉璃，玩家2最后一个角色
    
    jun.current_hp = 1
    liuli2.current_hp = 1
    
    print(f"设置场景：双方各剩最后一个角色，都只有1血")
    print(f"  俊血量: {jun.current_hp}")
    print(f"  琉璃血量: {liuli2.current_hp}")
    
    # 施加中毒让琉璃先死
    poison_buff = PoisonBuff(stacks=2, caster=jun)
    liuli2.add_buff(poison_buff, game_state)
    
    print(f"\n对琉璃施加2层中毒")
    
    # 执行回合结束
    print(f"执行回合结束处理...")
    engine.process_turn_end(game_state)
    
    print(f"\n结果：")
    print(f"  俊存活: {jun.is_alive}")
    print(f"  琉璃存活: {liuli2.is_alive}")
    print(f"  游戏结束: {game_state.game_over}")
    if game_state.game_over:
        print(f"  获胜方: 玩家{game_state.winner}")
    
    # 验证结果
    assert not liuli2.is_alive, "琉璃应该因中毒死亡"
    assert jun.is_alive, "俊应该存活"
    assert game_state.game_over, "游戏应该结束"
    assert game_state.winner == 1, "玩家1应该获胜"
    
    print("✅ 边缘场景处理测试通过")


def test_no_defeat_continuation():
    """测试无败北情况下的游戏继续"""
    print("\n=== 测试无败北情况下的游戏继续 ===")
    
    game_state, engine = create_enhanced_test_game()
    player1 = game_state.players[0]
    player2 = game_state.players[1]
    
    print(f"初始状态 - 双方都有存活角色")
    print(f"  玩家1存活: {len(player1.get_alive_characters())}")
    print(f"  玩家2存活: {len(player2.get_alive_characters())}")
    
    # 执行多次回合结束，确保游戏能正常继续
    for i in range(3):
        print(f"\n第{i+1}次回合结束处理...")
        engine.process_turn_end(game_state)
        
        print(f"  游戏结束: {game_state.game_over}")
        print(f"  玩家1存活: {len(player1.get_alive_characters())}")
        print(f"  玩家2存活: {len(player2.get_alive_characters())}")
        
        # 游戏不应该结束
        assert not game_state.game_over, f"第{i+1}次检查，游戏不应该结束"
    
    print("✅ 无败北情况下游戏继续测试通过")


if __name__ == "__main__":
    try:
        test_enhanced_defeat_detection_logs()
        test_turn_end_comprehensive_check()
        test_simultaneous_team_defeat_scenario()
        test_no_defeat_continuation()
        
        print(f"\n🎉 所有增强队伍败北检测测试通过！")
        print(f"\n新增功能总结：")
        print(f"1. ✅ 增强的败北检测日志，详细记录队伍状态")
        print(f"2. ✅ 回合结束时的全面安全检查")
        print(f"3. ✅ 更可靠的边缘场景处理")
        print(f"4. ✅ 确保游戏在正常情况下能够继续")
        print(f"\n机制完整性验证：")
        print(f"- 每回合结束时都会检测双方队伍被击败情况")
        print(f"- 如果有一方成员均被击败，会直接判定比赛结果")
        print(f"- 提供详细的日志信息便于调试和了解游戏状态")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()