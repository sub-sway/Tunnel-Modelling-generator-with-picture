"""
터널 3D 포인트클라우드 생성기
- IMU(yaw, pitch) + Encoder(distance) 데이터로 중심선 생성
- 반원 단면을 Sweep하여 포인트클라우드 생성
- 결함 위치 + 사진 매핑 데이터를 JSON으로 출력
- 결과물: viewer/data/tunnel_points.json, viewer/data/defects.json
"""

import numpy as np
import json
import os
import webbrowser
import cv2


# ==============================
# 1. 터널 기본 설정
# ==============================

R = 5.0          # 터널 반지름(m)
length = 50      # 터널 길이(m)
step_size = 0.5  # 중심선 간격(m) — 작을수록 포인트 밀도 높음
n_theta = 40     # 단면 포인트 수 (반원 방향)

# 출력 경로
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "viewer", "data")
DEFECT_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "defect_images")
VIEWER_PATH = os.path.join(os.path.dirname(__file__), "viewer", "index.html")


# ==============================
# 2. IMU + Encoder 데이터
# (★ 실제 센서값으로 교체하세요)
# ==============================

distance = np.arange(0, length, step_size)

# yaw 변화(deg) — 실제로는 IMU yaw값 사용
yaw_deg = np.zeros_like(distance)
yaw_deg[distance >= 20] = 0.5 * (distance[distance >= 20] - 20)

# pitch 변화(deg) — 실제로는 IMU pitch값 사용
pitch_deg = np.zeros_like(distance)
pitch_deg[distance >= 30] = 0.3 * (distance[distance >= 30] - 30)


# ==============================
# 3. 터널 중심선 생성
# ==============================

centerline = np.zeros((len(distance), 3))

for i in range(1, len(distance)):
    yaw = np.deg2rad(yaw_deg[i])
    pitch = np.deg2rad(pitch_deg[i])

    dx = np.cos(yaw) * np.cos(pitch)
    dy = np.sin(yaw) * np.cos(pitch)
    dz = np.sin(pitch)

    ds = distance[i] - distance[i - 1]
    centerline[i] = centerline[i - 1] + np.array([dx, dy, dz]) * ds


# ==============================
# 4. Frenet-Serret 프레임 계산
# ==============================

def compute_frames(centerline):
    n = len(centerline)
    tangents = np.zeros_like(centerline)

    tangents[0] = centerline[1] - centerline[0]
    tangents[-1] = centerline[-1] - centerline[-2]
    for i in range(1, n - 1):
        tangents[i] = centerline[i + 1] - centerline[i - 1]

    norms = np.linalg.norm(tangents, axis=1, keepdims=True)
    norms[norms == 0] = 1
    tangents = tangents / norms

    up = np.array([0, 0, 1.0])
    normals = np.zeros_like(centerline)
    binormals = np.zeros_like(centerline)

    for i in range(n):
        binormal = np.cross(tangents[i], up)
        if np.linalg.norm(binormal) < 1e-6:
            binormal = np.cross(tangents[i], np.array([1, 0, 0]))
        binormal = binormal / np.linalg.norm(binormal)
        normal = np.cross(binormal, tangents[i])
        normal = normal / np.linalg.norm(normal)

        normals[i] = normal
        binormals[i] = binormal

    return tangents, normals, binormals


tangents, normals, binormals = compute_frames(centerline)


# ==============================
# 5. 포인트클라우드 생성 (반원 단면 Sweep)
# ==============================

theta = np.linspace(0, np.pi, n_theta)
points = []

for i in range(len(centerline)):
    for t in theta:
        local_right = R * np.cos(t)
        local_up = R * np.sin(t)

        pt = (centerline[i]
              + local_right * binormals[i]
              + local_up * normals[i])
        points.append(pt)

points = np.array(points)
print(f"✅ 포인트클라우드 생성: {len(points):,}개 점")


