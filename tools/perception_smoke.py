"""Real RawFrame-to-perception smoke test; macOS camera required."""
import argparse, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from spatial_system.acquisition import CameraConfiguration, MacOSAVFoundationSource
from spatial_system.perception import VisionPerceptionAdapter
def main():
    p=argparse.ArgumentParser(); p.add_argument("--duration",type=float,default=1); a=p.parse_args()
    source=MacOSAVFoundationSource(CameraConfiguration("builtin-webcam","avfoundation",640,480,"BGRA",None,"high-default")); adapter=VisionPerceptionAdapter(); count=0
    try:
        import time; end=time.monotonic()+a.duration
        while time.monotonic()<end:
            o=adapter.observe(source.read()); count+=1
            if o.validity.value != "valid": raise RuntimeError("invalid observation")
        print({"status":"REAL_HARDWARE","frames":count,"observations":count,"adapter":adapter.adapter_id,"latency_samples":len(adapter.latency_ns)})
    finally: adapter.close(); source.close()
if __name__=="__main__": main()
