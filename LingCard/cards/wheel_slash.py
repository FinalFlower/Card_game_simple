# LingCard/cards/wheel_slash.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.buffs.sword_intent import SwordIntentBuff

class WheelSlashCard(ActionCard):
    """
    轮斩卡牌 (2cost)
    
    效果：
    - 使用后在下一自身回合回复3点cost
    - 抽取1张行动卡
    - 为自身施加2层剑意
    """
    
    def __init__(self):
        super().__init__(
            name="轮斩",
            description="下一回合回复3点电能并抽取1张行动卡，获得2层剑意（消耗2点电能）",
            action_type=ActionType.SWORD_SUPPORT,
            energy_cost=2
        )
    
    def get_base_value(self) -> int:
        """获取剑意层数"""
        return 2
    
    def get_energy_restore_amount(self) -> int:
        """获取下回合回复的电能数量"""
        return 3
    
    def get_draw_card_amount(self) -> int:
        """获取下回合抽取的卡牌数量"""
        return 1
    
    def execute_effect(self, user, target, game_state):
        """
        执行轮斩的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色（对于自我增益卡，target通常等于user）
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 添加下回合回复电能的延迟效果
        energy_restore_amount = self.get_energy_restore_amount()
        energy_delay_effect = {
            'type': 'restore_energy',
            'target_player': user.name,
            'amount': energy_restore_amount,
            'trigger_turn': game_state.get_next_turn_for_player(user.name),
            'description': f'{user.name} 在下回合将恢复{energy_restore_amount}点电能（轮斩效果）'
        }
        game_state.add_delayed_effect(energy_delay_effect)
        results.append({
            'type': 'delayed_effect',
            'effect_type': 'energy_restore',
            'amount': energy_restore_amount,
            'message': f'{user.name} 将在下回合恢复{energy_restore_amount}点电能'
        })
        
        # 2. 添加下回合抽卡的延迟效果
        draw_amount = self.get_draw_card_amount()
        draw_delay_effect = {
            'type': 'draw_card',
            'target_player': user.name,
            'amount': draw_amount,
            'trigger_turn': game_state.get_next_turn_for_player(user.name),
            'description': f'{user.name} 在下回合将抽取{draw_amount}张行动卡（轮斩效果）'
        }
        game_state.add_delayed_effect(draw_delay_effect)
        results.append({
            'type': 'delayed_effect',
            'effect_type': 'draw_card',
            'amount': draw_amount,
            'message': f'{user.name} 将在下回合抽取{draw_amount}张行动卡'
        })
        
        # 3. 为使用者添加剑意
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
        
        return {
            'card_name': self.name,
            'effects': results,
            'sword_intent_gained': sword_intent_stacks,
            'delayed_energy_restore': energy_restore_amount,
            'delayed_card_draw': draw_amount
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