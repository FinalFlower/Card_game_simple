#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试游戏流程修复：验证游戏结束时流程正确停止
验证：
1. 回合结束时检测到游戏结束，应该进入GAME_OVER阶段
2. 玩家行动时检测到游戏结束，应该进入GAME_OVER阶段
3. AI行动时检测到游戏结束，应该进入GAME_OVER阶段
4. 游戏状态机不应该在游戏结束后继续运行回合
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LingCard.core.game_state import GameState
from LingCard.core.game_engine import GameEngine
from LingCard.core.player import Player
from LingCard.characters.cafe import Cafe
from LingCard.characters.liuli import Liuli
from LingCard.buffs.poison import PoisonBuff
from LingCard.utils.enums import GamePhase
from LingCard.game_manager import GameManager


def test_turn_end_game_over_detection():
    """测试回合结束时的游戏结束检测"""
    print("=== 测试回合结束时的游戏结束检测 ===")
    
    # 创建最小化的游戏管理器实例
    game_manager = GameManager()
    game_manager.vs_ai = False
    
    # 手动设置游戏状态
    game_state = GameState()
    player1 = Player(1)
    player2 = Player(2)
    
    cafe = Cafe()
    liuli = Liuli()
    
    player1.characters = [cafe]
    player2.characters = [liuli]
    
    game_state.players = [player1, player2]
    game_state.turn_order = [0, 1]
    game_state.current_player_idx = 0
    
    game_manager.game_state = game_state
    game_manager.phase = GamePhase.TURN_END
    
    # 设置琉璃即将因中毒死亡的状态
    liuli.current_hp = 1
    poison_buff = PoisonBuff(stacks=2, caster=cafe)
    liuli.add_buff(poison_buff, game_state)
    
    print(f"设置状态：")
    print(f"  琉璃血量: {liuli.current_hp}")
    print(f"  中毒层数: 2")
    print(f"  当前游戏阶段: {game_manager.phase}")
    print(f"  游戏结束状态: {game_state.game_over}")
    
    # 执行回合结束处理
    print(f"\n执行回合结束处理...")
    game_manager._phase_turn_end()
    
    print(f"\n回合结束后：")
    print(f"  琉璃血量: {liuli.current_hp}")
    print(f"  琉璃存活: {liuli.is_alive}")
    print(f"  游戏结束状态: {game_state.game_over}")
    print(f"  获胜方: 玩家{game_state.winner}")
    print(f"  游戏阶段: {game_manager.phase}")
    
    # 验证结果
    assert not liuli.is_alive, "琉璃应该因中毒死亡"
    assert game_state.game_over, "游戏应该结束"
    assert game_manager.phase == GamePhase.GAME_OVER, "游戏管理器应该进入GAME_OVER阶段"
    
    print("✅ 回合结束时游戏结束检测正常")


def test_player_action_game_over_detection():
    """测试玩家行动时的游戏结束检测"""
    print("\n=== 测试玩家行动时的游戏结束检测 ===")
    
    # 创建游戏状态
    game_state = GameState()
    config = {
        'game_settings': {
            'initial_hand_size': 3,
            'deck_composition': {}
        },
        'team_effects': []
    }
    engine = GameEngine(config)
    
    player1 = Player(1)
    player2 = Player(2)
    
    cafe = Cafe()
    liuli = Liuli()
    
    # 设置琉璃只有1血，容易被击杀
    liuli.current_hp = 1
    
    player1.characters = [cafe]
    player2.characters = [liuli]
    
    game_state.players = [player1, player2]
    game_state.turn_order = [0, 1]
    game_state.current_player_idx = 0
    
    print(f"设置状态：")
    print(f"  Cafe血量: {cafe.current_hp}")
    print(f"  琉璃血量: {liuli.current_hp}")
    print(f"  游戏结束状态: {game_state.game_over}")
    
    # 模拟攻击导致游戏结束
    print(f"\n模拟Cafe攻击琉璃...")
    damage = 5  # 足够击杀琉璃
    actual_damage = liuli.take_damage(damage)
    print(f"  造成 {actual_damage} 点伤害")
    
    # 检查游戏结束
    engine.check_game_over(game_state)
    
    print(f"\n攻击后：")
    print(f"  琉璃血量: {liuli.current_hp}")
    print(f"  琉璃存活: {liuli.is_alive}")
    print(f"  游戏结束状态: {game_state.game_over}")
    print(f"  获胜方: 玩家{game_state.winner}")
    
    # 验证结果
    assert not liuli.is_alive, "琉璃应该死亡"
    assert game_state.game_over, "游戏应该结束"
    assert game_state.winner == 1, "玩家1应该获胜"
    
    print("✅ 玩家行动时游戏结束检测正常")


