import random
import json
from enum import Enum
from typing import Dict, List, Optional
import time

class ActionType(Enum):
    """行动类型枚举"""
    ATTACK = "attack"
    DEFEND = "defend"
    SKILL = "skill"
    CHARGE = "charge"  # 充能，为下回合积累能量

class BattleStatus(Enum):
    """战斗状态枚举"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

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

class BattleAction:
    """战斗行动类"""
    def __init__(self, robot: Robot, action_type: ActionType, target: Robot = None, skill_index: int = None):
        self.robot = robot
        self.action_type = action_type
        self.target = target
        self.skill_index = skill_index
        self.timestamp = time.time()

class BattleEngine:
    """战斗引擎"""
    def __init__(self, robot1: Robot, robot2: Robot):
        self.robot1 = robot1
        self.robot2 = robot2
        self.current_turn = 1
        self.status = BattleStatus.WAITING
        self.battle_log = []
        self.winner = None
        
        # 回合行动存储
        self.pending_actions = {}  # {robot_owner_id: BattleAction}
    
    def start_battle(self):
        """开始战斗"""
        self.status = BattleStatus.IN_PROGRESS
        self.log_event("战斗开始！")
        self.log_event(f"{self.robot1.name} VS {self.robot2.name}")
    
    def log_event(self, message: str):
        """记录战斗日志"""
        log_entry = {
            "turn": self.current_turn,
            "timestamp": time.time(),
            "message": message
        }
        self.battle_log.append(log_entry)
        print(f"[回合 {self.current_turn}] {message}")
    
    def submit_action(self, owner_id: str, action_type: ActionType, target_id: str = None, skill_index: int = None) -> bool:
        """提交行动"""
        if self.status != BattleStatus.IN_PROGRESS:
            return False
        
        # 找到行动的机器人
        acting_robot = None
        target_robot = None
        
        if self.robot1.owner_id == owner_id:
            acting_robot = self.robot1
            target_robot = self.robot2
        elif self.robot2.owner_id == owner_id:
            acting_robot = self.robot2
            target_robot = self.robot1
        else:
            return False
        
        if not acting_robot.is_alive():
            return False
        
        # 验证技能
        if action_type == ActionType.SKILL:
            if skill_index is None or skill_index >= len(acting_robot.skills):
                return False
            skill = acting_robot.skills[skill_index]
            if acting_robot.energy < skill["cost"]:
                return False
        
        # 创建行动
        action = BattleAction(acting_robot, action_type, target_robot, skill_index)
        self.pending_actions[owner_id] = action
        
        return True
    
    def can_process_turn(self) -> bool:
        """检查是否可以处理回合"""
        return (len(self.pending_actions) == 2 or 
                any(not robot.is_alive() for robot in [self.robot1, self.robot2]))
    
    def process_turn(self) -> Dict:
        """处理回合"""
        if not self.can_process_turn():
            return {"success": False, "message": "等待玩家行动"}
        
        # 重置防御状态
        self.robot1.is_defending = False
        self.robot2.is_defending = False
        
        # 按速度排序行动
        actions = list(self.pending_actions.values())
        actions.sort(key=lambda x: x.robot.speed, reverse=True)
        
        turn_results = []
        
        # 执行行动
        for action in actions:
            if not action.robot.is_alive():
                continue
                
            result = self._execute_action(action)
            turn_results.append(result)
            
            # 检查战斗是否结束
            if self._check_battle_end():
                break
        
        # 清空待处理行动
        self.pending_actions.clear()
        
        # 回合结束处理
        self._end_turn_processing()
        
        self.current_turn += 1
        
        return {
            "success": True,
            "turn": self.current_turn - 1,
            "results": turn_results,
            "battle_status": self.get_battle_status()
        }
    
    def _execute_action(self, action: BattleAction) -> Dict:
        """执行单个行动"""
        robot = action.robot
        target = action.target
        result = {
            "robot": robot.name,
            "action": action.action_type.value,
            "success": True,
            "message": "",
            "damage": 0,
            "heal": 0
        }
        
        if action.action_type == ActionType.ATTACK:
            damage = robot.attack + random.randint(-3, 3)  # 添加随机性
            actual_damage = target.take_damage(damage)
            result["damage"] = actual_damage
            result["message"] = f"{robot.name} 攻击 {target.name}，造成 {actual_damage} 点伤害"
            self.log_event(result["message"])
            
        elif action.action_type == ActionType.DEFEND:
            robot.is_defending = True
            robot.gain_energy(10)  # 防御时获得少量能量
            result["message"] = f"{robot.name} 进入防御状态"
            self.log_event(result["message"])
            
        elif action.action_type == ActionType.SKILL:
            skill = robot.skills[action.skill_index]
            if robot.use_energy(skill["cost"]):
                if "damage_multiplier" in skill:
                    damage = int(robot.attack * skill["damage_multiplier"])
                    actual_damage = target.take_damage(damage)
                    result["damage"] = actual_damage
                    result["message"] = f"{robot.name} 使用技能 {skill['name']}，对 {target.name} 造成 {actual_damage} 点伤害"
                
                if "heal_amount" in skill:
                    heal_amount = robot.heal(skill["heal_amount"])
                    result["heal"] = heal_amount
                    result["message"] = f"{robot.name} 使用技能 {skill['name']}，恢复了 {heal_amount} 点生命值"
                
                if "energy_gain" in skill:
                    robot.gain_energy(skill["energy_gain"])
                
                self.log_event(result["message"])
            else:
                result["success"] = False
                result["message"] = f"{robot.name} 能量不足，无法使用技能 {skill['name']}"
                
        elif action.action_type == ActionType.CHARGE:
            robot.gain_energy(25)
            result["message"] = f"{robot.name} 充能，获得 25 点能量"
            self.log_event(result["message"])
        
        return result
    
    def _end_turn_processing(self):
        """回合结束处理"""
        # 为存活的机器人恢复少量能量
        for robot in [self.robot1, self.robot2]:
            if robot.is_alive():
                robot.gain_energy(5)
    
    def _check_battle_end(self) -> bool:
        """检查战斗是否结束"""
        if not self.robot1.is_alive():
            self.winner = self.robot2
            self.status = BattleStatus.FINISHED
            self.log_event(f"{self.robot2.name} 获胜！")
            return True
        elif not self.robot2.is_alive():
            self.winner = self.robot1
            self.status = BattleStatus.FINISHED
            self.log_event(f"{self.robot1.name} 获胜！")
            return True
        return False
    
    def get_battle_status(self) -> Dict:
        """获取战斗状态"""
        return {
            "status": self.status.value,
            "current_turn": self.current_turn,
            "robot1": self.robot1.get_status(),
            "robot2": self.robot2.get_status(),
            "winner": self.winner.name if self.winner else None,
            "pending_actions": list(self.pending_actions.keys())
        }
    
    def get_battle_log(self) -> List[Dict]:
        """获取战斗日志"""
        return self.battle_log

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