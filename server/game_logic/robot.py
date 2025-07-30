from typing import Dict, List, Optional


class Robot:
    """机器人类"""
    def __init__(self, name: str, owner_id: str, config: Dict = None):
        self.name = name
        self.owner_id = owner_id
        
        # 基础属性
        if config:
            self.max_hp = config.get('hp', 100)
            self.attack = config.get('attack', 20)
            self.defense = config.get('defense', 5)
            self.speed = config.get('speed', 10)
        else:
            # 默认属性
            self.max_hp = 100
            self.attack = 20
            self.defense = 5
            self.speed = 10
        
        # 当前状态
        self.current_hp = self.max_hp
        self.energy = 0  # 技能能量
        self.max_energy = 100
        self.is_defending = False
        self.status_effects = []  # 状态效果列表
        
        # 技能列表
        self.skills = [
            {"name": "重击", "cost": 30, "damage_multiplier": 1.5, "description": "造成1.5倍攻击力伤害"},
            {"name": "治疗", "cost": 40, "heal_amount": 30, "description": "恢复30点生命值"},
            {"name": "充能打击", "cost": 50, "damage_multiplier": 2.0, "energy_gain": 20, "description": "造成2倍伤害并获得额外能量"}
        ]
    
    def is_alive(self) -> bool:
        """检查机器人是否存活"""
        return self.current_hp > 0
    
    def take_damage(self, damage: int) -> int:
        """受到伤害"""
        if self.is_defending:
            damage = max(1, damage // 2)  # 防御状态减半伤害
        
        actual_damage = max(1, damage - self.defense)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗"""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def gain_energy(self, amount: int):
        """获得能量"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def use_energy(self, amount: int) -> bool:
        """消耗能量"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def get_status(self) -> Dict:
        """获取机器人状态"""
        return {
            "name": self.name,
            "owner_id": self.owner_id,
            "hp": self.current_hp,
            "max_hp": self.max_hp,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "is_defending": self.is_defending,
            "is_alive": self.is_alive()
        }