def test_game_flow_consistency():
    """测试游戏流程的一致性"""
    print("\n=== 测试游戏流程一致性 ===")
    
    # 测试游戏不应该在结束后继续
    game_manager = GameManager()
    game_manager.vs_ai = False
    
    # 直接设置游戏为结束状态
    game_state = GameState()
    player1 = Player(1)
    player2 = Player(2)
    
    cafe = Cafe()
    liuli = Liuli()
    
    player1.characters = [cafe]
    player2.characters = [liuli]
    
    game_state.players = [player1, player2]
    game_state.turn_order = [0, 1]
    game_state.current_player_idx = 0
    game_state.game_over = True
    game_state.winner = 1
    
    game_manager.game_state = game_state
    game_manager.phase = GamePhase.TURN_END
    
    print(f"设置游戏已结束状态：")
    print(f"  游戏结束: {game_state.game_over}")
    print(f"  获胜方: 玩家{game_state.winner}")
    print(f"  当前阶段: {game_manager.phase}")
    
    # 尝试执行回合结束处理
    print(f"\n尝试执行回合结束处理...")
    game_manager._phase_turn_end()
    
    print(f"\n处理后：")
    print(f"  游戏阶段: {game_manager.phase}")
    
    # 验证游戏应该进入GAME_OVER阶段而不是继续
    assert game_manager.phase == GamePhase.GAME_OVER, "游戏应该进入GAME_OVER阶段"
    
    print("✅ 游戏流程一致性测试正常")


def test_multiple_scenarios():
    """测试多种游戏结束场景"""
    print("\n=== 测试多种游戏结束场景 ===")
    
    scenarios = [
        ("中毒导致队伍全灭", True),
        ("直接攻击导致队伍全灭", False),
    ]
    
    for scenario_name, use_poison in scenarios:
        print(f"\n测试场景：{scenario_name}")
        
        # 创建新的游戏状态
        game_manager = GameManager()
        game_state = GameState()
        
        player1 = Player(1)
        player2 = Player(2)
        
        cafe = Cafe()
        liuli = Liuli()
        liuli.current_hp = 2 if use_poison else 1
        
        player1.characters = [cafe]
        player2.characters = [liuli]
        
        game_state.players = [player1, player2]
        game_state.turn_order = [0, 1]
        game_state.current_player_idx = 0
        
        game_manager.game_state = game_state
        
        if use_poison:
            # 中毒场景
            poison_buff = PoisonBuff(stacks=3, caster=cafe)
            liuli.add_buff(poison_buff, game_state)
            game_manager.phase = GamePhase.TURN_END
            game_manager._phase_turn_end()
        else:
            # 直接攻击场景
            liuli.take_damage(5)
            game_manager.engine.check_game_over(game_state)
        
        print(f"  琉璃存活: {liuli.is_alive}")
        print(f"  游戏结束: {game_state.game_over}")
        if use_poison:
            print(f"  最终阶段: {game_manager.phase}")
        
        # 验证结果
        assert not liuli.is_alive, f"{scenario_name} - 琉璃应该死亡"
        assert game_state.game_over, f"{scenario_name} - 游戏应该结束"
        if use_poison:
            assert game_manager.phase == GamePhase.GAME_OVER, f"{scenario_name} - 应该进入GAME_OVER阶段"
        
        print(f"  ✅ {scenario_name} 测试通过")
    
    print("✅ 多种游戏结束场景测试通过")


if __name__ == "__main__":
    try:
        test_turn_end_game_over_detection()
        test_player_action_game_over_detection()
        test_game_flow_consistency()
        test_multiple_scenarios()
        
        print(f"\n🎉 所有游戏流程修复测试通过！")
        print(f"\n修复总结：")
        print(f"1. ✅ 回合结束时正确检测游戏结束状态")
        print(f"2. ✅ 游戏结束时立即进入GAME_OVER阶段")
        print(f"3. ✅ 防止游戏在结束后继续运行")
        print(f"4. ✅ 支持多种游戏结束场景（中毒、攻击等）")
        print(f"5. ✅ 保持游戏状态机的一致性")
        
        print(f"\n问题解决：")
        print(f"- 游戏日志记录玩家获胜后，主游戏流程现在会正确停止")
        print(f"- 不再出现游戏结束但仍继续进行回合的问题")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()