# ==============================
# 6. 결함 데이터 정의
# (★ 실제 결함 검출 결과로 교체하세요)
# ==============================

defects = [
    {
        "id": 1,
        "label": "균열 #1",
        "type": "crack",
        "pos": [10.0, 0.5, 4.0],
        "image": "crack_01.jpg",
        "description": "종방향 균열, 폭 2mm, 길이 30cm",
    },
    {
        "id": 2,
        "label": "누수 #2",
        "type": "leak",
        "pos": [25.0, 3.0, 3.5],
        "image": "leak_02.jpg",
        "description": "천장부 누수, 석회 침착 동반",
    },
    {
        "id": 3,
        "label": "박리 #3",
        "type": "spalling",
        "pos": [40.0, 6.0, 2.0],
        "image": "spalling_03.jpg",
        "description": "콘크리트 박리, 철근 노출 10cm",
    },
]

# 테스트용 더미 이미지 생성 (실제 사진으로 교체)
os.makedirs(DEFECT_IMAGE_DIR, exist_ok=True)
for d in defects:
    img_path = os.path.join(DEFECT_IMAGE_DIR, d["image"])
    if not os.path.exists(img_path):
        dummy = np.zeros((400, 600, 3), dtype=np.uint8)
        dummy[:] = (40, 40, 40)
        cv2.putText(dummy, d["label"], (50, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 200, 255), 3)
        cv2.putText(dummy, d["description"], (50, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(dummy, f"pos: {d['pos']}", (50, 320),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        cv2.putText(dummy, "[TEST IMAGE]", (50, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        cv2.imwrite(img_path, dummy)


# ==============================
# 7. JSON 출력
# ==============================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 포인트클라우드 JSON (좌표 + 색상)
z_vals = points[:, 2]
z_min, z_max = z_vals.min(), z_vals.max()
z_range = z_max - z_min if z_max - z_min > 0 else 1.0
z_norm = (z_vals - z_min) / z_range

colors = np.zeros((len(points), 3))
colors[:, 0] = z_norm
colors[:, 1] = 1.0 - np.abs(z_norm - 0.5) * 2
colors[:, 2] = 1.0 - z_norm

tunnel_data = {
    "radius": R,
    "length": length,
    "num_points": len(points),
    "points": points.tolist(),
    "colors": colors.tolist(),
    "centerline": centerline.tolist(),
    "entrance": centerline[0].tolist(),
    "exit": centerline[-1].tolist(),
}

tunnel_json_path = os.path.join(OUTPUT_DIR, "tunnel_points.json")
with open(tunnel_json_path, "w", encoding="utf-8") as f:
    json.dump(tunnel_data, f)
print(f"✅ 포인트클라우드 저장: {tunnel_json_path}")

# 결함 데이터 JSON
defects_json_path = os.path.join(OUTPUT_DIR, "defects.json")
with open(defects_json_path, "w", encoding="utf-8") as f:
    json.dump(defects, f, ensure_ascii=False, indent=2)
print(f"✅ 결함 데이터 저장: {defects_json_path}")


# ==============================
# 8. 로컬 서버 + 브라우저 열기
# ==============================

import http.server
import socketserver
import threading
import socket
import time

VIEWER_DIR = os.path.dirname(os.path.abspath(__file__))  # 프로젝트 루트

def find_free_port(start=9000, end=9100):
    """사용 가능한 포트 찾기"""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return None

PORT = find_free_port()
if PORT is None:
    print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
    exit(1)

def start_server():
    os.chdir(VIEWER_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()

# 서버를 백그라운드 스레드로 실행
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(0.5)

url = f"http://127.0.0.1:{PORT}/viewer/index.html"
print(f"\n🌐 뷰어 서버 시작: {url}")
print("   (종료: Ctrl+C)")
webbrowser.open(url)

# 서버 유지 (Ctrl+C로 종료)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n서버 종료.")
