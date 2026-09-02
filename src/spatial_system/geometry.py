from __future__ import annotations
from dataclasses import dataclass
import math

SPACES = frozenset({"image", "camera", "hand_local", "world", "object_local"})
@dataclass(frozen=True)
class Vec3:
    x: float; y: float; z: float
    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.x,self.y,self.z)): raise ValueError("non-finite vector")
    def __add__(self, o): return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def scale(self, s): return Vec3(self.x*s, self.y*s, self.z*s)

@dataclass(frozen=True)
class Quaternion:
    w: float; x: float; y: float; z: float
    def normalized(self):
        n=math.sqrt(self.w*self.w+self.x*self.x+self.y*self.y+self.z*self.z)
        if n <= 1e-12: raise ValueError("zero quaternion")
        return Quaternion(self.w/n,self.x/n,self.y/n,self.z/n)
    def __mul__(self,o):
        return Quaternion(self.w*o.w-self.x*o.x-self.y*o.y-self.z*o.z,self.w*o.x+self.x*o.w+self.y*o.z-self.z*o.y,self.w*o.y-self.x*o.z+self.y*o.w+self.z*o.x,self.w*o.z+self.x*o.y-self.y*o.x+self.z*o.w)
    def rotate(self, p):
        q=self.normalized(); v=Quaternion(0,p.x,p.y,p.z); r=q*v*Quaternion(q.w,-q.x,-q.y,-q.z)
        return Vec3(r.x,r.y,r.z)

@dataclass(frozen=True)
class Transform:
    source_space: str; target_space: str; translation: Vec3 = Vec3(0,0,0)
    rotation: Quaternion = Quaternion(1,0,0,0); scale: Vec3 = Vec3(1,1,1)
    def __post_init__(self):
        if self.source_space not in SPACES or self.target_space not in SPACES: raise ValueError("unknown coordinate space")
        if min(self.scale.x,self.scale.y,self.scale.z) == 0: raise ValueError("zero scale")
        if self.rotation != Quaternion(1,0,0,0) and not (self.scale.x == self.scale.y == self.scale.z):
            raise NotImplementedError("non-uniform scale with rotation is unsupported by the TRS representation")
    @staticmethod
    def identity(space): return Transform(space, space)
    def apply(self, p): return self.rotation.rotate(Vec3(p.x*self.scale.x,p.y*self.scale.y,p.z*self.scale.z)) + self.translation
    def then(self, other):
        if self.target_space != other.source_space: raise ValueError("transform space mismatch")
        rotation = other.rotation*self.rotation
        scale = Vec3(self.scale.x*other.scale.x,self.scale.y*other.scale.y,self.scale.z*other.scale.z)
        return Transform(self.source_space,other.target_space, other.apply(self.translation), rotation, scale)
    def inverse(self):
        if self.rotation != Quaternion(1,0,0,0) and not (self.scale.x == self.scale.y == self.scale.z):
            raise NotImplementedError("non-uniform scale with rotation is unsupported by the TRS representation")
        q=self.rotation.normalized(); qi=Quaternion(q.w,-q.x,-q.y,-q.z)
        inv_scale=Vec3(1/self.scale.x,1/self.scale.y,1/self.scale.z)
        return Transform(self.target_space,self.source_space,qi.rotate(self.translation.scale(-1)).scale(1/self.scale.x if self.scale.x == self.scale.y == self.scale.z else 1),qi,inv_scale)
