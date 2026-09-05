"""Hardware-dependent acquisition smoke entry point; never used by normal CI."""
import argparse, platform, time
from spatial_system.acquisition import CameraConfiguration, MacOSAVFoundationSource, AcquisitionError
from spatial_system.instrumentation import BoundedBuffer
def main():
    p=argparse.ArgumentParser(); p.add_argument("--duration",type=float,default=5); a=p.parse_args()
    config=CameraConfiguration("builtin-webcam","avfoundation",640,480,"BGRA",None,"default")
    try: source=MacOSAVFoundationSource(config)
    except AcquisitionError as e: print({"status":"unavailable","code":e.code.value,"message":str(e),"platform":platform.platform()}); return 2
    frames=0; error=None; started=time.monotonic()
    try:
        while time.monotonic()-started < a.duration:
            source.read(); frames += 1
    except AcquisitionError as e: error={"code":e.code.value,"message":str(e)}
    finally: source.close()
    if frames == 0: print({"status":"failed","reason":"no real frames delivered","error":error}); return 4
    print({"status":"REAL_HARDWARE","backend":"avfoundation","frames":frames,"error":error}); return 0
if __name__=="__main__": raise SystemExit(main())
