# -*- coding: utf-8 -*-
from .base_skill import BaseSkill, SkillRegistry, skill_tool
from .inventory_skill import InventorySkill
from .sales_skill import SalesSkill
from .analytics_skill import AnalyticsSkill
from .policy_skill import PolicyRAGSkill

def create_default_registry() -> SkillRegistry:
    """Khởi tạo và nạp toàn bộ các Kỹ năng nghiệp vụ vào Registry"""
    registry = SkillRegistry()
    registry.register(InventorySkill())
    registry.register(SalesSkill())
    registry.register(AnalyticsSkill())
    registry.register(PolicyRAGSkill())
    return registry

default_registry = create_default_registry()

__all__ = [
    "BaseSkill",
    "SkillRegistry",
    "skill_tool",
    "InventorySkill",
    "SalesSkill",
    "AnalyticsSkill",
    "PolicyRAGSkill",
    "create_default_registry",
    "default_registry"
]
