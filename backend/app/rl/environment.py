"""
Smart Loan AI - RL Custom Environment
======================================
Custom OpenAI Gym-style environment for financial recommendation.
"""

import numpy as np
from enum import IntEnum


class RecommendationAction(IntEnum):
    REDUCE_EXPENSES = 0
    PAY_DOWN_DEBT = 1
    INCREASE_INCOME = 2
    IMPROVE_CREDIT = 3
    REDUCE_LOAN_AMOUNT = 4
    EXTEND_LOAN_TERM = 5
    BUILD_SAVINGS = 6
    CONSOLIDATE_DEBT = 7
    DIVERSIFY_INCOME = 8
    FINANCIAL_EDUCATION = 9


ACTION_DESCRIPTIONS = {
    RecommendationAction.REDUCE_EXPENSES: {
        'title': 'Reduce Monthly Expenses',
        'description': 'Track and cut unnecessary spending.',
        'tips': ['Review subscriptions', 'Cook at home', 'Use 50/30/20 rule', 'Find cheaper alternatives']
    },
    RecommendationAction.PAY_DOWN_DEBT: {
        'title': 'Pay Down Existing Debts',
        'description': 'Focus on reducing current debt burden.',
        'tips': ['Use avalanche method', 'Balance transfer options', 'Pay more than minimum', 'Auto-pay debts']
    },
    RecommendationAction.INCREASE_INCOME: {
        'title': 'Increase Your Income',
        'description': 'Explore opportunities to boost earnings.',
        'tips': ['Negotiate a raise', 'Start freelancing', 'Invest in skills', 'Consider overtime']
    },
    RecommendationAction.IMPROVE_CREDIT: {
        'title': 'Improve Credit Score',
        'description': 'Build and maintain strong credit history.',
        'tips': ['Pay bills on time', 'Keep utilization below 30%', 'Keep old accounts', 'Check credit report']
    },
    RecommendationAction.REDUCE_LOAN_AMOUNT: {
        'title': 'Reduce Loan Amount',
        'description': 'Request a smaller loan fitting your income.',
        'tips': ['Reassess needs', 'Save for down payment', 'Phased borrowing', 'Look for grants']
    },
    RecommendationAction.EXTEND_LOAN_TERM: {
        'title': 'Extend Loan Term',
        'description': 'Longer term reduces monthly EMI burden.',
        'tips': ['Compare interest costs', 'Keep EMI below 30% income', 'Plan early repayment', 'Fixed vs variable rates']
    },
    RecommendationAction.BUILD_SAVINGS: {
        'title': 'Build Emergency Fund',
        'description': 'Establish a financial safety net.',
        'tips': ['Save 3-6 months expenses', 'Automate savings', 'High-yield accounts', 'Redirect one expense']
    },
    RecommendationAction.CONSOLIDATE_DEBT: {
        'title': 'Consolidate Debts',
        'description': 'Combine multiple debts into one payment.',
        'tips': ['Compare consolidation rates', 'Ensure lower total cost', 'Avoid new debt', 'Credit counseling']
    },
    RecommendationAction.DIVERSIFY_INCOME: {
        'title': 'Diversify Income Sources',
        'description': 'Multiple income streams strengthen profile.',
        'tips': ['Dividend investments', 'Passive income streams', 'Develop side skills', 'Rental income']
    },
    RecommendationAction.FINANCIAL_EDUCATION: {
        'title': 'Improve Financial Literacy',
        'description': 'Better knowledge leads to better decisions.',
        'tips': ['Free online courses', 'Read finance books', 'Use planning apps', 'Consult advisor']
    }
}


