import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LingCard.characters.yangguang import Yangguang
from LingCard.core.game_state import GameState
from LingCard.core.player import Player

def create_test_environment():
    """创建一个简单的测试环境"""
    game_state = GameState()
    player = Player("TestPlayer")
    yangguang = Yangguang()
    player.characters = [yangguang]
    game_state.players = [player]
    return game_state, player, yangguang

def test_revive_with_energy():
    """测试有足够电能时复活成功"""
    print("=== 测试1: 有电能时复活 ===")
    game_state, player, yangguang = create_test_environment()

    # 设置初始状态
    yangguang.energy_system.current_energy = 40
    yangguang.current_hp = 10
    print(f"初始状态: HP={yangguang.current_hp}, Energy={yangguang.energy_system.current_energy}")

    # 造成致命伤害
    damage_taken = yangguang.take_damage(100, game_state)
    print(f"受到100点伤害，实际承受伤害: {damage_taken}")

    # 验证复活
    assert yangguang.is_alive, "角色应该存活"
    print("✓ 角色存活")

    expected_heal = int(yangguang.max_hp * 40 * 0.05)
    assert yangguang.current_hp == expected_heal, f"复活后HP应为 {expected_heal}, 实际为 {yangguang.current_hp}"
    print(f"✓ 复活后HP正确: {yangguang.current_hp}")

    assert yangguang.energy_system.current_energy == 0, "复活后电能应为0"
    print("✓ 电能已清空")

    assert yangguang.has_used_revive, "复活标记应为True"
    print("✓ 复活标记已设置")
    print("测试1通过！\n")

def test_revive_with_low_energy():
    """测试电能较低时，至少恢复1点HP"""
    print("=== 测试2: 低电能时复活 (至少恢复1HP) ===")
    game_state, player, yangguang = create_test_environment()

    # 设置初始状态
    yangguang.energy_system.current_energy = 10
    yangguang.current_hp = 5
    print(f"初始状态: HP={yangguang.current_hp}, Energy={yangguang.energy_system.current_energy}")

    # 造成致命伤害
    yangguang.take_damage(50, game_state)

    # 验证复活
    assert yangguang.is_alive, "角色应该存活"
    print("✓ 角色存活")

    # max_hp(70) * energy(10) * 0.05 = 35
    expected_heal = int(yangguang.max_hp * 10 * 0.05)
    assert yangguang.current_hp == expected_heal, f"低电能复活后HP应为 {expected_heal}, 实际为 {yangguang.current_hp}"
    print(f"✓ 复活后HP正确: {yangguang.current_hp}")
    print("测试2通过！\n")

def test_no_revive_without_energy():
    """测试没有电能时无法复活"""
    print("=== 测试3: 没有电能时无法复活 ===")
    game_state, player, yangguang = create_test_environment()

    # 设置初始状态
    yangguang.energy_system.current_energy = 0
    yangguang.current_hp = 20
    print(f"初始状态: HP={yangguang.current_hp}, Energy={yangguang.energy_system.current_energy}")

    # 造成致命伤害
    yangguang.take_damage(100, game_state)

    # 验证死亡
    assert not yangguang.is_alive, "没有电能时角色应该死亡"
    print("✓ 角色已死亡")
    print("测试3通过！\n")

def test_revive_only_once():
    """测试复活只能触发一次"""
    print("=== 测试4: 复活只能触发一次 ===")
    game_state, player, yangguang = create_test_environment()

    # 第一次复活
    yangguang.energy_system.current_energy = 50
    yangguang.current_hp = 10
    yangguang.take_damage(100, game_state)
    print(f"第一次复活后: HP={yangguang.current_hp}, is_alive={yangguang.is_alive}")
    assert yangguang.is_alive, "第一次应成功复活"

    # 再次给予电能并将HP设置为一个较低的值，然后造成致命伤害
    yangguang.energy_system.current_energy = 50
    yangguang.current_hp = 10
    yangguang.take_damage(100, game_state)
    print(f"第二次受到致命伤害后: HP={yangguang.current_hp}, is_alive={yangguang.is_alive}")

    # 验证死亡
    assert not yangguang.is_alive, "第二次受到致命伤害时角色应该死亡"
    print("✓ 角色已死亡")
    print("测试4通过！\n")

if __name__ == "__main__":
    test_revive_with_energy()
    test_revive_with_low_energy()
    test_no_revive_without_energy()
    test_revive_only_once()
    print("所有复活功能测试完成。")
