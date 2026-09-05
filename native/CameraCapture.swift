import AVFoundation
import AppKit
import Foundation
import Darwin

func fail(_ code: Int32, _ message: String) -> Never {
    FileHandle.standardError.write(("CAMERA_ERROR code=\(code) message=\(message)\n").data(using: .utf8)!)
    exit(code)
}

func diagnostic(_ message: String) {
    FileHandle.standardError.write(("CAMERA_DIAGNOSTIC " + message + "\n").data(using: .utf8)!)
}

func authorizationName(_ status: AVAuthorizationStatus) -> String {
    switch status {
    case .notDetermined: return "notDetermined"
    case .restricted: return "restricted"
    case .denied: return "denied"
    case .authorized: return "authorized"
    @unknown default: return "unknown"
    }
}

// Native helper protocol: one UTF-8 JSON header line, then uint32 little-endian
// payload length and owned BGRA bytes. Stdout is reserved for this protocol.
final class Delegate: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    let output = FileHandle.standardOutput
    var sequence: UInt64 = 0
    let sourceID: String
    init(sourceID: String) { self.sourceID = sourceID }
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let image = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        CVPixelBufferLockBaseAddress(image, .readOnly); defer { CVPixelBufferUnlockBaseAddress(image, .readOnly) }
        guard let base = CVPixelBufferGetBaseAddress(image) else { return }
        let bytes = CVPixelBufferGetDataSize(image); let data = Data(bytes: base, count: bytes)
        let pts = CMSampleBufferGetPresentationTimeStamp(sampleBuffer)
        let ns = Int64((Double(pts.value) / Double(pts.timescale)) * 1_000_000_000.0)
        let header: [String:Any] = ["frame_id":"frame-\(sequence)","source_id":sourceID,"sequence":sequence,"timestamp_ns":ns,"timestamp_domain":"avfoundation-media-time","timestamp_origin":"CMSampleBuffer presentation timestamp","width":CVPixelBufferGetWidth(image),"height":CVPixelBufferGetHeight(image),"pixel_format":"BGRA8","orientation":"native","mirrored":false,"bytes_per_row":CVPixelBufferGetBytesPerRow(image),"payload_size":bytes]
        guard let json = try? JSONSerialization.data(withJSONObject: header), var line = String(data: json, encoding: .utf8) else { return }
        line.append("\n"); self.output.write(line.data(using: .utf8)!); var length = UInt32(data.count).littleEndian; self.output.write(Data(bytes: &length, count: 4)); self.output.write(data); sequence += 1
    }
}

