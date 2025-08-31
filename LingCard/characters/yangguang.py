from .character import Character
from typing import Tuple, Optional
from LingCard.core.game_state import GameState
from LingCard.core.player import Player
from LingCard.cards.yangguang_special import YangguangSpecialCard
import random

class Yangguang(Character):
    """阳光：具有独特的血量和被动技能的角色"""
    
    def __init__(self):
        # 阳光的发电阈值（均衡）：5 -> 8 -> 11 -> 14 -> 17
        upgrade_thresholds = [5, 13, 24, 38, 55]
        
        super().__init__(
            name="阳光",
            description="自身发电等级每提升一级，最大血量上限增加20；单次受到伤害超过自身最大血量上限30%时反击；被击败时可复活；真正击败后造成范围伤害",
            max_hp=70,
            base_energy_limit=3,
            upgrade_thresholds=upgrade_thresholds
        )
        self.max_hp_base = 70  # 基础血量上限
        self.has_used_revive = False  # 是否已经使用过复活被动
        # 确保初始血量为70
        self.current_hp = 70
        # 确保最大血量为70
        self.max_hp = 70
    
    def on_turn_start(self, game_state, player, engine=None):
        """回合开始时，根据发电等级提升最大血量"""
        if not self.is_alive:
            return
            
        # 根据发电等级提升最大血量上限
        level = self.energy_system.generation_level
        self.max_hp = self.max_hp_base + level * 20
        # 注意：当前血量不随此增加
        
        # 更新血量显示（如果当前血量超过新上限，则调整）
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
            
        # 检查是否达到发电等级3级，获得专属卡
        if level >= 3 and not hasattr(self, '_special_card_given'):
            # 创建专属卡实例
            special_card = YangguangSpecialCard()
            # 将卡牌加入玩家手牌
            player.hand.append(special_card)
            # 标记已给予专属卡，避免重复给予
            self._special_card_given = True
            # 添加日志
            game_state.add_log(f"角色技能[{self.name}]触发：发电等级达到3级，获得专属卡牌【皓日当空】！")
    
    def on_take_damage(self, damage: int, attacker, game_state) -> Tuple[int, int]:
        """受到伤害时的被动效果"""
        if not self.is_alive:
            return (0, 0)
            
        # 计算实际伤害
        actual_damage = max(0, damage - self.defense_buff)
        
        # 检查是否超过最大血量30%
        if actual_damage > self.max_hp * 0.3 and attacker:
            # 反击造成最大血量40%的伤害
            counter_damage = int(self.max_hp * 0.4)
            game_state.add_log(f"角色技能[{self.name}]触发：受到致命伤害，反击造成{counter_damage}点伤害！")
            # 对攻击者造成反击伤害
            if hasattr(attacker, 'take_damage'):
                # 确保attacker是Character实例
                if isinstance(attacker, Character):
                    # 基类Character的take_damage方法只接受damage参数
                    attacker.take_damage(counter_damage)
            return (actual_damage, counter_damage)
            
        return (actual_damage, 0)
    
    def take_damage(self, damage: int, game_state=None) -> int:
        """重写受伤逻辑以处理复活被动"""
        if not self.is_alive:
            return 0
            
        # 先应用防御
        actual_damage = max(0, damage - self.defense_buff)
        
        # 检查是否会被击败
        if self.current_hp <= actual_damage and not self.has_used_revive:
            # 触发复活被动
            # 扣除当前所有电能(cost)
            energy_to_spend = self.energy_system.current_energy
            if energy_to_spend > 0:
                heal_amount = int(self.max_hp * energy_to_spend * 0.05)
                # 确保至少恢复1点生命值以存活
                if heal_amount <= 0 and energy_to_spend > 0:
                    heal_amount = 1
                
                self.current_hp = heal_amount
                self.is_alive = True
                self.has_used_revive = True
                self.energy_system.current_energy = 0  # 扣除所有电能
                
                # 清除防御
                self.defense_buff = 0
                
                if game_state:
                    game_state.add_log(f"角色技能[{self.name}]触发：被击败时消耗所有发电值，恢复{heal_amount}点生命！")
                return 0  # 伤害被完全抵消
            
        # 正常处理伤害
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        if self.current_hp <= 0:
            self.is_alive = False
            # 触发真正击败后的效果
            if self.has_used_revive:
                # 已经复活过，真正被击败
                self._on_truly_defeated(game_state)
            else:
                # 如果因为没有能量而未能复活，也需要标记为已使用
                self.has_used_revive = True
                
        if self.defense_buff > 0:
            reduced_damage = min(damage, self.defense_buff)
            self.defense_buff = max(0, self.defense_buff - damage)
            
        return actual_damage
    
    def take_damage_with_attacker(self, damage: int, game_state=None, attacker=None) -> int:
        """带攻击者信息的受伤逻辑，用于触发反击效果"""
        if not self.is_alive:
            return 0
            
        # 先触发反击效果
        actual_damage, counter_damage = self.on_take_damage(damage, attacker, game_state)
        
        # 然后调用统一的受伤处理逻辑
        return self.take_damage(actual_damage, game_state)
    
    def _on_truly_defeated(self, game_state):
        """真正被击败后的效果"""
        if not game_state:
            return
            
        # 随机对场上任意目标造成其最大生命值20%的伤害
        players = game_state.players
        if not players:
            return
            
        # 收集所有存活的角色
        all_alive_characters = []
        for player in players:
            all_alive_characters.extend(player.get_alive_characters())
        
        if all_alive_characters:
            target_character = random.choice(all_alive_characters)
            damage = int(target_character.max_hp * 0.2)
            target_character.take_damage(damage)
            game_state.add_log(f"角色技能[{self.name}]触发：被真正击败，对{target_character.name}造成{damage}点伤害！")
