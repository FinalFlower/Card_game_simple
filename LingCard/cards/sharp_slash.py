# LingCard/cards/sharp_slash.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.buffs.sword_intent import SwordIntentBuff

class SharpSlashCard(ActionCard):
    """
    锐斩卡牌 (2cost)
    
    效果：
    - 对目标造成12点伤害
    - 同时在下一个自身回合抽取1张行动卡
    - 同时为自身施加一层剑意
    """
    
    def __init__(self):
        super().__init__(
            name="锐斩",
            description="对目标造成12点伤害，下一回合抽取1张行动卡，获得1层剑意（消耗2点电能）",
            action_type=ActionType.SWORD_ATTACK,
            energy_cost=2
        )
    
    def get_base_value(self) -> int:
        """获取基础伤害值"""
        return 12
    
    def execute_effect(self, user, target, game_state):
        """
        执行锐斩的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 造成基础伤害
        damage = self.get_base_value()
        actual_damage = target.take_damage(damage)
        results.append({
            'type': 'damage',
            'target': target.name,
            'damage': actual_damage,
            'message': f'{user.name} 使用锐斩对 {target.name} 造成了 {actual_damage} 点伤害'
        })
        
        # 累积伤害到发电等级
        if actual_damage > 0:
            user.add_damage_to_generation(actual_damage, game_state)
        
        # 2. 添加下回合抽卡效果（延迟效果）
        delay_effect = {
            'type': 'draw_card',
            'target_player': user.name,
            'amount': 1,
            'trigger_turn': game_state.get_next_turn_for_player(user.name),
            'description': f'{user.name} 在下回合将抽取1张行动卡（锐斩效果）'
        }
        game_state.add_delayed_effect(delay_effect)
        results.append({
            'type': 'delayed_effect',
            'message': f'{user.name} 将在下回合抽取1张行动卡'
        })
        
        # 3. 为使用者添加剑意
        sword_intent_buff = SwordIntentBuff(stacks=1)
        user.buff_manager.add_buff(sword_intent_buff, game_state)
        results.append({
            'type': 'buff_applied',
            'target': user.name,
            'buff': 'sword_intent',
            'stacks': 1,
            'message': f'{user.name} 获得了1层剑意'
        })
        
        return {
            'card_name': self.name,
            'effects': results,
            'total_damage': actual_damage
        }