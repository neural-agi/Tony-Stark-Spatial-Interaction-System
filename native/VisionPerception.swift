import Foundation
import Vision
import CoreVideo

func fail(_ message: String) -> Never { FileHandle.standardError.write(("PERCEPTION_ERROR " + message + "\n").data(using: .utf8)!); exit(1) }
let request = VNDetectHumanHandPoseRequest()
let input = FileHandle.standardInput
while true {
    let line = input.readData(ofLength: 1)
    if line.isEmpty { break }
    var headerData = line
    while headerData.last != 10 { let b=input.readData(ofLength: 1); if b.isEmpty { fail("truncated header") }; headerData.append(b) }
    guard let header = (try? JSONSerialization.jsonObject(with: headerData)) as? [String:Any], let width=header["width"] as? Int, let height=header["height"] as? Int, let payloadSize=header["payload_size"] as? Int else { fail("invalid frame header") }
    let lengthData=input.readData(ofLength: 4); guard lengthData.count == 4 else { fail("truncated length") }
    let size=lengthData.withUnsafeBytes { $0.load(as: UInt32.self) }; guard Int(size)==payloadSize else { fail("payload length mismatch") }
    let payload=input.readData(ofLength: Int(size)); guard payload.count == Int(size) else { fail("truncated payload") }
    var observations:[[String:Any]]=[]
    payload.withUnsafeBytes { raw in
        var buffer: CVPixelBuffer?
        let status=CVPixelBufferCreateWithBytes(nil,width,height,kCVPixelFormatType_32BGRA,UnsafeMutableRawPointer(mutating: raw.baseAddress!),width*4,nil,nil,nil,&buffer)
        guard status == kCVReturnSuccess, let pixel=buffer else { return }
        let handler=VNImageRequestHandler(cvPixelBuffer: pixel, options: [:]); try? handler.perform([request])
        for (index, hand) in (request.results ?? []).enumerated() {
            let points=try? hand.recognizedPoints(.all); var landmarks:[[Double]]=[]
            for name in [VNHumanHandPoseObservation.JointName.wrist,.thumbCMC,.thumbMP,.thumbIP,.thumbTip,.indexMCP,.indexPIP,.indexDIP,.indexTip,.middleMCP,.middlePIP,.middleDIP,.middleTip,.ringMCP,.ringPIP,.ringDIP,.ringTip,.littleMCP,.littlePIP,.littleDIP,.littleTip] { let p=points?[name]; landmarks.append([p?.location.x ?? 0,p?.location.y ?? 0,0]) }
            observations.append(["hand_id":"vision-\(index)","landmarks":landmarks,"confidence":hand.confidence])
        }
    }
    let result:[String:Any]=["frame_id":header["frame_id"] ?? "","source_id":header["source_id"] ?? "","timestamp_ns":header["timestamp_ns"] ?? 0,"timestamp_domain":header["timestamp_domain"] ?? "","timestamp_origin":header["timestamp_origin"] ?? "","image_size":[width,height],"hands":observations,"tracking_status":observations.isEmpty ? "no_hand" : "observed"]
    let data=try! JSONSerialization.data(withJSONObject: result); FileHandle.standardOutput.write(data); FileHandle.standardOutput.write(Data([10]))
}
