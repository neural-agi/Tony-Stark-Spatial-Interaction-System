import AppKit
import AVFoundation
import Vision
import Foundation
import Darwin
import CoreGraphics
import ImageIO

FileHandle.standardError.write(("SPATIAL_DIAGNOSTIC stage=process_start pid=\(ProcessInfo.processInfo.processIdentifier) cwd=\(FileManager.default.currentDirectoryPath) argv=\(CommandLine.arguments)\n").data(using:.utf8)!)

final class View: NSView {
    var presentation: [String: Any] = [:]
    var hands: [[[Double]]] = []
    var renderSamples:[UInt64]=[]
    override var isFlipped: Bool { true }
    override func draw(_ rect: NSRect) {
        let now=DispatchTime.now().uptimeNanoseconds; renderSamples.append(now); renderSamples=renderSamples.filter{$0+2_000_000_000 >= now}
        NSColor(calibratedRed: 0.015, green: 0.03, blue: 0.07, alpha: 1).setFill(); rect.fill()
        let objects = presentation["objects"] as? [[String: Any]] ?? []
        let object = objects.first ?? [:]
        let selected = object["selected"] as? Bool ?? false
        let t = object["translation"] as? [Double] ?? [0, 0, 0]
        let s = (object["scale"] as? [Double])?.first ?? 1
        let q = object["rotation"] as? [Double] ?? [1, 0, 0, 0]
        let qw = q.count > 0 ? q[0] : 1; let qx = q.count > 1 ? q[1] : 0; let qy = q.count > 2 ? q[2] : 0; let qz = q.count > 3 ? q[3] : 0
        var angle = CGFloat(2 * atan2(qz, qw)); if angle < 0 { angle += 2 * .pi }
        let center = CGPoint(x: bounds.midX + CGFloat(t[0]) * 180, y: bounds.midY + CGFloat(t[1]) * 180)
        let vertices: [(CGFloat, CGFloat, CGFloat)] = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        let edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        var points: [CGPoint] = []
        for (x,y,z) in vertices {
            let rx = x * cos(angle) - z * sin(angle); let rz = x * sin(angle) + z * cos(angle)
            let depth = 1 / max(0.3, 4.5 - rz)
            points.append(CGPoint(x: center.x + rx * 180 * CGFloat(s) * depth, y: center.y + y * 180 * CGFloat(s) * depth))
        }
        let color = selected ? NSColor.systemOrange : NSColor.systemTeal; color.setStroke()
        let path = NSBezierPath(); path.lineWidth = 3
        for (a,b) in edges { path.move(to: points[a]); path.line(to: points[b]) }; path.stroke()
        for hand in hands { for point in hand where point.count >= 2 {
            let p = CGPoint(x: point[0] * bounds.width, y: (1 - point[1]) * bounds.height)
            NSColor.systemPink.setFill(); NSBezierPath(ovalIn: NSRect(x:p.x-4,y:p.y-4,width:8,height:8)).fill()
        }}
        let text = selected ? "LIVE VISION • SELECTED" : "LIVE VISION • move hand to select"
        NSString(string: text).draw(at: CGPoint(x: 24, y: 24), withAttributes: [.foregroundColor: color, .font: NSFont.systemFont(ofSize: 18, weight: .bold)])
        let hud = "hands: \(presentation["hands_count"] as? Int ?? 0)/2   selected: \(selected ? "YES" : "NO")   position: (\(String(format: "%.2f", t[0])), \(String(format: "%.2f", t[1])))   scale: \(String(format: "%.2f", s))   rotation: \(String(format: "%.2f", angle)) rad   active: \(presentation["active_interaction"] as? String ?? "NONE")   camera/observation rate: \(String(format: "%.1f", presentation["frame_rate"] as? Double ?? 0)) FPS"
        // Transform the marker's local +X axis with the received object quaternion.
        // This keeps the visual diagnostic coupled to the same rotation state as the cube.
        let norm = max(1e-12, sqrt(qw*qw + qx*qx + qy*qy + qz*qz)); let w=qw/norm; let x=qx/norm; let y=qy/norm; let z=qz/norm
        let markerX = CGFloat(1 - 2 * (y*y + z*z)); let markerY = CGFloat(2 * (x*y + w*z))
        let markerEnd = CGPoint(x:center.x + markerX * 130 * CGFloat(s), y:center.y + markerY * 130 * CGFloat(s))
        let marker = NSBezierPath(); marker.move(to: center); marker.line(to: markerEnd); marker.lineWidth=6; color.setStroke(); marker.stroke()
        if presentation["rotation_trace"] != nil { diagnostic("stage=renderer rotation_quaternion=\(qw),\(qx),\(qy),\(qz) marker_endpoint=\(markerEnd.x),\(markerEnd.y)") }
        NSString(string: hud).draw(at: CGPoint(x: 24, y: 52), withAttributes: [.foregroundColor: NSColor.white, .font: NSFont.monospacedSystemFont(ofSize: 13, weight: .regular)])
        let renderRate=renderSamples.count>1 ? Double(renderSamples.count-1)*1_000_000_000.0/Double(renderSamples.last!-renderSamples.first!) : 0
        let rates="camera FPS: \(String(format: "%.1f", presentation["camera_fps"] as? Double ?? 0))   Vision FPS: \(String(format: "%.1f", presentation["vision_fps"] as? Double ?? 0))   interaction FPS: \(String(format: "%.1f", presentation["interaction_fps"] as? Double ?? 0))   render FPS: \(String(format: "%.1f", renderRate))"
        NSString(string: rates).draw(at: CGPoint(x:24,y:76), withAttributes: [.foregroundColor:NSColor.systemGreen,.font:NSFont.monospacedSystemFont(ofSize:13,weight:.regular)])
        NSString(string: "Native camera + Vision host • scene revision \(presentation["scene_revision"] as? Int ?? 0)").draw(at: CGPoint(x:24,y:bounds.height-36), withAttributes: [.foregroundColor:NSColor.systemBlue,.font:NSFont.systemFont(ofSize:13)])
    }
}

