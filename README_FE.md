# 🎨 Hướng dẫn tích hợp Frontend (Web / App) với LiveKit Cloud (V5)

Tài liệu này hướng dẫn chi tiết cách kết nối và hiển thị luồng video Edge AI (vẽ YOLO) từ LiveKit Cloud lên giao diện Web (React / Vue / HTML) hoặc Mobile App (Flutter / React Native) của người dùng cuối.

---

## 🗺️ Luồng hoạt động (Token & Connection Flow)

Hạ tầng LiveKit Cloud sử dụng cơ chế xác thực JWT bảo mật. Quy trình thiết lập kết nối từ phía Frontend như sau:

```
[Browser / Mobile App]                  [Cloud Signaling Server]                 [LiveKit Cloud]
         │                                         │                                    │
         ├─────── 1. Yêu cầu cấp Token ───────────>│                                    │
         │         (Gửi camera_id & Client JWT)    │                                    │
         │                                         │                                    │
         │<────── 2. Trả về Token truy cập ────────┤                                    │
         │         (Token chứa quyền join room)    │                                    │
         │                                                                              │
         ├────────────────────── 3. Kết nối WebRTC trực tiếp ──────────────────────────>│
         │                          (Sử dụng Token vừa nhận)                             │
         │                                                                              │
         │<===================== 4. Nhận Video Track từ Camera =========================┤
```

---

## 🔌 API Endpoint từ Cloud Server

* **Endpoint:** `POST /api/cameras/{camera_id}/token`
* **Headers:** `Content-Type: application/json` (Kèm theo Authorization Header nếu hệ thống của bạn yêu cầu đăng nhập)
* **Body Request:**
  ```json
  {
    "identity": "web_viewer_random123",
    "room_name": "mylongai"
  }
  ```
* **Body Response (200 OK):**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWRlbyI6ey...",
    "server_url": "wss://mylongai-2154szvq.livekit.cloud",
    "room_name": "mylongai"
  }
  ```

---

## 💻 1. Mã nguồn tích hợp cho Web (React / Next.js) - *Khuyên dùng*

Cài đặt thư viện Client SDK chính thức của LiveKit:
```bash
npm install livekit-client
```

### React Hook / Component mẫu:
```jsx
import React, { useEffect, useRef, useState } from 'react';
import { Room, RoomEvent } from 'livekit-client';

export const CameraViewer = ({ cloudServerUrl, cameraId, roomName, userJwt }) => {
    const videoRef = useRef(null);
    const [status, setStatus] = useState('OFFLINE'); // OFFLINE, CONNECTING, LIVE, ERROR
    const [room, setRoom] = useState(null);

    const startStream = async () => {
        setStatus('CONNECTING');
        try {
            // 1. Gọi API của Cloud Server để lấy Token truy cập phòng
            const response = await fetch(`${cloudServerUrl}/api/cameras/${cameraId}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userJwt}`
                },
                body: JSON.stringify({
                    identity: `viewer_${Math.random().toString(36).substring(7)}`,
                    room_name: roomName
                })
            });

            if (!response.ok) throw new Error("Lỗi cấp Token từ máy chủ");
            const { token, server_url } = await response.json();

            // 2. Khởi tạo Room LiveKit với các cấu hình tối ưu băng thông
            const lkRoom = new Room({
                adaptiveStream: true, // Tự động bóp độ phân giải khi mạng yếu
                dynacast: true        // Tiết kiệm băng thông gửi từ camera
            });

            // 3. Đăng ký sự kiện lắng nghe Video Track
            lkRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
                if (track.kind === 'video' && videoRef.current) {
                    track.attach(videoRef.current); // Gắn track video vào thẻ HTML
                    setStatus('LIVE');
                }
            });

            lkRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
                if (videoRef.current) track.detach(videoRef.current);
                setStatus('OFFLINE');
            });

            lkRoom.on(RoomEvent.Disconnected, () => {
                setStatus('OFFLINE');
            });

            // 4. Kết nối WebRTC trực tiếp tới LiveKit Cloud
            await lkRoom.connect(server_url, token);
            setRoom(lkRoom);

        } catch (error) {
            console.error("❌ Kết nối LiveKit lỗi:", error);
            setStatus('ERROR');
        }
    };

    const stopStream = async () => {
        if (room) {
            await room.disconnect();
            setRoom(null);
        }
        setStatus('OFFLINE');
    };

    useEffect(() => {
        // Tự động dọn dẹp kết nối khi component bị huỷ (Unmount)
        return () => {
            if (room) room.disconnect();
        };
    }, [room]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ position: 'relative', width: '640px', height: '360px', background: '#000' }}>
                {status !== 'LIVE' && (
                    <div style={{ color: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        {status === 'CONNECTING' ? 'Đang kết nối camera...' : 'Camera ngoại tuyến'}
                    </div>
                )}
                <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', display: status === 'LIVE' ? 'block' : 'none' }} />
            </div>
            <div>
                {status === 'OFFLINE' || status === 'ERROR' ? (
                    <button onClick={startStream}>Xem Camera</button>
                ) : (
                    <button onClick={stopStream}>Dừng xem</button>
                )}
            </div>
        </div>
    );
};
```

---

## 💻 2. Mã nguồn tích hợp cho Web (Vanilla Javascript / CDN)

Nếu dự án của bạn sử dụng HTML tĩnh hoặc các hệ thống không dùng bundler (như PHP, Django), bạn có thể nhúng trực tiếp qua thẻ `<script>`.

### ⚠️ Lưu ý đặc biệt về UMD Global Variable:
Khi nhúng qua CDN, thư viện LiveKit Client sẽ xuất ra một biến toàn cục trên đối tượng `window` với tên là **`LivekitClient`** (lưu ý: **chữ `k` viết thường**). Mọi thao tác truy cập sẽ đi qua đối tượng này.

```html
<!-- Nhúng LiveKit Client SDK -->
<script src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js"></script>

