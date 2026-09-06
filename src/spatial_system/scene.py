from dataclasses import dataclass, replace
from .contracts import SceneObjectState, PresentationState, InteractionEvent
from .geometry import Transform, Vec3

@dataclass
class Scene:
    objects: dict[str, SceneObjectState]
    revision: int = 0
    def __post_init__(self): self._validate()
    def _validate(self):
        for o in self.objects.values():
            if o.parent_id == o.object_id or (o.parent_id and o.parent_id not in self.objects): raise ValueError("invalid hierarchy")
    def select(self, object_id):
        if object_id not in self.objects: raise KeyError(object_id)
        self.objects={k:replace(v,selected=(k==object_id)) for k,v in self.objects.items()}; self.revision+=1
    def set_visibility(self, object_id, visible):
        if object_id not in self.objects: raise KeyError(object_id)
        self.objects={**self.objects,object_id:replace(self.objects[object_id],visible=bool(visible))}; self.revision+=1
    def reset_object(self, object_id):
        if object_id not in self.objects: raise KeyError(object_id)
        o=self.objects[object_id]; t=o.transform
        self.objects={**self.objects,object_id:replace(o,transform=Transform(t.source_space,t.target_space,Vec3(0,0,0),type(t.rotation)(1,0,0,0),Vec3(1,1,1)))}; self.revision+=1
    def apply(self,event: InteractionEvent):
        if not event.authorized or not event.target_id: return
        o=self.objects.get(event.target_id)
        if not o: raise KeyError(event.target_id)
        if event.action == "select": self.select(o.object_id); return
        t=o.transform; p=event.parameters
        if event.action == "translate": t=Transform(t.source_space,t.target_space,t.translation+Vec3(*p["delta"]),t.rotation,t.scale)
        elif event.action == "scale": t=Transform(t.source_space,t.target_space,t.translation,t.rotation,t.scale.scale(p["factor"]))
        elif event.action == "rotate": t=Transform(t.source_space,t.target_space,t.translation,p["rotation"]*t.rotation,t.scale)
        else: raise ValueError("unknown interaction action")
        self.objects={**self.objects,o.object_id:replace(o,transform=t)}; self.revision+=1
    def presentation(self,backend_id,capabilities=frozenset()): return PresentationState(self.revision,tuple(self.objects.values()),backend_id,capabilities)
