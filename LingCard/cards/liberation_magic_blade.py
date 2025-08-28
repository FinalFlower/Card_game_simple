# LingCard/cards/liberation_magic_blade.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType
from LingCard.buffs.demonic import DemonicBuff

class LiberationMagicBladeCard(ActionCard):
    """
    解放.魔刀卡牌 (5cost)
    
    效果：
    - 对主要目标造成25点伤害
    - 对其队伍队友造成10点伤害
    - 同时为自身施加一层堕魔
    """
    
    def __init__(self):
        super().__init__(
            name="解放.魔刀",
            description="对主要目标造成25点伤害，对其队伍队友造成10点伤害，自身获得1层堕魔（消耗5点电能）",
            action_type=ActionType.LIBERATION,
            energy_cost=5
        )
    
    def get_base_value(self) -> int:
        """获取对主要目标的基础伤害值"""
        return 25
    
    def get_aoe_damage(self) -> int:
        """获取对队友的范围伤害值"""
        return 10
    
    def execute_effect(self, user, target, game_state):
        """
        执行解放.魔刀的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 主要目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 对主要目标造成伤害
        main_damage = self.get_base_value()
        actual_main_damage = target.take_damage(main_damage)
        results.append({
            'type': 'main_damage',
            'target': target.name,
            'damage': actual_main_damage,
            'message': f'{user.name} 使用解放.魔刀对 {target.name} 造成了 {actual_main_damage} 点伤害'
        })
        
        # 累积主要伤害到发电等级
        if actual_main_damage > 0:
            user.add_damage_to_generation(actual_main_damage, game_state)
        
        # 2. 对队友造成范围伤害
        aoe_results = self._handle_aoe_damage(user, target, game_state)
        results.extend(aoe_results)
        
        # 3. 为使用者添加堕魔
        demonic_buff = DemonicBuff(stacks=1)
        user.buff_manager.add_buff(demonic_buff, game_state)
        results.append({
            'type': 'buff_applied',
            'target': user.name,
            'buff': 'demonic',
            'stacks': 1,
            'message': f'{user.name} 被魔刀的力量侵蚀，获得了1层堕魔'
        })
        
        return {
            'card_name': self.name,
            'effects': results,
            'main_damage': actual_main_damage,
            'aoe_damage': self.get_aoe_damage()
        }
    
    def _handle_aoe_damage(self, user, primary_target, game_state):
        """
        处理对队友的范围伤害
        
        Args:
            user: 使用卡牌的角色
            primary_target: 主要目标
            game_state: 游戏状态
            
        Returns:
            list: 范围伤害结果列表
        """
        results = []
        aoe_damage = self.get_aoe_damage()
        total_aoe_damage = 0  # 用于累积发电等级
        
        # 获取目标的队友
        teammates = self._get_teammates(primary_target, game_state)
        
        if teammates:
            for teammate in teammates:
                actual_aoe_damage = teammate.take_damage(aoe_damage)
                total_aoe_damage += actual_aoe_damage
                results.append({
                    'type': 'aoe_damage',
                    'target': teammate.name,
                    'damage': actual_aoe_damage,
                    'message': f'{teammate.name} 受到魔刀解放的余波影响，受到了 {actual_aoe_damage} 点伤害'
                })
        else:
            results.append({
                'type': 'no_teammates',
                'message': f'{primary_target.name} 没有队友，范围伤害无效'
            })
        
        # 累积范围伤害到发电等级
        if total_aoe_damage > 0:
            user.add_damage_to_generation(total_aoe_damage, game_state)
        
        return results
    
    def _get_teammates(self, target, game_state):
        """
        获取目标的队友列表
        
        Args:
            target: 主要目标
            game_state: 游戏状态
            
        Returns:
            list: 队友列表
        """
        teammates = []
        
        # 获取对手玩家（目标所在的玩家）
        opponent_player = game_state.get_opponent_player()
        
        # 获取对手的所有存活角色，除了主要目标
        if opponent_player:
            for character in opponent_player.get_alive_characters():
                if character != target:  # 排除主要目标
                    teammates.append(character)
        
        return teammates
    
    def can_use(self, character) -> bool:
        """
        检查是否可以使用该卡牌
        解放.魔刀需要大量电能，确保角色有足够的资源
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        return super().can_use(character)