from typing import Protocol
from .contracts import PresentationState
class DisplayBackend(Protocol):
    backend_id: str
    capabilities: frozenset[str]
    def present(self,state: PresentationState) -> str: ...
class RecordingDisplay:
    backend_id="recording"; capabilities=frozenset({"local_display"})
    def __init__(self): self.frames=[]
    def present(self,state): self.frames.append(state); return state.presentation_frame_id or f"presentation-{len(self.frames)}"