class LoanRecommendationEnv:
    N_STATES = 7
    N_ACTIONS = len(RecommendationAction)

    def __init__(self):
        self.state = None
        self.user_profile = None
        self.step_count = 0
        self.max_steps = 5

    def reset(self, user_profile=None):
        self.step_count = 0
        if user_profile is None:
            self.user_profile = self._random_profile()
        else:
            self.user_profile = user_profile
        self.state = self._profile_to_state(self.user_profile)
        return self.state.copy()

    def step(self, action):
        self.step_count += 1
        action = RecommendationAction(action)
        reward = self._calculate_reward(action)
        self._apply_action_effect(action)
        done = self.step_count >= self.max_steps
        info = {'action_name': ACTION_DESCRIPTIONS[action]['title'], 'relevance': reward}
        return self.state.copy(), reward, done, info

    def _profile_to_state(self, profile):
        state = np.zeros(self.N_STATES)
        state[0] = np.clip((profile.get('credit_score', 650) - 300) / 550, 0, 1)
        dti = profile.get('existing_debts', 0) / max(profile.get('annual_income', 1), 1)
        state[1] = np.clip(1 - dti, 0, 1)
        mi = profile.get('annual_income', 0) / 12
        me = profile.get('monthly_expenses', 0)
        state[2] = np.clip((mi - me) / max(mi, 1), 0, 1)
        state[3] = np.clip(profile.get('annual_income', 0) / 200000, 0, 1)
        lr = profile.get('loan_amount', 0) / max(profile.get('annual_income', 1), 1)
        state[4] = np.clip(1 - lr / 5, 0, 1)
        emp_scores = {'Employed': 1.0, 'Self-Employed': 0.8, 'Part-Time': 0.4, 'Retired': 0.5, 'Unemployed': 0.1}
        state[5] = emp_scores.get(profile.get('employment_status', 'Employed'), 0.5)
        edu_scores = {'PhD': 1.0, 'Master': 0.8, 'Bachelor': 0.6, 'Associate': 0.4, 'High School': 0.2}
        state[6] = edu_scores.get(profile.get('education', 'Bachelor'), 0.5)
        return state

    def _calculate_reward(self, action):
        weakness_map = {
            RecommendationAction.IMPROVE_CREDIT: 0, RecommendationAction.PAY_DOWN_DEBT: 1,
            RecommendationAction.CONSOLIDATE_DEBT: 1, RecommendationAction.REDUCE_EXPENSES: 2,
            RecommendationAction.BUILD_SAVINGS: 2, RecommendationAction.INCREASE_INCOME: 3,
            RecommendationAction.DIVERSIFY_INCOME: 3, RecommendationAction.REDUCE_LOAN_AMOUNT: 4,
            RecommendationAction.EXTEND_LOAN_TERM: 4, RecommendationAction.FINANCIAL_EDUCATION: 6,
        }
        state_idx = weakness_map.get(action, 0)
        weakness = 1 - self.state[state_idx]
        reward = weakness * 2.0
        if state_idx == np.argmin(self.state):
            reward += 1.0
        if self.state[state_idx] > 0.8:
            reward -= 0.5
        reward -= 0.05
        return round(reward, 4)

    def _apply_action_effect(self, action):
        improvement = np.random.uniform(0.02, 0.08)
        effect_map = {
            RecommendationAction.IMPROVE_CREDIT: 0, RecommendationAction.PAY_DOWN_DEBT: 1,
            RecommendationAction.CONSOLIDATE_DEBT: 1, RecommendationAction.REDUCE_EXPENSES: 2,
            RecommendationAction.BUILD_SAVINGS: 2, RecommendationAction.INCREASE_INCOME: 3,
            RecommendationAction.DIVERSIFY_INCOME: 3, RecommendationAction.REDUCE_LOAN_AMOUNT: 4,
            RecommendationAction.EXTEND_LOAN_TERM: 4, RecommendationAction.FINANCIAL_EDUCATION: 6,
        }
        idx = effect_map.get(action, 0)
        self.state[idx] = min(1.0, self.state[idx] + improvement)

    def _random_profile(self):
        emp = np.random.choice(['Employed', 'Self-Employed', 'Unemployed', 'Part-Time', 'Retired'], p=[0.5, 0.2, 0.1, 0.12, 0.08])
        edu = np.random.choice(['High School', 'Associate', 'Bachelor', 'Master', 'PhD'], p=[0.2, 0.15, 0.35, 0.22, 0.08])
        income = int(np.clip(np.random.lognormal(10.8, 0.5), 10000, 300000))
        return {
            'age': int(np.random.normal(35, 10)), 'gender': np.random.choice(['Male', 'Female', 'Other']),
            'education': edu, 'employment_status': emp, 'annual_income': income,
            'monthly_expenses': int(income / 12 * np.random.uniform(0.3, 0.8)),
            'existing_debts': int(income * np.random.exponential(0.15)),
            'loan_amount': int(np.random.lognormal(10.2, 0.8)),
            'loan_term': int(np.random.choice([12, 24, 36, 48, 60, 120, 240, 360])),
            'credit_score': int(np.clip(np.random.normal(650, 100), 300, 850))
        }

    def get_action_description(self, action):
        return ACTION_DESCRIPTIONS[RecommendationAction(action)]
