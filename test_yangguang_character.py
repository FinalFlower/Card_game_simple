"""
测试脚本：验证阳光角色及其专属卡牌"皓日当空"的所有功能
"""

import sys
import os

# 添加项目根目录到Python路径，以便导入游戏模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LingCard.characters.yangguang import Yangguang
from LingCard.cards.yangguang_special import YangguangSpecialCard
from LingCard.core.game_state import GameState
from LingCard.core.player import Player
from LingCard.core.game_engine import GameEngine

def create_test_game():
    """创建一个用于测试的游戏环境"""
    game_state = GameState()
    
    # 创建两个玩家
    player1 = Player("玩家1")
    player2 = Player("玩家2")
    
    # 为玩家1创建阳光角色
    yangguang = Yangguang()
    player1.characters = [yangguang]
    player1.active_character_index = 0
    
    # 为玩家2创建一个普通角色（使用基类Character作为占位符）
    from LingCard.characters.character import Character
    dummy_char = Character("测试角色", "用于测试的角色", max_hp=100)
    player2.characters = [dummy_char]
    player2.active_character_index = 0
    
    # 将玩家添加到游戏状态
    game_state.players = [player1, player2]
    game_state.current_player_index = 0
    
    return game_state, player1, player2, yangguang, dummy_char

def test_initial_state():
    """测试阳光角色的初始状态"""
    print("=== 测试1: 初始状态 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 检查初始血量上限
    assert yangguang.max_hp == 70, f"初始血量上限应为70，实际为{yangguang.max_hp}"
    print("✓ 初始血量上限正确")
    
    # 检查初始发电等级
    assert yangguang.energy_system.generation_level == 0, f"初始发电等级应为0，实际为{yangguang.energy_system.generation_level}"
    print("✓ 初始发电等级正确")
    
    print("初始状态测试通过！")

def test_health_increase_on_generation():
    """测试发电等级提升时血量上限增加"""
    print("\n=== 测试2: 发电等级提升对血量上限的影响 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 模拟发电等级提升
    yangguang.energy_system.generation_level = 1
    yangguang.on_turn_start(game_state, player1)
    assert yangguang.max_hp == 90, f"发电等级1时血量上限应为90，实际为{yangguang.max_hp}"
    print("✓ 发电等级1: 血量上限正确")
    
    yangguang.energy_system.generation_level = 2
    yangguang.on_turn_start(game_state, player1)
    assert yangguang.max_hp == 110, f"发电等级2时血量上限应为110，实际为{yangguang.max_hp}"
    print("✓ 发电等级2: 血量上限正确")
    
    yangguang.energy_system.generation_level = 3
    yangguang.on_turn_start(game_state, player1)
    assert yangguang.max_hp == 130, f"发电等级3时血量上限应为130，实际为{yangguang.max_hp}"
    print("✓ 发电等级3: 血量上限正确")
    
    # 检查当前血量没有增加
    assert yangguang.current_hp == 70, f"血量上限增加时，当前血量不应改变，实际为{yangguang.current_hp}"
    print("✓ 当前血量未随血量上限增加")
    
    print("发电等级提升测试通过！")

def test_counter_damage():
    """测试反击伤害效果"""
    print("\n=== 测试3: 反击伤害效果 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 提升发电等级以增加血量上限
    yangguang.energy_system.generation_level = 2
    yangguang.on_turn_start(game_state, player1)
    
    initial_logs_count = len(game_state.log)
    initial_dummy_hp = dummy_char.current_hp
    
    # 对阳光造成超过30%最大血量的伤害（110 * 0.3 = 33，所以造成40点伤害）
    # 使用带攻击者信息的方法以触发反击
    damage_dealt = yangguang.take_damage_with_attacker(40, game_state, attacker=dummy_char)
    assert damage_dealt == 40, f"应受到40点伤害，实际受到{damage_dealt}"
    print("✓ 成功造成超过30%血量的伤害")
    
    # 检查是否触发了反击伤害
    counter_damage = int(110 * 0.4)  # 最大血量上限的40%
    expected_dummy_hp = max(0, initial_dummy_hp - counter_damage)  # 血量不能低于0
    
    # 检查攻击者是否受到了反击伤害
    assert dummy_char.current_hp == expected_dummy_hp, f"攻击者应受到{counter_damage}点反击伤害，血量应从{initial_dummy_hp}变为{expected_dummy_hp}，实际为{dummy_char.current_hp}"
    print(f"✓ 攻击者受到了{counter_damage}点反击伤害")
    
    # 反击伤害应该记录在日志中
    counter_damage_log = None
    for log in game_state.log[initial_logs_count:]:
        if "反击" in log and str(counter_damage) in log and "点伤害" in log:
            counter_damage_log = log
            break

    assert counter_damage_log is not None, f"未找到反击伤害日志，期望对攻击者造成{counter_damage}点伤害"
    print(f"✓ 反击伤害效果触发: {counter_damage_log}")
    
    print("反击伤害测试通过！")

def test_revive_on_defeat():
    """测试被击败时的复活效果"""
    print("\n=== 测试4: 被击败时的复活效果 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 提升发电等级
    yangguang.energy_system.generation_level = 2
    yangguang.energy_system.current_generation = 50  # 设置当前发电值
    yangguang.on_turn_start(game_state, player1)
    
    initial_health = yangguang.current_hp
    initial_max_health = yangguang.max_hp  # 110
    
    # 造成致命伤害
    damage_dealt = yangguang.take_damage(200, game_state)
    assert damage_dealt < 200, "角色应该在受到致命伤害前被复活"
    print("✓ 角色在受到致命伤害前被复活")
    
    # 检查是否恢复了生命值
    expected_heal = int(50 * 0.05)  # 5% of current_generation
    assert yangguang.current_hp == expected_heal, f"复活后生命值应为{expected_heal}，实际为{yangguang.current_hp}"
    print(f"✓ 复活后恢复了{expected_heal}点生命值")
    
    # 检查发电值是否被扣除
    assert yangguang.energy_system.current_generation == 0, f"复活后发电值应被清空，实际为{yangguang.energy_system.current_generation}"
    print("✓ 复活后发电值被清空")
    
    # 检查被动技能是否失效
    assert yangguang.has_used_revive == True, "复活被动技能应该失效"
    print("✓ 复活被动技能失效")
    
    print("复活效果测试通过！")

def test_final_death_effect():
    """测试真正被击败后的最终伤害效果"""
    print("\n=== 测试5: 真正被击败后的最终伤害效果 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 先触发一次复活
    yangguang.energy_system.generation_level = 1
    yangguang.energy_system.current_generation = 30
    yangguang.on_turn_start(game_state, player1)
    yangguang.take_damage(100, game_state)  # 触发复活
    
    initial_logs_count = len(game_state.log)
    
    # 再次造成致命伤害，触发最终伤害
    yangguang.take_damage(200, game_state)
    
    # 检查是否对场上任意目标造成了最大生命值20%的伤害
    final_damage_triggered = False
    final_damage_log = None
    for log in game_state.log[initial_logs_count:]:
        if "被真正击败" in log and "点伤害" in log:
            final_damage_triggered = True
            final_damage_log = log
            break

    assert final_damage_triggered, f"未找到真正被击败后的最终伤害日志。日志内容：{game_state.log[initial_logs_count:]}"
    print(f"✓ 真正被击败后的最终伤害效果触发: {final_damage_log}")
    
    print("最终伤害效果测试通过！")

def test_special_card_acquisition():
    """测试专属卡牌获取"""
    print("\n=== 测试6: 专属卡牌获取 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 检查初始手牌为空
    assert len(player1.hand) == 0, f"初始手牌应为空，实际有{len(player1.hand)}张"
    print("✓ 初始手牌为空")
    
    # 提升发电等级到3
    yangguang.energy_system.generation_level = 3
    yangguang.on_turn_start(game_state, player1)
    
    # 检查是否获得了专属卡
    assert len(player1.hand) == 1, f"发电等级3时应获得1张专属卡，实际有{len(player1.hand)}张"
    assert isinstance(player1.hand[0], YangguangSpecialCard), "手牌中的卡牌不是YangguangSpecialCard类型"
    print("✓ 成功获得专属卡牌")
    
    # 再次触发on_turn_start，检查是否重复获得卡牌
    yangguang.on_turn_start(game_state, player1)
    assert len(player1.hand) == 1, "不应重复获得专属卡牌"
    print("✓ 没有重复获得专属卡牌")
    
    print("专属卡牌获取测试通过！")

def test_special_card_effect():
    """测试专属卡牌效果"""
    print("\n=== 测试7: 专属卡牌效果 ===")
    game_state, player1, player2, yangguang, dummy_char = create_test_game()
    
    # 获取使用者角色
    user_char = player1.get_alive_characters()[0]
    
    # 提升发电等级到3并获得专属卡
    yangguang.energy_system.generation_level = 3
    yangguang.on_turn_start(game_state, player1)
    
    # 获取专属卡
    special_card = player1.hand[0]
    
    # 检查基础能量消耗
    assert special_card.energy_cost == 5, f"基础能量消耗应为5，实际为{special_card.energy_cost}"
    print("✓ 基础能量消耗正确")
    
    # 检查额外费用
    assert special_card.get_extra_cost() == 3, f"额外费用应为3，实际为{special_card.get_extra_cost()}"
    print("✓ 额外费用正确")
    
    # 测试基础效果：对除自身外所有目标造成伤害
    initial_health = dummy_char.current_hp
    special_card.play(player1, game_state)
    
    damage_taken = initial_health - dummy_char.current_hp
    assert damage_taken == 30, f"应造成30点伤害，实际造成{damage_taken}点伤害"
    print("✓ 基础伤害效果正确")
    
    # 测试额外费用效果：保护队友
    player1.hand.append(special_card)  # 重新将卡牌加入手牌
    user_char.energy_system.current_energy = 10  # 确保有足够的能量
    
    initial_logs_count = len(game_state.log)
    special_card.play(player1, game_state, extra_cost=3)
    
    # 检查是否消耗了额外能量
    assert user_char.energy_system.current_energy == 2, f"应消耗8点总能量（5+3），实际剩余{user_char.energy_system.current_energy}"
    print("✓ 额外能量消耗正确")
    
    # 检查是否设置了保护状态
    assert player1.status.get('protected_team', False) == True, "队友保护状态未设置"
    print("✓ 队友保护状态正确设置")
    
    print("专属卡牌效果测试通过！")

def run_all_tests():
    """运行所有测试"""
    tests = [
        test_initial_state,
        test_health_increase_on_generation,
        test_counter_damage,
        test_revive_on_defeat,
        test_final_death_effect,
        test_special_card_acquisition,
        test_special_card_effect
    ]
    
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            return
        except Exception as e:
            print(f"✗ {test.__name__} 异常: {e}")
            return
    
    print("\n🎉 所有测试通过！阳光角色及其专属卡牌的所有功能均正常工作。")

if __name__ == "__main__":
    run_all_tests()
