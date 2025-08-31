# LingCard/utils/deck_config_manager.py
"""
配卡配置管理模块
负责配卡配置的持久化存储、加载和验证
"""

import os
import yaml
from typing import Dict, Optional, List
from pathlib import Path

class DeckConfigManager:
    """配卡配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配卡配置管理器
        
        Args:
            config_dir: 配置文件存储目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "deck_config.yaml"
    
    def save_deck_config(self, player_id: str, config: Dict[str, int]) -> bool:
        """
        保存玩家的配卡配置
        
        Args:
            player_id: 玩家ID
            config: 配卡配置字典 {卡牌名称: 数量}
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证配置有效性
            if not self._validate_deck_config(config):
                return False
            
            # 加载现有配置
            all_configs = self._load_all_configs()
            
            # 更新指定玩家的配置
            all_configs[player_id] = config
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(all_configs, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"保存配卡配置失败: {e}")
            return False
    
    def load_deck_config(self, player_id: str) -> Optional[Dict[str, int]]:
        """
        加载指定玩家的配卡配置
        
        Args:
            player_id: 玩家ID
            
        Returns:
            Optional[Dict[str, int]]: 配卡配置，如果不存在则返回None
        """
        try:
            all_configs = self._load_all_configs()
            return all_configs.get(player_id)
        except Exception as e:
            print(f"加载配卡配置失败: {e}")
            return None
    
    def _validate_deck_config(self, config: Dict[str, int]) -> bool:
        """
        验证配卡配置的有效性
        
        Args:
            config: 配卡配置字典
            
        Returns:
            bool: 配置是否有效
        """
        if not isinstance(config, dict):
            return False
        
        # 检查卡牌总数是否合理 (通常为10-30张)
        total_cards = sum(config.values())
        if total_cards < 5 or total_cards > 50:
            return False
        
        # 检查每张卡牌数量是否合理
        for card_name, count in config.items():
            if not isinstance(card_name, str) or not isinstance(count, int):
                return False
            if count < 0 or count > 10:  # 每种卡牌最多10张
                return False
        
        # 检查卡牌类型是否在可用列表中
        available_cards = self.get_available_card_types()
        for card_name in config.keys():
            if card_name not in available_cards:
                return False
        
        return True
    
    def _load_all_configs(self) -> Dict[str, Dict[str, int]]:
        """
        加载所有玩家的配卡配置
        
        Returns:
            Dict[str, Dict[str, int]]: 所有玩家的配置
        """
        try:
            if not self.config_file.exists():
                return {}
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def get_default_deck_config(self) -> Dict[str, int]:
        """
        获取默认的配卡配置
        
        Returns:
            Dict[str, int]: 默认配卡配置
        """
        return {
            # 剑技卡牌
            'SharpSlashCard': 2,      # 锐斩 2张
            'SlidingBladeCard': 2,    # 滑刃 2张
            'RemoveScarsCard': 2,     # 祛痕 2张
            
            # 重铸系列（只有重铸.木刀在默认配置中）
            'ReforgeWoodenSwordCard': 1,  # 重铸.木刀 1张
            
            # 功能性卡牌
            'SwordEdgeTurnCard': 1,   # 剑锋直转 1张
            'WheelSlashCard': 1,      # 轮斩 1张
            
            # 补充卡牌以达到10张
            'DrawSwordSlashCard': 1   # 拔刀斩 1张
        }
    
    def get_available_card_types(self) -> List[str]:
        """
        获取所有可用的卡牌类型
        
        Returns:
            List[str]: 可用卡牌类型列表
        """
        return [
            # 剑技卡牌
            'SharpSlashCard',
            'SlidingBladeCard',
            'ThornsSlashCard',
            'RemoveScarsCard',
            'SwordEdgeTurnCard',
            'WheelSlashCard',
            'DrawSwordSlashCard',
            
            # 重铸系列卡牌（注意：除重铸.木刀外，其他重铸卡牌不应出现在可选列表中）
            'ReforgeWoodenSwordCard',
            # 'ReforgeCrudeIronCard',     # 不应出现在可选列表中
            # 'ReforgeFamousBladeCard',   # 不应出现在可选列表中
            # 'ReforgeDemonBladeCard',    # 不应出现在可选列表中
            # 'ReforgeMagicBladeCard',    # 不应出现在可选列表中
            
            # 解放系列卡牌（解放.魔刀不应出现在可选列表中）
            # 'LiberationMagicBladeCard'  # 不应出现在可选列表中
        ]
    
    def get_card_display_name(self, card_class_name: str) -> str:
        """
        获取卡牌的显示名称
        
        Args:
            card_class_name: 卡牌类名
            
        Returns:
            str: 卡牌显示名称
        """
        display_names = {
            # 剑技卡牌
            'SharpSlashCard': '锐斩',
            'SlidingBladeCard': '滑刃',
            'ThornsSlashCard': '披荆斩棘',
            'RemoveScarsCard': '祛痕',
            'SwordEdgeTurnCard': '剑锋直转',
            'WheelSlashCard': '轮斩',
            'DrawSwordSlashCard': '拔刀斩',
            
            # 重铸系列卡牌
            'ReforgeWoodenSwordCard': '重铸.木刀',
            'ReforgeCrudeIronCard': '重铸.粗制铁刃',
            'ReforgeFamousBladeCard': '重铸.名刀',
            'ReforgeDemonBladeCard': '重铸.妖刀',
            'ReforgeMagicBladeCard': '重铸.魔刀',
            
            # 解放系列卡牌
            'LiberationMagicBladeCard': '解放.魔刀',
            
            # 专属卡牌
            # 'YangguangSpecialCard': '皓日当空'  # 专属卡牌不显示在配卡界面
        }
        return display_names.get(card_class_name, card_class_name)
    
    def export_config_to_yaml(self, player_id: str, output_file: str) -> bool:
        """
        将指定玩家的配置导出为YAML文件
        
        Args:
            player_id: 玩家ID
            output_file: 输出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            config = self.load_deck_config(player_id)
            if config is None:
                return False
            
            import datetime
            export_data = {
                'player_id': player_id,
                'deck_config': config,
                'metadata': {
                    'total_cards': sum(config.values()),
                    'export_date': datetime.datetime.now().isoformat()
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config_from_yaml(self, input_file: str) -> Optional[str]:
        """
        从YAML文件导入配置
        
        Args:
            input_file: 输入文件路径
            
        Returns:
            Optional[str]: 导入的玩家ID，失败返回None
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            player_id = data.get('player_id')
            config = data.get('deck_config')
            
            if player_id and config and self.save_deck_config(player_id, config):
                return player_id
            
            return None
        except Exception as e:
            print(f"导入配置失败: {e}")
            return None


# 全局实例
_deck_config_manager = None

def get_deck_config_manager() -> DeckConfigManager:
    """
    获取全局的配卡配置管理器实例
    
    Returns:
        DeckConfigManager: 配卡配置管理器实例
    """
    global _deck_config_manager
    if _deck_config_manager is None:
        _deck_config_manager = DeckConfigManager()
    return _deck_config_manager