let app = NSApplication.shared; app.setActivationPolicy(.regular)
let window = NSWindow(contentRect:NSRect(x:0,y:0,width:1000,height:700),styleMask:[.titled,.closable,.resizable],backing:.buffered,defer:false)
window.title = "Tony Stark Spatial Interaction"; let view=View(frame:window.contentView!.bounds); view.autoresizingMask=[.width,.height]; window.contentView=view; window.center(); window.makeKeyAndOrderFront(nil); app.activate(ignoringOtherApps:true)

let writeLock = NSLock()
let diagnosticLock = NSLock()
func diagnostic(_ message:String) { diagnosticLock.lock(); FileHandle.standardError.write(("SPATIAL_DIAGNOSTIC " + message + "\n").data(using:.utf8)!); diagnosticLock.unlock() }
func emit(_ value: [String: Any]) { guard let data=try? JSONSerialization.data(withJSONObject:value), let line=String(data:data,encoding:.utf8) else{return}; writeLock.lock(); FileHandle.standardOutput.write((line+"\n").data(using:.utf8)!); writeLock.unlock() }
func error(_ message:String)->Never { emit(["type":"error","message":message]); exit(1) }
let auth=AVCaptureDevice.authorizationStatus(for:.video); diagnostic("stage=authorization status=\(auth) bundle=\(Bundle.main.bundleIdentifier ?? "<nil>")"); emit(["type":"status","status":"authorization_\(auth == .authorized ? "authorized" : auth == .notDetermined ? "notDetermined" : "denied")","bundle_id":Bundle.main.bundleIdentifier ?? ""])
if auth == .notDetermined { let sem=DispatchSemaphore(value:0); AVCaptureDevice.requestAccess(for:.video){ _ in sem.signal() }; sem.wait() }
guard AVCaptureDevice.authorizationStatus(for:.video) == .authorized else { error("camera authorization denied") }
guard let device=AVCaptureDevice.default(for:.video) else { diagnostic("stage=device_discovery result=missing"); error("no video device") }
diagnostic("stage=device_discovery result=found name=\(device.localizedName) id=\(device.uniqueID)")
let session=AVCaptureSession(); session.beginConfiguration(); session.sessionPreset = .high
guard let input=try? AVCaptureDeviceInput(device:device), session.canAddInput(input) else { error("camera input unavailable") }; session.addInput(input)
let output=AVCaptureVideoDataOutput(); output.videoSettings=[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA]; output.alwaysDiscardsLateVideoFrames=true
guard session.canAddOutput(output) else { error("camera output unavailable") }; session.addOutput(output); session.commitConfiguration()
let activeDimensions=CMVideoFormatDescriptionGetDimensions(device.activeFormat.formatDescription)
emit(["type":"status","status":"camera_ready","device_id":device.uniqueID,"device_name":device.localizedName,"width":activeDimensions.width,"height":activeDimensions.height,"pixel_format":"BGRA8","timestamp_domain":"avfoundation-media-time","timestamp_origin":"CMSampleBuffer presentation timestamp" ])
let request=VNDetectHumanHandPoseRequest(); request.maximumHandCount=2
final class Delegate:NSObject,AVCaptureVideoDataOutputSampleBufferDelegate {
    let deviceID:String; let request:VNDetectHumanHandPoseRequest
    var frameCount=0; var firstChecksum:UInt64?; var sampleSaved=false
    var cameraSamples:[UInt64]=[]; var visionSamples:[UInt64]=[]
    func rate(_ samples:[UInt64])->Double { samples.count>1 ? Double(samples.count-1)*1_000_000_000.0/Double(samples.last!-samples.first!) : 0 }
    init(deviceID:String,request:VNDetectHumanHandPoseRequest){self.deviceID=deviceID;self.request=request}
    func captureOutput(_ output:AVCaptureOutput,didOutput sampleBuffer:CMSampleBuffer,from connection:AVCaptureConnection){
        let receipt=DispatchTime.now().uptimeNanoseconds; cameraSamples.append(receipt); cameraSamples=cameraSamples.filter{$0+2_000_000_000 >= receipt}
        guard let pixel=CMSampleBufferGetImageBuffer(sampleBuffer) else { diagnostic("stage=delegate result=no_pixel_buffer"); return }
        CVPixelBufferLockBaseAddress(pixel,.readOnly); defer { CVPixelBufferUnlockBaseAddress(pixel,.readOnly) }
        guard let base=CVPixelBufferGetBaseAddress(pixel) else { diagnostic("stage=delegate result=unreadable_buffer"); return }
        let bytes=CVPixelBufferGetDataSize(pixel); let raw=base.assumingMemoryBound(to:UInt8.self); var checksum:UInt64=0
        for i in stride(from:0,to:bytes,by:max(1,bytes/4096)){ checksum = (checksum &* 131) &+ UInt64(raw[i]) }
        if firstChecksum == nil { firstChecksum=checksum } else if checksum != firstChecksum { diagnostic("stage=delegate image_data=changing") }
        if !sampleSaved { saveSample(pixel); sampleSaved=true }
        let pts=CMSampleBufferGetPresentationTimeStamp(sampleBuffer); diagnostic("stage=delegate frame=\(sequence) dimensions=\(CVPixelBufferGetWidth(pixel))x\(CVPixelBufferGetHeight(pixel)) format=\(CVPixelBufferGetPixelFormatType(pixel)) stride=\(CVPixelBufferGetBytesPerRow(pixel)) bytes=\(bytes) checksum=\(checksum) timestamp=\(pts.value)/\(pts.timescale) locked_readable=true")
        let handler=VNImageRequestHandler(cvPixelBuffer:pixel,options:[:]); do { try handler.perform([request]); visionSamples.append(DispatchTime.now().uptimeNanoseconds); visionSamples=visionSamples.filter{$0+2_000_000_000 >= receipt}; diagnostic("stage=vision frame=\(sequence) completed=true error=none revision=\(request.revision) max_hands=\(request.maximumHandCount) results=\(request.results?.count ?? 0)") } catch { diagnostic("stage=vision frame=\(sequence) completed=false error=\(error) revision=\(request.revision)") }; var hands:[[String:Any]]=[]
        for (i,hand) in (request.results ?? []).enumerated(){ guard let points=try? hand.recognizedPoints(.all) else{continue}; var ls:[[Double]]=[]
            for name in [VNHumanHandPoseObservation.JointName.wrist,.thumbCMC,.thumbMP,.thumbIP,.thumbTip,.indexMCP,.indexPIP,.indexDIP,.indexTip,.middleMCP,.middlePIP,.middleDIP,.middleTip,.ringMCP,.ringPIP,.ringDIP,.ringTip,.littleMCP,.littlePIP,.littleDIP,.littleTip] { let p=points[name]; ls.append([p?.location.x ?? 0,p?.location.y ?? 0,0]) }
            diagnostic("stage=vision frame=\(sequence) hand=\(i) points=\(ls.count) confidence=\(hand.confidence)"); hands.append(["hand_id":"vision-\(i)","landmarks":ls,"confidence":hand.confidence])
        }
        let nsDouble=Double(pts.value)/Double(pts.timescale)*1_000_000_000.0; let ns=Int64(nsDouble)
        emit(["type":"observation","frame_id":"frame-\(sequence)","source_id":deviceID,"sequence":sequence,"timestamp_ns":ns,"timestamp_domain":"avfoundation-media-time","timestamp_origin":"CMSampleBuffer presentation timestamp","width":CVPixelBufferGetWidth(pixel),"height":CVPixelBufferGetHeight(pixel),"pixel_format":"BGRA8","orientation":"native","mirrored":false,"hands":hands,"validity":"valid","tracking_status":hands.isEmpty ? "no_hand" : "observed","camera_fps":rate(cameraSamples),"vision_fps":rate(visionSamples)]); diagnostic("stage=ipc observation_written frame=\(sequence) hands=\(hands.count)"); sequence+=1
    }
    func saveSample(_ pixel:CVPixelBuffer) { let width=CVPixelBufferGetWidth(pixel), height=CVPixelBufferGetHeight(pixel), stride=CVPixelBufferGetBytesPerRow(pixel); guard let base=CVPixelBufferGetBaseAddress(pixel), let provider=CGDataProvider(data:Data(bytes:base,count:stride*height) as CFData), let image=CGImage(width:width,height:height,bitsPerComponent:8,bitsPerPixel:32,bytesPerRow:stride,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGBitmapInfo(rawValue:CGImageAlphaInfo.premultipliedFirst.rawValue|CGBitmapInfo.byteOrder32Little.rawValue),provider:provider,decode:nil,shouldInterpolate:false,intent:.defaultIntent), let dest=CGImageDestinationCreateWithURL(URL(fileURLWithPath:"/tmp/spatial_vision_sample.png") as CFURL, "public.png" as CFString, 1, nil) else { diagnostic("stage=sample_save result=failed"); return }; CGImageDestinationAddImage(dest,image,nil); diagnostic("stage=sample_save result=\(CGImageDestinationFinalize(dest)) path=/tmp/spatial_vision_sample.png") }
    var sequence:UInt64=0
}
let delegate=Delegate(deviceID:device.uniqueID,request:request); let queue=DispatchQueue(label:"spatial.camera"); output.setSampleBufferDelegate(delegate,queue:queue); if let connection=output.connection(with:.video) { diagnostic("stage=video_connection mirrored=\(connection.isVideoMirrored) orientation_supported=\(connection.isVideoOrientationSupported) orientation=\(connection.videoOrientation.rawValue)") }; diagnostic("stage=vision_configuration revision=\(request.revision) supported_revisions=\(VNDetectHumanHandPoseRequest.supportedRevisions) max_hands=\(request.maximumHandCount)"); session.startRunning(); diagnostic("stage=session_start running=\(session.isRunning)")
DispatchQueue.global(qos:.userInitiated).async { while let line=readLine(), let data=line.data(using:.utf8), let payload=(try? JSONSerialization.jsonObject(with:data)) as? [String:Any] { DispatchQueue.main.async { if payload["type"] as? String == "presentation" { view.presentation=payload; view.hands=payload["hands"] as? [[[Double]]] ?? []; view.needsDisplay=true } } }; DispatchQueue.main.async { session.stopRunning(); app.terminate(nil) } }
signal(SIGTERM,SIG_IGN); let term=DispatchSource.makeSignalSource(signal:SIGTERM,queue:.main); term.setEventHandler{session.stopRunning();app.terminate(nil)}; term.resume(); app.run()
