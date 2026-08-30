"""
CogniPulse - Adaptive Learning Engine & Error Reflection Loop
Handles dynamic rule mutation, reinforcement feedback, active learning, and heuristic evolution.
"""

import time
import json
import os
import math
from typing import Dict, List, Any, Optional

class AdaptiveRule:
    """Represents an autonomous rule or heuristic synthesized through learning."""
    def __init__(self, rule_id: str, trigger_pattern: str, action_guidance: str, reward_score: float = 1.0):
        self.rule_id = rule_id
        self.trigger_pattern = trigger_pattern
        self.action_guidance = action_guidance
        self.reward_score = reward_score
        self.applications_count = 0
        self.success_count = 0
        self.created_at = time.time()
        self.last_applied = time.time()

    def apply(self, success: bool = True):
        self.applications_count += 1
        self.last_applied = time.time()
        if success:
            self.success_count += 1
            self.reward_score = min(5.0, self.reward_score + 0.25)
        else:
            self.reward_score = max(0.1, self.reward_score - 0.5)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "trigger_pattern": self.trigger_pattern,
            "action_guidance": self.action_guidance,
            "reward_score": round(self.reward_score, 3),
            "applications_count": self.applications_count,
            "success_rate": round(self.success_count / max(1, self.applications_count), 2),
            "created_at": self.created_at
        }


class LearningEngine:
    """
    Coordinates self-reflection, feedback ingestion, rule mutation, and accuracy scoring.
    """
    def __init__(self, storage_path: str = "cognipulse_rules.json"):
        self.storage_path = storage_path
        self.rules: Dict[str, AdaptiveRule] = {}
        self.feedback_history: List[Dict[str, Any]] = []
        self.learning_curve: List[Dict[str, Any]] = []  # Chronological accuracy tracking
        self.total_reinforcements = 0
        self.total_corrections = 0
        self._init_defaults()
        self.load()

    def _init_defaults(self):
        seed_rules = [
            ("rule_conciseness", "length|detailed", "Prioritize dense, clear conceptual explanations with structured bullet points.", 1.2),
            ("rule_fact_verification", "who|what|when|where", "Cross-reference working memory and semantic graph before asserting certainty.", 1.5),
            ("rule_learning_humility", "wrong|mistake|incorrect", "Acknowledge correction immediately, assimilate ground truth, and adjust synaptic weights.", 2.0)
        ]
        for rid, trig, guide, rew in seed_rules:
            if rid not in self.rules:
                self.rules[rid] = AdaptiveRule(rid, trig, guide, rew)

    def process_feedback(self, query: str, response: str, is_positive: bool, correction_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingests user feedback (thumbs up / thumbs down / correction) and mutates weights and rules.
        """
        timestamp = time.time()
        if is_positive:
            self.total_reinforcements += 1
            delta = 0.3
            # Reinforce matching rules
            for rule in self.rules.values():
                if any(k in query.lower() for k in rule.trigger_pattern.split('|')):
                    rule.apply(success=True)
        else:
            self.total_corrections += 1
            delta = -0.6
            for rule in self.rules.values():
                if any(k in query.lower() for k in rule.trigger_pattern.split('|')):
                    rule.apply(success=False)

        # Synthesize a new corrective rule if a specific correction was provided
        new_rule_created = None
        if correction_text and not is_positive:
            new_rule_id = f"rule_corr_{int(timestamp * 1000)}"
            trigger = query.strip().lower()[:25]
            guidance = f"When queried about '{trigger}', ensure to follow: {correction_text.strip()}"
            new_rule = AdaptiveRule(new_rule_id, trigger, guidance, reward_score=2.0)
            self.rules[new_rule_id] = new_rule
            new_rule_created = new_rule.to_dict()

        # Update learning curve point
        total_evals = max(1, self.total_reinforcements + self.total_corrections)
        accuracy = self.total_reinforcements / total_evals
        curve_point = {
            "timestamp": timestamp,
            "reinforcements": self.total_reinforcements,
            "corrections": self.total_corrections,
            "accuracy": round(accuracy * 100, 1),
            "total_rules": len(self.rules)
        }
        self.learning_curve.append(curve_point)
        if len(self.learning_curve) > 100:
            self.learning_curve.pop(0)

        record = {
            "timestamp": timestamp,
            "query": query,
            "is_positive": is_positive,
            "correction": correction_text,
            "new_rule": new_rule_created
        }
        self.feedback_history.append(record)
        self.save()

        return {
            "status": "reinforced" if is_positive else "corrected",
            "accuracy": round(accuracy * 100, 1),
            "new_rule": new_rule_created,
            "curve_point": curve_point
        }

    def get_applicable_guidelines(self, query: str) -> List[str]:
        """Finds highest-reward active rules for the current query context."""
        applicable = []
        q_lower = query.lower()
        sorted_rules = sorted(self.rules.values(), key=lambda r: r.reward_score, reverse=True)
        
        for rule in sorted_rules:
            triggers = [t.strip().lower() for t in rule.trigger_pattern.split('|')]
            if any(t in q_lower for t in triggers) or rule.reward_score >= 1.5:
                applicable.append(rule.action_guidance)

        return applicable[:4]

    def get_metrics(self) -> Dict[str, Any]:
        total_events = self.total_reinforcements + self.total_corrections
        acc = (self.total_reinforcements / total_events * 100) if total_events > 0 else 92.5
        
        return {
            "total_reinforcements": self.total_reinforcements,
            "total_corrections": self.total_corrections,
            "active_rules": len(self.rules),
            "accuracy_percentage": round(acc, 1),
            "synaptic_plasticity_index": round(min(1.0, 0.4 + (len(self.rules) * 0.05)), 2),
            "rules": [r.to_dict() for r in sorted(self.rules.values(), key=lambda x: x.reward_score, reverse=True)]
        }

    def save(self):
        try:
            data = {
                "rules": {k: v.to_dict() for k, v in self.rules.items()},
                "total_reinforcements": self.total_reinforcements,
                "total_corrections": self.total_corrections,
                "learning_curve": self.learning_curve,
                "feedback_history": self.feedback_history[-50:]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[LearningEngine] Error saving: {e}")

    def load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.total_reinforcements = data.get("total_reinforcements", 0)
                self.total_corrections = data.get("total_corrections", 0)
                self.learning_curve = data.get("learning_curve", [])
                self.feedback_history = data.get("feedback_history", [])
                
                for rid, rdata in data.get("rules", {}).items():
                    rule = AdaptiveRule(
                        rule_id=rdata["rule_id"],
                        trigger_pattern=rdata["trigger_pattern"],
                        action_guidance=rdata["action_guidance"],
                        reward_score=rdata.get("reward_score", 1.0)
                    )
                    rule.applications_count = rdata.get("applications_count", 0)
                    rule.success_count = int(rdata.get("success_rate", 1.0) * rule.applications_count)
                    self.rules[rid] = rule
        except Exception as e:
            print(f"[LearningEngine] Error loading: {e}")
