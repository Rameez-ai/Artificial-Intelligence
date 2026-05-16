"""
Smart Loan AI - RL Recommendation Service
============================================
Serves personalized recommendations from the trained RL agent.
"""

import os
import pickle
from firebase.operations import FirebaseOperations

RECOMMENDATIONS_COLLECTION = "recommendations"
_agent = None
_env = None


class RLService:
    """Reinforcement learning recommendation service."""

    @staticmethod
    def load_agent():
        """Load the trained RL agent."""
        global _agent, _env
        agent_path = os.path.join(os.path.dirname(__file__), '..', 'rl', 'trained_agent.pkl')

        if os.path.exists(agent_path):
            with open(agent_path, 'rb') as f:
                _agent = pickle.load(f)

        from rl.environment import LoanRecommendationEnv
        _env = LoanRecommendationEnv()

    @staticmethod
    def get_recommendations(user_profile: dict, user_id: str = None, n_recommendations: int = 3) -> dict:
        """Get personalized recommendations for a user."""
        global _agent, _env
        from rl.environment import LoanRecommendationEnv, ACTION_DESCRIPTIONS, RecommendationAction

        if _env is None:
            _env = LoanRecommendationEnv()

        state = _env.reset(user_profile)

        if _agent is not None:
            # Use trained agent
            top_actions = _agent.get_top_actions(state, n=n_recommendations)
        else:
            # Fallback: recommend based on weakest areas
            top_actions = RLService._heuristic_recommendations(state, n_recommendations)

        recommendations = []
        for action_idx, q_value in top_actions:
            action_info = ACTION_DESCRIPTIONS[RecommendationAction(action_idx)]
            recommendations.append({
                'action_id': action_idx,
                'title': action_info['title'],
                'description': action_info['description'],
                'tips': action_info['tips'],
                'confidence': round(max(0, min(1, (q_value + 2) / 4)), 2),
                'priority': 'high' if q_value > 1 else 'medium' if q_value > 0 else 'low'
            })

        # Save recommendations
        if user_id:
            FirebaseOperations.create(RECOMMENDATIONS_COLLECTION, {
                'user_id': user_id,
                'recommendations': [r['title'] for r in recommendations],
                'user_profile_snapshot': {k: v for k, v in user_profile.items()
                                          if k in ['credit_score', 'annual_income', 'existing_debts']}
            })

        state_labels = ['Credit Health', 'Debt Management', 'Savings Rate',
                        'Income Level', 'Loan Affordability', 'Employment', 'Education']
        user_state = {label: round(float(state[i]) * 100, 1) for i, label in enumerate(state_labels)}

        return {
            'recommendations': recommendations,
            'user_state': user_state
        }

    @staticmethod
    def _heuristic_recommendations(state, n):
        """Fallback heuristic when RL agent is not trained."""
        # Map state dimensions to actions
        dim_to_actions = {
            0: 3,   # credit -> IMPROVE_CREDIT
            1: 1,   # dti -> PAY_DOWN_DEBT
            2: 0,   # savings -> REDUCE_EXPENSES
            3: 2,   # income -> INCREASE_INCOME
            4: 4,   # loan_afford -> REDUCE_LOAN_AMOUNT
            5: 2,   # employment -> INCREASE_INCOME
            6: 9,   # education -> FINANCIAL_EDUCATION
        }

        # Sort by weakness (lowest state value)
        sorted_dims = sorted(range(len(state)), key=lambda i: state[i])
        seen_actions = set()
        result = []

        for dim in sorted_dims:
            action = dim_to_actions.get(dim, 9)
            if action not in seen_actions:
                seen_actions.add(action)
                weakness = 1 - state[dim]
                result.append((action, weakness * 2))
            if len(result) >= n:
                break

        return result

    @staticmethod
    def submit_feedback(user_id: str, recommendation_id: str, helpful: bool, action_taken: str = None):
        """Process user feedback for RL reward signal."""
        FirebaseOperations.create("recommendation_feedback", {
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'helpful': helpful,
            'action_taken': action_taken,
            'reward': 1.0 if helpful else -0.5
        })
        return {"status": "feedback_recorded"}

    @staticmethod
    def get_metrics() -> dict:
        """Get RL agent performance metrics."""
        global _agent
        if _agent is not None:
            return _agent.get_metrics()
        return {
            'total_episodes': 0,
            'q_table_size': 0,
            'epsilon': 1.0,
            'avg_reward_last_100': 0,
            'status': 'Agent not loaded'
        }
