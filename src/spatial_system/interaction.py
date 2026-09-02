from enum import Enum
from .contracts import InteractionEvent

class HandMode(str,Enum): NONE="none"; ONE="one"; TWO="two"; LOST="lost"
class InteractionState:
    def __init__(self): self.mode=HandMode.NONE; self.selected_id=None
    def update(self, hand_count, tracking_valid=True):
        if not tracking_valid: self.mode=HandMode.LOST
        elif hand_count==0: self.mode=HandMode.NONE
        elif hand_count==1: self.mode=HandMode.ONE
        elif hand_count==2: self.mode=HandMode.TWO
        else: raise ValueError("unsupported hand count")
    def event(self, action,target_id,time,parameters,confidence=1.0,authorized=True,state_id=None):
        if action not in {"select","translate","rotate","scale"}: raise ValueError("unsupported action")
        return InteractionEvent(f"event-{time.timestamp_ns}-{action}",action,target_id,dict(parameters),time,state_id,confidence,authorized)