<div class="video-container">
    <video id="camera-video" autoplay muted playsinline controls style="width: 100%; max-width: 640px; background: #000;"></video>
</div>
<button onclick="viewCamera()">Bắt Đầu Xem</button>

<script>
    async function viewCamera() {
        const cloudServerUrl = "https://camera-relay-v5.onrender.com";
        const cameraId = "workshop-laptop-camera";
        const roomName = "mylongai";
        const videoEl = document.getElementById("camera-video");

        try {
            // 1. Gọi API của bạn để lấy Token
            const res = await fetch(`${cloudServerUrl}/api/cameras/${cameraId}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    identity: `web_viewer_${Math.random().toString(36).substring(7)}`,
                    room_name: roomName
                })
            });
            const { token, server_url } = await res.json();

            // 2. Khởi tạo Room (sử dụng đối tượng LivekitClient toàn cục)
            const { Room, RoomEvent } = window.LivekitClient;
            const room = new Room({ adaptiveStream: true, dynacast: true });

            // 3. Đăng ký nhận luồng video
            room.on(RoomEvent.TrackSubscribed, (track) => {
                if (track.kind === 'video') {
                    track.attach(videoEl);
                }
            });

            // 4. Kết nối
            await room.connect(server_url, token);
            console.log("✅ Đã kết nối thành công!");

        } catch (e) {
            console.error("Lỗi kết nối WebRTC:", e);
        }
    }
</script>
```

---

## 📱 3. Mã nguồn tích hợp cho Mobile (Flutter)

Sử dụng package chính thức của LiveKit trên pub.dev: [livekit_client](https://pub.dev/packages/livekit_client).

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:livekit_client/livekit_client.dart';

class LiveKitMobileViewer {
  final String cloudServerUrl;
  final String cameraId;
  Room? _room;
  
  // Renderer để vẽ hình ảnh lên giao diện Flutter (được gắn vào Widget VideoTrackRenderer)
  VideoTrack? videoTrack;

  LiveKitMobileViewer(this.cloudServerUrl, this.cameraId);

  Future<void> connectToCamera() async {
    try {
      // 1. Lấy token từ Cloud Server
      var response = await http.post(
        Uri.parse('$cloudServerUrl/api/cameras/$cameraId/token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'identity': 'flutter_viewer_device',
          'room_name': 'mylongai'
        }),
      );

      if (response.statusCode != 200) {
        throw Exception("Không thể lấy token xác thực");
      }

      var data = jsonDecode(response.body);
      String token = data['token'];
      String serverUrl = data['server_url'];

      // 2. Khởi tạo Room và kết nối
      _room = await Room.connect(
        serverUrl,
        token,
        roomOptions: const RoomOptions(
          adaptiveStream: true,
          dynacast: true,
        ),
      );

      // 3. Lắng nghe sự kiện nhận track
      final listener = _room!.createListener();
      listener.on<TrackSubscribedEvent>((event) {
        if (event.track is VideoTrack) {
          // Lưu track lại để hiển thị lên UI Widget của Flutter
          videoTrack = event.track as VideoTrack;
          print("📹 Đã nhận được track video camera từ LiveKit!");
        }
      });

    } catch (e) {
      print("❌ Lỗi kết nối LiveKit Flutter: $e");
      Future.delayed(const Duration(seconds: 5), () => connectToCamera());
    }
  }

  void disconnect() async {
    await _room?.disconnect();
    _room = null;
  }
}
```

---

## 💡 Các lưu ý đặc biệt cho FE khi tích hợp LiveKit

1. **Chế độ Autoplay của Trình duyệt:** Hầu hết các trình duyệt hiện đại (Chrome, Safari, iOS Safari) sẽ chặn phát video tự động nếu video đó có âm thanh. Hãy đảm bảo thẻ `<video>` của bạn có các thuộc tính `muted`, `playsinline` và `autoplay`.
2. **Quản lý Vòng đời Kết nối (Connection Lifecycle):** Đảm bảo gọi phương thức `room.disconnect()` hoặc `track.detach()` khi người dùng chuyển trang hoặc đóng giao diện xem camera (Component Unmount). Nếu không, trình duyệt sẽ tiếp tục tải luồng dữ liệu video ngầm làm tiêu hao băng thông của người dùng và thiết bị local.
3. **Adaptive Bitrate (Tự động thích ứng mạng):** LiveKit SDK tự động xử lý các tình huống mạng chập chờn. Khi mạng của người dùng yếu, LiveKit sẽ tự động giảm bitrate/fps của luồng video xuống để tránh bị đứng hình, và tự động nâng chất lượng lên khi mạng ổn định trở lại.
