#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配卡系统测试脚本
用于验证配卡功能和抽卡测试卡牌的正确性
"""

import yaml
from LingCard.utils.loader import load_characters, load_cards
from LingCard.core.player import Player
from LingCard.core.game_engine import GameEngine
from LingCard.core.game_state import GameState

def test_deck_builder():
    """测试配卡系统"""
    print("=== 配卡系统测试 ===")
    
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 加载卡牌类
    all_cards = load_cards()
    print(f"已加载卡牌类: {list(all_cards.keys())}")
    
    # 创建测试玩家
    player = Player(1)
    
    # 测试1: 设置自定义配卡
    print("\n--- 测试1: 设置自定义配卡 ---")
    custom_config = {
        'AttackCard': 3,
        'HealCard': 2,
        'DefendCard': 3,
        'PoisonCard': 1,
        'DrawTestCard': 1  # 新的抽卡测试卡
    }
    
    try:
        player.set_custom_deck_config(custom_config)
        print(f"✅ 成功设置自定义配卡: {player.get_deck_config()}")
    except Exception as e:
        print(f"❌ 设置自定义配卡失败: {e}")
    
    # 测试2: 验证牌库初始化
    print("\n--- 测试2: 验证牌库初始化 ---")
    engine = GameEngine(config)
    try:
        engine.initialize_player_deck(player, all_cards)
        print(f"✅ 牌库初始化成功，牌库大小: {len(player.deck)}")
        
        # 统计牌库中的卡牌类型
        deck_composition = {}
        for card in player.deck:
            card_type = card.__class__.__name__
            deck_composition[card_type] = deck_composition.get(card_type, 0) + 1
        print(f"   牌库组成: {deck_composition}")
    except Exception as e:
        print(f"❌ 牌库初始化失败: {e}")
    
    # 测试3: 验证抽卡测试卡
    print("\n--- 测试3: 验证抽卡测试卡 ---")
    draw_test_cards = [card for card in player.deck if card.__class__.__name__ == 'DrawTestCard']
    if draw_test_cards:
        card = draw_test_cards[0]
        print(f"✅ 找到抽卡测试卡: {card.name}")
        print(f"   电能消耗: {card.energy_cost}")
        print(f"   描述: {card.description}")
        print(f"   基础值: {card.get_base_value()}")
    else:
        print("❌ 未找到抽卡测试卡")

def test_draw_mechanics():
    """测试抽卡机制"""
    print("\n=== 抽卡机制测试 ===")
    
    # 加载配置和卡牌
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    all_cards = load_cards()
    
    # 创建测试环境
    game_state = GameState("test_game.yaml")
    player = Player(1)
    engine = GameEngine(config)
    
    # 设置自定义配卡（少量卡牌便于测试）
    test_config = {
        'AttackCard': 5,
        'DrawTestCard': 3,
        'HealCard': 2
    }
    player.set_custom_deck_config(test_config)
    engine.initialize_player_deck(player, all_cards)
    
    print(f"初始牌库大小: {len(player.deck)}")
    print(f"初始手牌大小: {len(player.hand)}")
    print(f"初始弃牌堆大小: {len(player.discard_pile)}")
    
    # 测试抽卡
    print("\n--- 测试基础抽卡 ---")
    drawn = engine.draw_cards(player, 2)
    print(f"抽取了 {drawn} 张卡")
    print(f"手牌大小: {len(player.hand)}")
    print(f"牌库大小: {len(player.deck)}")
    
    # 模拟使用卡牌进入弃牌堆
    print("\n--- 测试弃牌堆循环 ---")
    if player.hand:
        card = player.hand.pop()
        player.discard_pile.append(card)
        print(f"使用了一张卡，弃牌堆大小: {len(player.discard_pile)}")
    
    # 测试弃牌堆循环
    if len(player.deck) == 0:
        print("牌库已空，测试弃牌堆循环...")
        drawn = engine.draw_cards(player, 1)
        print(f"从弃牌堆抽取了 {drawn} 张卡")
        print(f"牌库大小: {len(player.deck)}")
        print(f"弃牌堆大小: {len(player.discard_pile)}")

def test_new_deck_builder_interface():
    """测试新的配卡界面功能"""
    print("\n=== 新配卡界面测试 ===")
    
    # 创建测试玩家
    player = Player(1)
    
    # 测试1: 初始化空牌库
    print("\n--- 测试1: 初始化空牌库 ---")
    print(f"初始牌库状态: {player.get_deck_config()}")
    print(f"是否使用自定义配置: {player.has_custom_deck}")
    
    # 测试2: 添加卡牌（无需二次确认）
    print("\n--- 测试2: 添加卡牌（无需二次确认） ---")
    cards_to_add = [
        ('AttackCard', 3),
        ('HealCard', 2),
        ('DefendCard', 3),
        ('PoisonCard', 1),
        ('DrawTestCard', 1)
    ]
    
    for card_name, count in cards_to_add:
        for _ in range(count):
            success = player.add_card_to_deck_config(card_name, 1)
            if success:
                current_count = player.get_deck_config().get(card_name, 0)
                print(f"✅ 添加 {card_name}: 当前 {current_count} 张")
            else:
                print(f"❌ 添加 {card_name} 失败")
    
    total_cards = sum(player.get_deck_config().values())
    print(f"牌库状态: {total_cards}/10 张")
    
    # 测试3: 移除卡牌
    print("\n--- 测试3: 移除卡牌 ---")
    print("移除前:", player.get_deck_config())
    
    # 移除一张攻击卡
    if player.remove_card_from_deck_config('AttackCard', 1):
        print(f"✅ 移除了一张攻击卡")
    else:
        print(f"❌ 移除攻击卡失败")
    
    print("移除后:", player.get_deck_config())
    
    # 测试4: 清空牌库（需要二次确认）
    print("\n--- 测试4: 清空牌库（需要二次确认） ---")
    print("清空前:", player.get_deck_config())
    
    player.clear_deck_config()
    print("清空后:", player.get_deck_config())
    print(f"是否使用自定义配置: {player.has_custom_deck}")
    
    # 测试5: 空间限制
    print("\n--- 测试5: 空间限制 ---")
    # 添加11张卡测试超出限制
    for i in range(11):
        success = player.add_card_to_deck_config('AttackCard', 1)
        if success:
            total = sum(player.get_deck_config().values())
            print(f"添加第{i+1}张卡成功，当前总数: {total}")
        else:
            total = sum(player.get_deck_config().values())
            print(f"添加第{i+1}张卡失败，当前总数: {total}（达到上限）")
            break

if __name__ == "__main__":
    try:
        test_deck_builder()
        test_draw_mechanics()
        test_new_deck_builder_interface()
        print("\n🎉 所有测试完成！")
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()