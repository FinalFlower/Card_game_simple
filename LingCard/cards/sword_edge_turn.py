# LingCard/cards/sword_edge_turn.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.buffs.sword_intent import SwordIntentBuff
from LingCard.core.buff_system import BuffType

class SwordEdgeTurnCard(ActionCard):
    """
    剑锋直转卡牌 (2cost)
    
    效果：
    - 为自身施加2层剑意
    - 为自身施加8点护盾
    """
    
    def __init__(self):
        super().__init__(
            name="剑锋直转",
            description="为自身施加2层剑意，获得8点护盾（消耗2点电能）",
            action_type=ActionType.SWORD_SUPPORT,
            energy_cost=2
        )
    
    def get_base_value(self) -> int:
        """获取剑意层数"""
        return 2
    
    def get_shield_value(self) -> int:
        """获取护盾值"""
        return 8
    
    def execute_effect(self, user, target, game_state):
        """
        执行剑锋直转的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色（对于自我增益卡，target通常等于user）
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 施加剑意
        sword_intent_stacks = self.get_base_value()
        sword_intent_buff = SwordIntentBuff(stacks=sword_intent_stacks)
        user.buff_manager.add_buff(sword_intent_buff, game_state)
        results.append({
            'type': 'buff_applied',
            'target': user.name,
            'buff': 'sword_intent',
            'stacks': sword_intent_stacks,
            'message': f'{user.name} 获得了 {sword_intent_stacks} 层剑意'
        })
        
        # 2. 施加护盾
        shield_amount = self.get_shield_value()
        shield_result = self._apply_shield(user, shield_amount, game_state)
        results.append(shield_result)
        
        return {
            'card_name': self.name,
            'effects': results,
            'sword_intent_gained': sword_intent_stacks,
            'shield_applied': shield_amount
        }
    
    def _apply_shield(self, user, shield_amount, game_state):
        """
        为用户施加护盾效果
        
        Args:
            user: 使用卡牌的角色
            shield_amount: 护盾点数
            game_state: 游戏状态
            
        Returns:
            dict: 护盾施加结果
        """
        # 检查是否已有护盾buff
        existing_shield = user.buff_manager.get_buff_by_type(BuffType.SHIELD)
        
        if existing_shield:
            # 如果已有护盾，增加层数
            existing_shield.add_stacks(shield_amount)
            current_shield = existing_shield.stacks
            message = f'{user.name} 的护盾增加了 {shield_amount} 点，当前护盾: {current_shield} 点'
        else:
            # 如果没有护盾，创建新的护盾buff
            from LingCard.buffs.shield import ShieldBuff  # 假设有护盾buff类
            shield_buff = ShieldBuff(stacks=shield_amount)
            user.buff_manager.add_buff(shield_buff, game_state)
            message = f'{user.name} 获得了 {shield_amount} 点护盾'
        
        return {
            'type': 'shield_applied',
            'target': user.name,
            'amount': shield_amount,
            'message': message
        }
    
    def can_use(self, character) -> bool:
        """
        检查是否可以使用该卡牌
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        return super().can_use(character)