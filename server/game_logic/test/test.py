import random
import json
from enum import Enum
from typing import Dict, List, Optional
import time



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




# 示例使用
if __name__ == "__main__":
    # 创建两个机器人
    robot1_config = {"hp": 120, "attack": 25, "defense": 8, "speed": 12}
    robot2_config = {"hp": 100, "attack": 30, "defense": 5, "speed": 15}
    
    robot1 = Robot("钢铁战士", "player1", robot1_config)
    robot2 = Robot("闪电突击", "player2", robot2_config)
    
    # 创建战斗引擎
    battle = BattleEngine(robot1, robot2)
    battle.start_battle()
    
    # 模拟几个回合
    for turn in range(3):
        print(f"\n=== 第 {turn + 1} 回合 ===")
        
        # 玩家1行动（随机选择）
        actions = [ActionType.ATTACK, ActionType.DEFEND, ActionType.CHARGE]
        if robot1.energy >= 30:
            actions.append(ActionType.SKILL)
        
        action1 = random.choice(actions)
        skill_idx = 0 if action1 == ActionType.SKILL else None
        battle.submit_action("player1", action1, skill_index=skill_idx)
        
        # 玩家2行动（随机选择）
        action2 = random.choice([ActionType.ATTACK, ActionType.DEFEND, ActionType.CHARGE])
        battle.submit_action("player2", action2)
        
        # 处理回合
        result = battle.process_turn()
        print(f"回合结果: {result}")
        
        if battle.status == BattleStatus.FINISHED:
            break
    
    print(f"\n最终状态: {battle.get_battle_status()}")