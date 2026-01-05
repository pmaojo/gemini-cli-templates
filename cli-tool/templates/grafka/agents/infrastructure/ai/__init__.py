"""AI infrastructure - SLM, AIR, training"""
# Import only what's needed, avoid Lightning dependency
from .slm import TrainableSLM
from .air import get_air, RewardSignal, AutomaticIntermediateRewarding as AIRSystem

__all__ = ['TrainableSLM', 'get_air', 'RewardSignal', 'AIRSystem']
