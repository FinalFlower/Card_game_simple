# LingCard/cards/reforge_base.py
from abc import abstractmethod
from typing import Optional, Type
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType

class ReforgeCard(ActionCard):
    """
    重铸系列卡牌基类
    
    重铸系列卡牌的共同特点：
    - 造成伤害
    - 使用后移出战斗，本场游戏无法再次抽取
    - 在本回合结束后向手中置入升级后的卡牌
    """
    
    def __init__(self, name: str, description: str, energy_cost: int, damage: int, next_card_name: Optional[str] = None):
        super().__init__(
            name=name,
            description=description,
            action_type=ActionType.REFORGE,
            energy_cost=energy_cost
        )
        self.damage = damage
        self.next_card_name = next_card_name  # 下一级卡牌名称
        self.is_single_use = True  # 标记为单次使用卡牌
    
    def get_base_value(self) -> int:
        """获取基础伤害值"""
        return self.damage
    
    @abstractmethod
    def get_next_card_class(self) -> Optional[Type['ActionCard']]:
        """获取下一级卡牌的类"""
        pass
    
    def execute_effect(self, user, target, game_state):
        """
        执行重铸卡牌的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 造成伤害
        damage = self.get_base_value()
        actual_damage = target.take_damage(damage)
        results.append({
            'type': 'damage',
            'target': target.name,
            'damage': actual_damage,
            'message': f'{user.name} 使用{self.name}对 {target.name} 造成了 {actual_damage} 点伤害'
        })
        
        # 累积伤害到发电等级
        if actual_damage > 0:
            user.add_damage_to_generation(actual_damage, game_state)
        
        # 2. 移出战斗（标记为已使用，不再出现在牌库中）
        self._mark_as_used(user, game_state)
        results.append({
            'type': 'card_removed',
            'message': f'{self.name} 已移出战斗，本场游戏无法再次抽取'
        })
        
        # 3. 添加下回合获得升级卡牌的效果
        if self.next_card_name:
            next_card_effect = self._create_next_card_effect(user, game_state)
            results.append(next_card_effect)
        
        return {
            'card_name': self.name,
            'effects': results,
            'total_damage': actual_damage,
            'is_final_form': self.next_card_name is None
        }
    
    def _mark_as_used(self, user, game_state):
        """
        标记卡牌为已使用，从所有牌库中移除
        
        Args:
            user: 使用卡牌的角色
            game_state: 游戏状态
        """
        # 从玩家的牌库、手牌、弃牌堆中移除此卡牌
        card_name = self.__class__.__name__
        
        # 标记在游戏状态中，确保不再生成
        if not hasattr(game_state, 'removed_cards'):
            game_state.removed_cards = set()
        game_state.removed_cards.add(card_name)
        
        # 获取当前玩家
        current_player = game_state.get_current_player()
        if current_player:
            # 从牌库中移除
            current_player.deck = [card for card in current_player.deck if card.__class__.__name__ != card_name]
            # 从手牌中移除
            current_player.hand = [card for card in current_player.hand if card.__class__.__name__ != card_name]
            # 从弃牌堆中移除
            current_player.discard_pile = [card for card in current_player.discard_pile if card.__class__.__name__ != card_name]
    
    def _create_next_card_effect(self, user, game_state):
        """
        创建回合结束后获得升级卡牌的延迟效果
        
        Args:
            user: 使用卡牌的角色
            game_state: 游戏状态
            
        Returns:
            dict: 延迟效果结果
        """
        # 获取当前玩家
        current_player = game_state.get_current_player()
        player_name = f"player_{current_player.id}"
        
        delay_effect = {
            'type': 'add_card_to_hand',
            'target_player': player_name,
            'card_class': self.get_next_card_class(),
            'trigger_type': 'turn_end',  # 新增：设置为回合结束时触发
            'trigger_turn': game_state.current_round,  # 修改：在当前回合结束时触发
            'description': f'{player_name} 在本回合结束后将获得 {self.next_card_name}（重铸效果）'
        }
        game_state.add_delayed_effect(delay_effect)
        
        return {
            'type': 'delayed_effect',
            'message': f'{user.name} 将在本回合结束后获得 {self.next_card_name}'
        }
    
    def can_use(self, character) -> bool:
        """
        检查是否可以使用该卡牌
        重铸卡牌除了基础检查外，还要确保没有被移出战斗
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        # 检查角色是否有足够的电能
        if not character.can_consume_energy(self.energy_cost):
            return False
        
        return True