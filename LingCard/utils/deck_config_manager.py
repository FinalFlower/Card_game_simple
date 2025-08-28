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
    
    def get_default_deck_config(self) -> Dict[str, int]:
        """
        获取默认的配卡配置
        
        Returns:
            Dict[str, int]: 默认配卡配置
        """
        return {
            'AttackCard': 3,
            'HealCard': 2,
            'DefendCard': 3,
            'PoisonCard': 1,
            'DrawTestCard': 1
        }
    
    def delete_deck_config(self, player_id: str) -> bool:
        """
        删除指定玩家的配卡配置
        
        Args:
            player_id: 玩家ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            all_configs = self._load_all_configs()
            if player_id in all_configs:
                del all_configs[player_id]
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(all_configs, f, allow_unicode=True, default_flow_style=False)
                
                return True
            return False
        except Exception as e:
            print(f"删除配卡配置失败: {e}")
            return False
    
    def list_all_player_configs(self) -> Dict[str, Dict[str, int]]:
        """
        列出所有玩家的配卡配置
        
        Returns:
            Dict[str, Dict[str, int]]: 所有玩家的配卡配置
        """
        return self._load_all_configs()
    
    def _load_all_configs(self) -> Dict[str, Dict[str, int]]:
        """
        加载所有玩家的配卡配置
        
        Returns:
            Dict[str, Dict[str, int]]: 所有配置的字典
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError):
            return {}
    
    def _validate_deck_config(self, config: Dict[str, int]) -> bool:
        """
        验证配卡配置的有效性
        
        Args:
            config: 配卡配置
            
        Returns:
            bool: 配置是否有效
        """
        if not isinstance(config, dict):
            return False
        
        # 检查卡牌总数是否为10张
        total_cards = sum(config.values())
        if total_cards != 10:
            print(f"配卡配置无效：总卡牌数为{total_cards}，必须为10张")
            return False
        
        # 检查是否有负数
        for card_name, count in config.items():
            if not isinstance(count, int) or count < 0:
                print(f"配卡配置无效：卡牌{card_name}的数量必须为非负整数")
                return False
        
        return True
    
    def get_available_card_types(self) -> List[str]:
        """
        获取所有可用的卡牌类型
        
        Returns:
            List[str]: 可用卡牌类型列表
        """
        return [
            'AttackCard',
            'HealCard', 
            'DefendCard',
            'PoisonCard',
            'DrawTestCard'
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
            'AttackCard': '攻击卡',
            'HealCard': '治疗卡',
            'DefendCard': '防御卡',
            'PoisonCard': '淬毒卡',
            'DrawTestCard': '抽卡测试'
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