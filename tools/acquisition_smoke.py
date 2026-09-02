"""Hardware-dependent acquisition smoke entry point; never used by normal CI."""
import argparse, platform
from spatial_system.acquisition import CameraConfiguration, MacOSAVFoundationSource, AcquisitionError
def main():
    p=argparse.ArgumentParser(); p.add_argument("--duration",type=float,default=5); a=p.parse_args()
    config=CameraConfiguration("builtin-webcam","avfoundation",640,480,"BGRA",None,"default")
    try: source=MacOSAVFoundationSource(config)
    except AcquisitionError as e: print({"status":"unavailable","code":e.code.value,"message":str(e),"platform":platform.platform()}); return 2
    source.close(); print({"status":"not-started","reason":"platform adapter requires capture integration"}); return 3
if __name__=="__main__": raise SystemExit(main())
