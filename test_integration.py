#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：在游戏环境中测试新的发电等级机制
验证新机制与游戏引擎的兼容性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LingCard.core.game_state import GameState
from LingCard.core.player import Player
from LingCard.characters.cafe import Cafe
from LingCard.characters.liuli import Liuli
from LingCard.cards.attack import AttackCard

def test_game_integration():
    """测试新发电等级机制与游戏引擎的集成"""
    print("=== 游戏集成测试：新发电等级机制 ===\n")
    
    # 创建游戏状态（使用正确的构造函数）
    game_state = GameState()
    
    # 创建玩家和角色
    player1 = Player(0)
    player2 = Player(1)
    
    cafe = Cafe()
    liuli = Liuli()
    
    player1.characters = [cafe]
    player2.characters = [liuli]
    
    game_state.players = [player1, player2]
    game_state.turn_order = [0, 1]
    
    print(f"Cafe 初始发电等级: {cafe.energy_system.generation_level}")
    print(f"Cafe 升级阈值: {cafe.upgrade_thresholds}")
    print(f"琉璃 初始发电等级: {liuli.energy_system.generation_level}")
    print(f"琉璃 升级阈值: {liuli.upgrade_thresholds}")
    
    # 模拟攻击过程，观察发电等级变化
    print("\n--- 模拟战斗过程 ---")
    
    # Cafe 攻击 琉璃 多次，观察发电等级提升
    for round_num in range(1, 8):
        print(f"\n第{round_num}回合:")
        
        # Cafe攻击琉璃
        damage = 3  # 基础攻击伤害
        actual_damage = liuli.take_damage(damage)
        print(f"  Cafe 攻击琉璃，造成 {actual_damage} 点伤害")
        
        # 累积发电等级
        old_level = cafe.energy_system.generation_level
        level_up = cafe.add_damage_to_generation(actual_damage, game_state)
        new_level = cafe.energy_system.generation_level
        
        print(f"  Cafe 发电等级: {old_level} -> {new_level}")
        print(f"  Cafe 累积伤害: {cafe.energy_system.accumulated_damage}")
        print(f"  Cafe 电能状态: {cafe.energy_system.current_energy}/{cafe.energy_system.get_energy_limit()}")
        
        if level_up:
            print(f"  🎉 Cafe 发电等级提升！")
        
        if new_level >= cafe.energy_system.max_generation_level:
            print(f"  🔴 Cafe 已达到最大发电等级!")
            break
        
        # 恢复琉璃的血量，以便继续测试
        liuli.current_hp = liuli.max_hp
        liuli.is_alive = True
    
    # 测试最终状态
    print(f"\n=== 最终状态 ===")
    print(f"Cafe:")
    print(f"  发电等级: {cafe.energy_system.generation_level}/{cafe.energy_system.max_generation_level}")
    print(f"  累积伤害: {cafe.energy_system.accumulated_damage}")
    print(f"  电能状态: {cafe.energy_system.current_energy}/{cafe.energy_system.get_energy_limit()}")
    print(f"  行动槽数: {cafe.energy_system.get_action_slots_count()}")
    
    # 验证上限
    assert cafe.energy_system.generation_level <= cafe.energy_system.max_generation_level
    print("✅ 发电等级上限验证通过")
    
    # 测试序列化和反序列化
    print("\n--- 测试序列化兼容性 ---")
    cafe_data = cafe.to_dict()
    print(f"序列化数据包含升级阈值: {'upgrade_thresholds' in cafe_data}")
    print(f"序列化的升级阈值: {cafe_data.get('upgrade_thresholds', '未找到')}")
    
    print("\n🎉 游戏集成测试通过！")

if __name__ == "__main__":
    try:
        test_game_integration()
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()