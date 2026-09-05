import AppKit
import Foundation

struct CubeState {
    var selected = false
    var x: CGFloat = 0
    var y: CGFloat = 0
    var scale: CGFloat = 1
    var angle: CGFloat = 0
}

final class DemoView: NSView {
    var state = CubeState()
    var sceneRevision = 0

    override var isFlipped: Bool { true }

    override func draw(_ dirtyRect: NSRect) {
        NSColor(calibratedRed: 0.02, green: 0.06, blue: 0.12, alpha: 1).setFill()
        dirtyRect.fill()
        let vertices: [(CGFloat, CGFloat, CGFloat)] = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        let edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        let center = CGPoint(x: bounds.midX + state.x, y: bounds.midY + state.y)
        var projected = [CGPoint]()
        for (x, y, z) in vertices {
            let rx = x * cos(state.angle) - z * sin(state.angle)
            let rz = x * sin(state.angle) + z * cos(state.angle)
            let depth = 1 / max(0.3, 4.5 - rz)
            projected.append(CGPoint(x: center.x + rx * 180 * state.scale * depth, y: center.y + y * 180 * state.scale * depth))
        }
        let color = state.selected ? NSColor.systemOrange : NSColor.systemTeal
        color.setStroke()
        let path = NSBezierPath()
        path.lineWidth = 3
        for (a, b) in edges { path.move(to: projected[a]); path.line(to: projected[b]) }
        path.stroke()
        let title = state.selected ? "SELECTED • Python Scene / InteractionState" : "Python PresentationState"
        let attrs: [NSAttributedString.Key: Any] = [.foregroundColor: color, .font: NSFont.systemFont(ofSize: 18, weight: .bold)]
        NSString(string: title).draw(at: CGPoint(x: 24, y: 24), withAttributes: attrs)
        NSString(string: "AppKit display backend • scene revision \(sceneRevision)").draw(at: CGPoint(x: 24, y: bounds.height - 36), withAttributes: [.foregroundColor: NSColor.systemBlue, .font: NSFont.systemFont(ofSize: 13)])
    }

    func apply(_ payload: [String: Any]) {
        sceneRevision = payload["scene_revision"] as? Int ?? sceneRevision
        guard let objects = payload["objects"] as? [[String: Any]], let object = objects.first else { return }
        state.selected = object["selected"] as? Bool ?? false
        if let t = object["translation"] as? [Double], t.count == 3 { state.x=CGFloat(t[0])*180; state.y=CGFloat(t[1])*180 }
        if let s = object["scale"] as? [Double], let first=s.first { state.scale=CGFloat(first) }
        if let q = object["rotation"] as? [Double], q.count == 4 { state.angle=CGFloat(2*atan2(q[2],q[0])) }
        needsDisplay = true
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 900, height: 650), styleMask: [.titled, .closable, .resizable], backing: .buffered, defer: false)
window.title = "Tony Stark Spatial Interaction — Native Synthetic Demo"
let view = DemoView(frame: window.contentView!.bounds)
view.autoresizingMask = [.width, .height]
window.contentView = view
window.center()
window.makeKeyAndOrderFront(nil)
app.activate(ignoringOtherApps: true)
DispatchQueue.global(qos: .userInitiated).async {
    while let line = readLine(), let data = line.data(using: .utf8), let payload = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] {
        DispatchQueue.main.async { view.apply(payload) }
    }
    DispatchQueue.main.async { app.terminate(nil) }
}
app.run()
