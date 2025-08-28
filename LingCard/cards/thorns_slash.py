# LingCard/cards/thorns_slash.py
from LingCard.cards.action_card import ActionCard
from LingCard.utils.enums import ActionType

class ThornsSlashCard(ActionCard):
    """
    披荆斩棘卡牌 (3cost)
    
    效果：
    - 对自身造成9点伤害
    - 对目标造成18点伤害
    - 对其召唤物造成30%的当前生命值伤害
    """
    
    def __init__(self):
        super().__init__(
            name="披荆斩棘",
            description="对自身造成9点伤害，对目标造成18点伤害，对其召唤物造成30%当前生命值伤害（消耗3点电能）",
            action_type=ActionType.SWORD_SPECIAL,
            energy_cost=3
        )
    
    def get_base_value(self) -> int:
        """获取对目标的基础伤害值"""
        return 18
    
    def get_self_damage(self) -> int:
        """获取对自身的伤害值"""
        return 9
    
    def get_summon_damage_percentage(self) -> float:
        """获取对召唤物的伤害百分比"""
        return 0.30  # 30%
    
    def execute_effect(self, user, target, game_state):
        """
        执行披荆斩棘的完整效果
        
        Args:
            user: 使用卡牌的角色
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            dict: 执行结果
        """
        results = []
        
        # 1. 对自身造成伤害
        self_damage = self.get_self_damage()
        actual_self_damage = user.take_damage(self_damage)
        results.append({
            'type': 'self_damage',
            'target': user.name,
            'damage': actual_self_damage,
            'message': f'{user.name} 使用披荆斩棘，对自身造成了 {actual_self_damage} 点伤害'
        })
        
        # 2. 对目标造成主要伤害
        main_damage = self.get_base_value()
        actual_main_damage = target.take_damage(main_damage)
        results.append({
            'type': 'main_damage',
            'target': target.name,
            'damage': actual_main_damage,
            'message': f'{user.name} 对 {target.name} 造成了 {actual_main_damage} 点伤害'
        })
        
        # 3. 对召唤物造成百分比伤害（如果存在召唤物系统）
        summon_damage_results = self._handle_summon_damage(target, game_state)
        results.extend(summon_damage_results)
        
        return {
            'card_name': self.name,
            'effects': results,
            'self_damage': actual_self_damage,
            'main_damage': actual_main_damage
        }
    
    def _handle_summon_damage(self, target, game_state):
        """
        处理对召唤物的伤害
        
        Args:
            target: 目标角色
            game_state: 游戏状态
            
        Returns:
            list: 召唤物伤害结果列表
        """
        results = []
        
        # 检查目标是否有召唤物系统
        if hasattr(target, 'summons') and target.summons:
            damage_percentage = self.get_summon_damage_percentage()
            
            for summon in target.summons[:]:  # 使用副本避免在迭代时修改列表
                current_hp = summon.current_hp
                summon_damage = int(current_hp * damage_percentage)
                
                if summon_damage > 0:
                    actual_summon_damage = summon.take_damage(summon_damage)
                    results.append({
                        'type': 'summon_damage',
                        'target': summon.name,
                        'damage': actual_summon_damage,
                        'percentage': damage_percentage * 100,
                        'message': f'{summon.name} 受到了 {actual_summon_damage} 点伤害（{damage_percentage*100}%当前生命值）'
                    })
                    
                    # 如果召唤物死亡，从列表中移除
                    if summon.current_hp <= 0:
                        target.summons.remove(summon)
                        results.append({
                            'type': 'summon_death',
                            'target': summon.name,
                            'message': f'{summon.name} 被摧毁了'
                        })
        else:
            # 如果没有召唤物，记录信息
            results.append({
                'type': 'no_summons',
                'message': f'{target.name} 没有召唤物'
            })
        
        return results
    
    def can_use(self, character) -> bool:
        """
        检查是否可以使用该卡牌
        考虑电能消耗和自伤后是否会导致死亡
        
        Args:
            character: 使用卡牌的角色
            
        Returns:
            bool: 是否可以使用
        """
        # 首先检查基础的电能消耗
        if not super().can_use(character):
            return False
        
        # 检查自伤后是否会导致死亡（留1点血的安全机制）
        self_damage = self.get_self_damage()
        if character.current_hp <= self_damage:
            return False
        
        return True