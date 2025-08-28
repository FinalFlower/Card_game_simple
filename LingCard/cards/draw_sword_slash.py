# LingCard/cards/draw_sword_slash.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.core.buff_system import BuffType

class DrawSwordSlashCard(ActionCard):
    """
    拔刀斩卡牌 (3cost)
    
    特殊机制：
    - 本行动牌无法被护盾抵抗
    - 剑意大于等于5时可以使用
    - 目标血量不足15%时，直接击败目标，同时减少自身2层剑意
    - 否则对敌方造成10点伤害，并且清除自身所有剑意层数
    """
    
    def __init__(self):
        super().__init__(
            name="拔刀斩",
            description="剑意≥5时可用，无法被护盾抵抗。目标血量<15%时直接击败并减少2层剑意，否则造成10点伤害并清空剑意（消耗3点电能）",
            action_type=ActionType.SWORD_SPECIAL,
            energy_cost=3
        )
        self.piercing = True  # 标记为穿透伤害，无法被护盾抵抗
    
    def get_base_value(self) -> int:
        """获取基础伤害值"""
        return 10
    
    def get_required_sword_intent(self) -> int:
        """获取所需剑意层数"""
        return 5
    
    def get_execute_threshold(self) -> float:
        """获取即死阈值（百分比）"""
        return 0.15  # 15%
    
    def can_use(self, character) -> bool:
        """
        检查是否可以使用该卡牌
        需要检查电能消耗和剑意层数
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        # 检查剑意层数（优先检查，因为这是拔刀斩的特殊条件）
        sword_intent_buff = character.buff_manager.get_buff_by_type(BuffType.SWORD_INTENT)
        required_sword_intent = self.get_required_sword_intent()
        
        if not sword_intent_buff or sword_intent_buff.stacks < required_sword_intent:
            # 剑意不足，不能使用
            return False
        
        # 检查基础的电能消耗
        if not super().can_use(character):
            # 电能不足，不能使用
            return False
        
        return True
    
    def execute_effect(self, user, target, game_state):
        """
        执行拔刀斩的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 检查目标血量是否低于执行阈值
        execute_threshold = self.get_execute_threshold()
        target_hp_percentage = target.current_hp / target.max_hp
        
        if target_hp_percentage < execute_threshold:
            # 执行即死效果
            execution_result = self._execute_target(user, target, game_state)
            results.append(execution_result)
            
            # 减少2层剑意
            sword_intent_reduction = self._reduce_sword_intent(user, 2, game_state)
            results.append(sword_intent_reduction)
        else:
            # 造成普通伤害
            damage_result = self._deal_piercing_damage(user, target, game_state)
            results.append(damage_result)
            
            # 清除所有剑意
            sword_intent_clear = self._clear_all_sword_intent(user, game_state)
            results.append(sword_intent_clear)
        
        return {
            'card_name': self.name,
            'effects': results,
            'was_execution': target_hp_percentage < execute_threshold,
            'target_hp_percentage': target_hp_percentage
        }
    
    def _execute_target(self, user, target, game_state):
        """
        执行即死效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        # 直接将目标血量设为0
        original_hp = target.current_hp
        target.current_hp = 0
        target.is_alive = False  # 确保更新存活状态
        
        # 记录日志
        if game_state:
            game_state.add_log(f'{user.name} 使用拔刀斩直接击败了 {target.name}！')
        
        return {
            'type': 'execution',
            'target': target.name,
            'original_hp': original_hp,
            'message': f'{user.name} 使用拔刀斩直接击败了 {target.name}！'
        }
    
    def _deal_piercing_damage(self, user, target, game_state):
        """
        造成穿透伤害（无法被护盾抵抗）
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 伤害结果
        """
        damage = self.get_base_value()
        
        # 穿透伤害，直接减少血量，不被护盾阻挡
        actual_damage = min(damage, target.current_hp)
        target.current_hp -= actual_damage
        
        # 检查目标是否死亡
        if target.current_hp <= 0:
            target.is_alive = False
        
        # 记录日志
        if game_state:
            game_state.add_log(f'{user.name} 使用拔刀斩对 {target.name} 造成了 {actual_damage} 点穿透伤害')
        
        return {
            'type': 'piercing_damage',
            'target': target.name,
            'damage': actual_damage,
            'message': f'{user.name} 对 {target.name} 造成了 {actual_damage} 点穿透伤害（无法被护盾抵抗）'
        }
    
    def _reduce_sword_intent(self, user, amount, game_state):
        """
        减少剑意层数
        
        Args:
            user: 使用卡牌的角色
            amount: 要减少的层数
            game_state: 游戏状态
            
        Returns:
            dict: 剑意减少结果
        """
        sword_intent_buff = user.buff_manager.get_buff_by_type(BuffType.SWORD_INTENT)
        
        if sword_intent_buff:
            old_stacks = sword_intent_buff.stacks
            sword_intent_buff.consume_stacks(amount)
            new_stacks = sword_intent_buff.stacks
            
            if game_state:
                game_state.add_log(f'{user.name} 的剑意减少了 {amount} 层，当前剑意: {new_stacks} 层')
            
            return {
                'type': 'sword_intent_reduced',
                'target': user.name,
                'amount': amount,
                'old_stacks': old_stacks,
                'new_stacks': new_stacks,
                'message': f'{user.name} 的剑意减少了 {amount} 层'
            }
        else:
            return {
                'type': 'no_sword_intent',
                'message': f'{user.name} 没有剑意可以减少'
            }
    
    def _clear_all_sword_intent(self, user, game_state):
        """
        清除所有剑意层数
        
        Args:
            user: 使用卡牌的角色
            game_state: 游戏状态
            
        Returns:
            dict: 剑意清除结果
        """
        sword_intent_buff = user.buff_manager.get_buff_by_type(BuffType.SWORD_INTENT)
        
        if sword_intent_buff:
            old_stacks = sword_intent_buff.stacks
            sword_intent_buff.stacks = 0
            
            if game_state:
                game_state.add_log(f'{user.name} 失去了所有剑意（{old_stacks}层）')
            
            return {
                'type': 'sword_intent_cleared',
                'target': user.name,
                'cleared_stacks': old_stacks,
                'message': f'{user.name} 失去了所有剑意（{old_stacks}层）'
            }
        else:
            return {
                'type': 'no_sword_intent',
                'message': f'{user.name} 没有剑意需要清除'
            }