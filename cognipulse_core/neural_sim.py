"""
CogniPulse - Real-time Reinforcement Learning Simulation Lab
Provides an interactive self-learning environment where an autonomous agent evolves
optimal navigation and decision policies in real time with dynamic reward telemetry.
"""

import random
import math
import time
from typing import Dict, List, Any, Tuple

class GridWorldSimulation:
    """
    Dynamic 8x8 GridWorld with goal, shifting obstacles, and dynamic reward gradients.
    Agent uses Q-Learning with epsilon-greedy decay to master navigation autonomously.
    """
    def __init__(self, size: int = 8):
        self.size = size
        self.agent_pos = [0, 0]
        self.goal_pos = [size - 1, size - 1]
        self.obstacles = [[1, 2], [2, 2], [3, 2], [5, 4], [5, 5], [2, 5], [3, 5]]
        self.actions = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.action_vectors = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Q-Table: (row, col) -> [q_up, q_right, q_down, q_left]
        self.q_table: Dict[Tuple[int, int], List[float]] = {}
        for r in range(size):
            for c in range(size):
                self.q_table[(r, c)] = [0.0, 0.0, 0.0, 0.0]

        self.lr = 0.2          # Learning rate (Alpha)
        self.gamma = 0.95      # Discount factor
        self.epsilon = 0.8     # Exploration probability
        self.min_epsilon = 0.05
        self.epsilon_decay = 0.995

        self.episode = 0
        self.total_steps = 0
        self.episode_rewards: List[float] = []
        self.cumulative_loss: List[float] = []
        self.is_running = False

    def reset_agent(self):
        self.agent_pos = [0, 0]

    def choose_action(self, state: Tuple[int, int]) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        q_vals = self.q_table[state]
        max_v = max(q_vals)
        best_actions = [i for i, v in enumerate(q_vals) if v == max_v]
        return random.choice(best_actions)

    def step(self) -> Dict[str, Any]:
        """Performs a single discrete self-learning step."""
        state = (self.agent_pos[0], self.agent_pos[1])
        action_idx = self.choose_action(state)
        dr, dc = self.action_vectors[action_idx]
        
        new_r = max(0, min(self.size - 1, self.agent_pos[0] + dr))
        new_c = max(0, min(self.size - 1, self.agent_pos[1] + dc))
        next_pos = [new_r, new_c]

        # Reward Calculation
        if next_pos == self.goal_pos:
            reward = 100.0
            done = True
        elif next_pos in self.obstacles:
            reward = -20.0
            done = False
            next_pos = self.agent_pos  # bounce back
        else:
            # Distance-based shaping reward
            old_dist = abs(self.agent_pos[0] - self.goal_pos[0]) + abs(self.agent_pos[1] - self.goal_pos[1])
            new_dist = abs(next_pos[0] - self.goal_pos[0]) + abs(next_pos[1] - self.goal_pos[1])
            reward = 1.0 if new_dist < old_dist else -1.0
            done = False

        next_state = (next_pos[0], next_pos[1])
        
        # Bellman Q-Update
        old_q = self.q_table[state][action_idx]
        max_future_q = max(self.q_table[next_state]) if not done else 0.0
        td_target = reward + self.gamma * max_future_q
        td_error = td_target - old_q
        self.q_table[state][action_idx] = old_q + self.lr * td_error

        # Update Agent Pos
        self.agent_pos = next_pos
        self.total_steps += 1

        if done:
            self.episode += 1
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            self.reset_agent()

        return {
            "agent_pos": self.agent_pos,
            "action": self.actions[action_idx],
            "reward": reward,
            "done": done,
            "episode": self.episode,
            "total_steps": self.total_steps,
            "epsilon": round(self.epsilon, 3),
            "td_loss": round(abs(td_error), 4)
        }

    def run_episodes(self, count: int = 10) -> Dict[str, Any]:
        """Runs batch simulation episodes for fast training."""
        steps_history = []
        for _ in range(count):
            self.reset_agent()
            ep_reward = 0.0
            ep_steps = 0
            done = False
            while not done and ep_steps < 100:
                result = self.step()
                ep_reward += result["reward"]
                ep_steps += 1
                done = result["done"]
            
            steps_history.append({"episode": self.episode, "reward": round(ep_reward, 2), "steps": ep_steps})
            self.episode_rewards.append(ep_reward)

        return {
            "episodes_completed": count,
            "current_episode": self.episode,
            "epsilon": round(self.epsilon, 3),
            "history": steps_history[-10:]
        }

    def get_state(self) -> Dict[str, Any]:
        """Serializes current environment and policy matrix for frontend rendering."""
        # Convert Q-table to 2D heat/arrow grid
        q_grid = []
        for r in range(self.size):
            row_vals = []
            for c in range(self.size):
                vals = self.q_table[(r, c)]
                best_act = self.actions[vals.index(max(vals))] if max(vals) > 0 else "NONE"
                row_vals.append({
                    "r": r,
                    "c": c,
                    "q_values": [round(v, 2) for v in vals],
                    "max_q": round(max(vals), 2),
                    "best_action": best_act
                })
            q_grid.append(row_vals)

        return {
            "size": self.size,
            "agent_pos": self.agent_pos,
            "goal_pos": self.goal_pos,
            "obstacles": self.obstacles,
            "episode": self.episode,
            "total_steps": self.total_steps,
            "epsilon": round(self.epsilon, 3),
            "q_grid": q_grid
        }
