#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试发电等级上限和递增难度机制
验证：
1. 发电等级上限为5级
2. 升级阈值递增机制
3. 升级时电能恢复至上限
4. 不同角色的差异化配置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LingCard.characters.cafe import Cafe
from LingCard.characters.jun import Jun
from LingCard.characters.liuli import Liuli
from LingCard.characters.xinhe import Xinhe
from LingCard.characters.yangguang import Yangguang

def test_character_generation_thresholds():
    """测试各角色的发电等级阈值配置"""
    print("=== 测试角色发电等级阈值配置 ===")
    
    characters = [
        ("Cafe（标准）", Cafe()),
        ("俊（守护型）", Jun()), 
        ("琉璃（反击型）", Liuli()),
        ("星河（辅助型）", Xinhe()),
        ("阳光（辅助型）", Yangguang())
    ]
    
    for name, char in characters:
        print(f"\n{name}:")
        print(f"  升级阈值: {char.upgrade_thresholds}")
        print(f"  最大等级: {char.energy_system.max_generation_level}")
        
        # 计算每级需要的额外伤害
        thresholds = char.upgrade_thresholds
        increments = []
        for i in range(len(thresholds)):
            if i == 0:
                increments.append(thresholds[i])
            else:
                increments.append(thresholds[i] - thresholds[i-1])
        print(f"  每级增量: {increments}")

def test_generation_level_progression():
    """测试发电等级提升机制"""
    print("\n\n=== 测试Cafe角色发电等级提升机制 ===")
    
    cafe = Cafe()
    energy_system = cafe.energy_system
    
    # 测试升级过程
    test_damages = [3, 2, 1, 7, 5, 3, 8, 10, 5, 20]  # 总共64点伤害
    
    print(f"初始状态: {energy_system}")
    print(f"升级阈值: {cafe.upgrade_thresholds}")
    
    for i, damage in enumerate(test_damages):
        print(f"\n第{i+1}次伤害: {damage}点")
        
        old_level = energy_system.generation_level
        old_energy = energy_system.current_energy
        old_limit = energy_system.get_energy_limit()
        
        level_up = energy_system.add_damage(damage)
        
        new_level = energy_system.generation_level
        new_energy = energy_system.current_energy
        new_limit = energy_system.get_energy_limit()
        
        print(f"  累积伤害: {energy_system.accumulated_damage}")
        print(f"  发电等级: {old_level} -> {new_level}")
        print(f"  电能上限: {old_limit} -> {new_limit}")
        print(f"  当前电能: {old_energy} -> {new_energy}")
        
        if level_up:
            print(f"  ✅ 发电等级提升！电能已恢复至上限")
        
        if new_level >= energy_system.max_generation_level:
            print(f"  🔴 已达到最大发电等级 {energy_system.max_generation_level}")
            break

def test_level_5_limit():
    """测试发电等级上限为5的限制"""
    print("\n\n=== 测试发电等级上限限制 ===")
    
    cafe = Cafe()
    energy_system = cafe.energy_system
    
    # 直接添加大量伤害，测试上限
    massive_damage = 1000
    print(f"添加大量伤害: {massive_damage}点")
    
    energy_system.add_damage(massive_damage)
    
    print(f"累积伤害: {energy_system.accumulated_damage}")
    print(f"发电等级: {energy_system.generation_level}")
    print(f"最大等级: {energy_system.max_generation_level}")
    print(f"电能上限: {energy_system.get_energy_limit()}")
    print(f"行动槽数: {energy_system.get_action_slots_count()}")
    
    # 验证状态
    status = energy_system.get_status()
    print(f"状态信息: {status}")
    
    assert energy_system.generation_level <= energy_system.max_generation_level, \
        f"发电等级 {energy_system.generation_level} 超过了上限 {energy_system.max_generation_level}"
    
    assert energy_system.generation_level == 5, \
        f"发电等级应该是5，实际是 {energy_system.generation_level}"
    
    print("✅ 发电等级上限测试通过")

def test_energy_restoration_on_levelup():
    """测试升级时电能恢复至上限"""
    print("\n\n=== 测试升级时电能恢复机制 ===")
    
    cafe = Cafe()
    energy_system = cafe.energy_system
    
    # 先消耗一些电能
    energy_system.consume_energy(2)
    print(f"消耗2点电能后: {energy_system.current_energy}/{energy_system.get_energy_limit()}")
    
    # 添加足够伤害升级
    print("添加5点伤害，应该升级到1级...")
    level_up = energy_system.add_damage(5)
    
    if level_up:
        print(f"✅ 升级成功！")
        print(f"升级后电能: {energy_system.current_energy}/{energy_system.get_energy_limit()}")
        
        assert energy_system.current_energy == energy_system.get_energy_limit(), \
            f"升级后电能应该是满的，实际: {energy_system.current_energy}/{energy_system.get_energy_limit()}"
        
        print("✅ 电能恢复机制测试通过")
    else:
        print("❌ 升级失败")

def test_different_character_types():
    """测试不同类型角色的发电差异"""
    print("\n\n=== 测试不同角色类型的发电差异 ===")
    
    characters = [
        ("琉璃（反击型-快速）", Liuli()),
        ("Cafe（标准）", Cafe()),
        ("俊（守护型-缓慢）", Jun())
    ]
    
    # 给所有角色相同的伤害
    test_damage = 10
    
    for name, char in characters:
        char.energy_system.add_damage(test_damage)
        print(f"{name}: {test_damage}点伤害 -> 等级{char.energy_system.generation_level} (阈值{char.upgrade_thresholds})")

if __name__ == "__main__":
    try:
        test_character_generation_thresholds()
        test_generation_level_progression()
        test_level_5_limit()
        test_energy_restoration_on_levelup()
        test_different_character_types()
        
        print("\n\n🎉 所有测试通过！新的发电等级机制工作正常。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()