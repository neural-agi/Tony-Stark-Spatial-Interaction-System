import AVFoundation
import Foundation
import Darwin

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
        line.append("\n"); output.write(line.data(using: .utf8)!); var length = UInt32(data.count).littleEndian; output.write(Data(bytes: &length, count: 4)); output.write(data); sequence += 1
    }
}

let requested = CommandLine.arguments.count > 1 ? CommandLine.arguments[1].data(using: .utf8)! : Data("{}".utf8)
let config = (try? JSONSerialization.jsonObject(with: requested) as? [String:Any]) ?? [:]
guard AVCaptureDevice.authorizationStatus(for: .video) != .denied else { exit(20) }
let semaphore = DispatchSemaphore(value: 0)
if AVCaptureDevice.authorizationStatus(for: .video) == .notDetermined { AVCaptureDevice.requestAccess(for: .video) { _ in semaphore.signal() }; semaphore.wait() }
guard let device = AVCaptureDevice.default(for: .video) else { exit(21) }
let session = AVCaptureSession(); session.beginConfiguration(); session.sessionPreset = .high
guard let input = try? AVCaptureDeviceInput(device: device), session.canAddInput(input) else { exit(22) }; session.addInput(input)
let output = AVCaptureVideoDataOutput(); output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA]; output.alwaysDiscardsLateVideoFrames = true
guard session.canAddOutput(output) else { exit(23) }; session.addOutput(output); session.commitConfiguration()
let delegate = Delegate(sourceID: device.uniqueID); let queue = DispatchQueue(label: "camera.capture")
output.setSampleBufferDelegate(delegate, queue: queue); session.startRunning(); RunLoop.current.run()
