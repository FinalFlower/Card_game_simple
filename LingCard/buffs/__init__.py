# LingCard/buffs/__init__.py
"""
Buff系统模块

包含所有buff效果的实现，如中毒、燃烧、冰冻等。
所有buff都继承自core.buff_system.Buff基类。
"""

from .poison import PoisonBuff
from .sword_intent import SwordIntentBuff
from .demonic import DemonicBuff
from .shield import ShieldBuff

# 导出所有buff类，便于动态加载
__all__ = [
    'PoisonBuff',
    'SwordIntentBuff',
    'DemonicBuff',
    'ShieldBuff'
]

# Buff类注册表，用于序列化和反序列化
BUFF_CLASSES = {
    'PoisonBuff': PoisonBuff,
    'SwordIntentBuff': SwordIntentBuff,
    'DemonicBuff': DemonicBuff,
    'ShieldBuff': ShieldBuff
}