let requested = CommandLine.arguments.count > 1 ? CommandLine.arguments[1].data(using: .utf8)! : Data("{}".utf8)
let config = (try? JSONSerialization.jsonObject(with: requested) as? [String:Any]) ?? [:]
if CommandLine.arguments.count > 1, CommandLine.arguments[1] == "--capabilities" {
    guard let device = AVCaptureDevice.default(for: .video) else { fail(21, "no default video device available") }
    var formats: [[String:Any]] = []
    for format in device.formats {
        let desc = format.formatDescription
        let dimensions = CMVideoFormatDescriptionGetDimensions(desc)
        let ranges = format.videoSupportedFrameRateRanges.map { ["min": $0.minFrameRate, "max": $0.maxFrameRate] }
        formats.append(["dimensions": ["width": dimensions.width, "height": dimensions.height], "media_subtype": CMFormatDescriptionGetMediaSubType(desc), "frame_rate_ranges": ranges])
    }
    let result: [String:Any] = ["device_unique_id": device.uniqueID, "device_name": device.localizedName, "formats": formats]
    let data = try! JSONSerialization.data(withJSONObject: result); FileHandle.standardOutput.write(data); FileHandle.standardOutput.write(Data([10])); exit(0)
}
let bundle = Bundle.main
let authorization = AVCaptureDevice.authorizationStatus(for: .video)
diagnostic("stage=authorization status=\(authorizationName(authorization)) bundle_id=\(bundle.bundleIdentifier ?? "<nil>") executable=\(bundle.executableURL?.path ?? "<nil>") pid=\(ProcessInfo.processInfo.processIdentifier) cwd=\(FileManager.default.currentDirectoryPath)")
guard authorization != .denied else { fail(20, "camera authorization denied") }
guard authorization != .restricted else { fail(20, "camera authorization restricted") }
let semaphore = DispatchSemaphore(value: 0)
if authorization == .notDetermined {
    AVCaptureDevice.requestAccess(for: .video) { granted in
        diagnostic("stage=requestAccess result=\(granted ? "authorized" : "denied")")
        semaphore.signal()
    }
    semaphore.wait()
}
diagnostic("stage=authorization_complete status=\(authorizationName(AVCaptureDevice.authorizationStatus(for: .video)))")
guard AVCaptureDevice.authorizationStatus(for: .video) == .authorized else { fail(20, "camera authorization not granted") }
guard let device = AVCaptureDevice.default(for: .video) else { diagnostic("stage=device_discovery result=missing"); fail(21, "no default video device available") }
diagnostic("stage=device_discovery result=found name=\(device.localizedName) model=\(device.modelID) unique_id=\(device.uniqueID)")
let session = AVCaptureSession(); session.beginConfiguration(); session.sessionPreset = .high
guard let input = try? AVCaptureDeviceInput(device: device) else { diagnostic("stage=input_creation result=failed"); fail(22, "cannot create camera input") }
guard session.canAddInput(input) else { diagnostic("stage=input_configuration result=cannot_add"); fail(22, "cannot add camera input") }; session.addInput(input)
let output = AVCaptureVideoDataOutput(); output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA]; output.alwaysDiscardsLateVideoFrames = true
guard session.canAddOutput(output) else { diagnostic("stage=output_configuration result=cannot_add"); fail(23, "cannot add video output") }; session.addOutput(output); session.commitConfiguration()
if let fps = config["requested_fps"] as? NSNumber, fps.doubleValue > 0 {
    let duration = CMTime(value: 1, timescale: CMTimeScale(fps.intValue))
    do {
        try device.lockForConfiguration()
        device.activeVideoMinFrameDuration = duration
        device.activeVideoMaxFrameDuration = duration
        device.unlockForConfiguration()
        diagnostic("stage=frame_duration result=requested fps=\(fps.doubleValue)")
    } catch { diagnostic("stage=frame_duration result=rejected fps=\(fps.doubleValue) reason=\(error)") }
}
let activeDescription = device.activeFormat.formatDescription
let activeDimensions = CMVideoFormatDescriptionGetDimensions(activeDescription)
let activeRanges = device.activeFormat.videoSupportedFrameRateRanges.map { "\($0.minFrameRate)-\($0.maxFrameRate)" }.joined(separator: ",")
diagnostic("stage=session_configuration result=committed preset=high active_dimensions=\(activeDimensions.width)x\(activeDimensions.height) active_ranges=\(activeRanges) min_frame_duration=\(device.activeVideoMinFrameDuration.seconds) max_frame_duration=\(device.activeVideoMaxFrameDuration.seconds)")
let delegate = Delegate(sourceID: device.uniqueID); let queue = DispatchQueue(label: "camera.capture")
output.setSampleBufferDelegate(delegate, queue: queue)

// Keep the capture session inside a real macOS application host for the full
// lifetime of the acquisition process. Stdout remains the frame protocol;
// AppKit is used only for process lifecycle and event delivery.
let application = NSApplication.shared
application.setActivationPolicy(.prohibited)
signal(SIGTERM, SIG_IGN)
signal(SIGINT, SIG_IGN)
let termination = DispatchSource.makeSignalSource(signal: SIGTERM, queue: .main)
termination.setEventHandler {
    diagnostic("stage=shutdown result=requested")
    output.setSampleBufferDelegate(nil, queue: nil)
    session.stopRunning()
    diagnostic("stage=shutdown result=stopped")
    application.terminate(nil)
}
termination.resume()
let interrupt = DispatchSource.makeSignalSource(signal: SIGINT, queue: .main)
interrupt.setEventHandler {
    diagnostic("stage=shutdown result=interrupted")
    output.setSampleBufferDelegate(nil, queue: nil)
    session.stopRunning()
    application.terminate(nil)
}
interrupt.resume()

session.startRunning()
diagnostic("stage=session_start result=started running=\(session.isRunning) app_host=NSApplication")
application.run()
