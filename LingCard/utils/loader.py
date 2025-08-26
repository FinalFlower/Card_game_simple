# LingCard/utils/loader.py
import os
import importlib
import inspect
from typing import Dict, Type

def _load_classes_from_directory(directory: str, base_class: Type) -> Dict[str, Type]:
    """
    动态从指定目录加载继承自 base_class 的所有类。
    返回一个字典 {类名: 类对象}
    """
    loaded_classes = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"{os.path.basename(directory)}.{filename[:-3]}"
            # 修正导入路径
            full_module_path = f"LingCard.{module_name}"
            
            try:
                module = importlib.import_module(full_module_path)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, base_class) and obj is not base_class:
                        loaded_classes[name] = obj
            except ImportError as e:
                print(f"Error importing {full_module_path}: {e}")
                
    return loaded_classes

def load_characters() -> Dict[str, Type]:
    """加载所有角色类"""
    from LingCard.characters.character import Character
    # 获取当前文件的目录，并构建 characters 目录的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chars_dir = os.path.join(os.path.dirname(current_dir), 'characters')
    return _load_classes_from_directory(chars_dir, Character)

def load_cards() -> Dict[str, Type]:
    """加载所有行动卡类"""
    from LingCard.cards.action_card import ActionCard
    # 获取当前文件的目录，并构建 cards 目录的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cards_dir = os.path.join(os.path.dirname(current_dir), 'cards')
    return _load_classes_from_directory(cards_dir, ActionCard)