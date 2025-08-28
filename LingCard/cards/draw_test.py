# LingCard/cards/draw_test.py
from .action_card import ActionCard
from LingCard.utils.enums import ActionType

class DrawTestCard(ActionCard):
    """
    抽卡测试卡牌
    消耗2点电能，在下回合开始时抽取2张行动卡
    """
    
    def __init__(self):
        super().__init__(
            name="抽卡测试",
            action_type=ActionType.SPECIAL,  # 使用特殊类型
            energy_cost=2,
            description="消耗2点电能，在下回合开始时抽取2张行动卡"
        )
    
    def get_base_value(self):
        """抽卡测试卡的基础值是抽卡数量"""
        return 2
    
    def can_use(self, character):
        """检查是否可以使用这张卡"""
        # 检查角色是否存活且有足够电能
        if not character.is_alive:
            return False
        
        energy_status = character.get_energy_status()
        return energy_status['current_energy'] >= self.energy_cost
    
    def apply_effect(self, game_state, user_char, target_char=None):
        """
        应用抽卡测试效果
        在使用者身上添加一个"下回合抽卡"的状态标记
        """
        # 在角色状态中添加下回合抽卡标记
        if 'next_turn_draw' not in user_char.status:
            user_char.status['next_turn_draw'] = 0
        
        user_char.status['next_turn_draw'] += self.get_base_value()
        
        game_state.add_log(f"{user_char.name} 使用了{self.name}，下回合开始时将额外抽取{self.get_base_value()}张卡")
        
        return True