# LingCard/cards/remove_scars.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.core.buff_system import BuffType

class RemoveScarsCard(ActionCard):
    """
    祛痕卡牌 (1cost)
    
    效果：
    - 为自身施加3点护盾
    - 恢复自身5点血量
    """
    
    def __init__(self):
        super().__init__(
            name="祛痕",
            description="为自身施加3点护盾，恢复5点血量（消耗1点电能）",
            action_type=ActionType.SWORD_SUPPORT,
            energy_cost=1
        )
    
    def get_base_value(self) -> int:
        """获取基础治疗值"""
        return 5
    
    def get_shield_value(self) -> int:
        """获取护盾值"""
        return 3
    
    def execute_effect(self, user, target, game_state):
        """
        执行祛痕的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色（对于自我治疗卡，target通常等于user）
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 恢复血量
        heal_amount = self.get_base_value()
        # 注意：heal方法不需要game_state参数
        user.heal(heal_amount)
        results.append({
            'type': 'heal',
            'target': user.name,
            'amount': heal_amount,
            'message': f'{user.name} 使用祛痕恢复了 {heal_amount} 点生命值'
        })
        
        # 2. 施加护盾
        shield_amount = self.get_shield_value()
        shield_result = self._apply_shield(user, shield_amount, game_state)
        results.append(shield_result)
        
        return {
            'card_name': self.name,
            'effects': results,
            'total_heal': heal_amount,
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