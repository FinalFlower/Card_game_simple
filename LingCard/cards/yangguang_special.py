from .action_card import ActionCard
from LingCard.core.game_state import GameState
from LingCard.core.player import Player
from LingCard.utils.enums import ActionType
from typing import List, Optional

class YangguangSpecialCard(ActionCard):
    """阳光的专属卡牌：皓日当空"""
    
    def __init__(self):
        super().__init__(
            name="皓日当空",
            description="对除自身外所有目标造成30点伤害。若额外付出3cost可免除队友所受伤害。",
            action_type=ActionType.SPECIAL,
            energy_cost=5
        )
        self.base_damage = 30
        self.can_pay_extra = True  # 标记是否可以支付额外费用
    
    def get_base_value(self) -> int:
        """获取基础伤害值"""
        return self.base_damage
    
    def get_extra_cost(self) -> int:
        """获取额外费用"""
        return 3 if self.can_pay_extra else 0
    
    def can_play(self, player: Player, game_state: GameState) -> bool:
        """检查是否可以打出此卡"""
        if not super().can_play(player, game_state):
            return False
        return True
    
    def play(self, player: Player, game_state: GameState, extra_cost: int = 0):
        """打出卡牌"""
        # 消耗基础能量
        # 使用第一个存活角色来消耗能量
        user_char = None
        if player.get_alive_characters():
            user_char = player.get_alive_characters()[0]
            user_char.consume_energy(self.energy_cost)
        
        # 检查是否支付额外费用
        protect_team = extra_cost >= 3
        
        if protect_team:
            if user_char:
                user_char.consume_energy(3)
            game_state.add_log(f"{user_char.name}使用{self.name}，额外消耗3点能量，为队友提供保护！")
        
        # 对除自身外所有目标造成伤害
        for target_player in game_state.players:
            for target_character in target_player.get_alive_characters():
                if target_character != user_char:  # 不对自身造成伤害
                    if protect_team and target_player == player:
                        # 如果支付了额外费用且是队友，跳过伤害
                        continue
                    
                    damage = self.base_damage
                    # 对于阳光角色，使用带攻击者信息的方法以触发反击
                    if hasattr(target_character, 'take_damage_with_attacker'):
                        actual_damage = target_character.take_damage_with_attacker(damage, game_state, user_char)
                    else:
                        actual_damage = target_character.take_damage(damage)
                    game_state.add_log(f"{target_character.name}受到了{actual_damage}点伤害！")
        
        # 如果保护队友，记录状态
        if protect_team:
            player.status['protected_team'] = True
            game_state.add_log(f"{user_char.name}的队友在本回合受到的伤害将被免除！")
