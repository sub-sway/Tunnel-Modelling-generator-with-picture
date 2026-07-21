# Tunnel-Modelling-generator-with-picture
사진과 IMU를 이용한 터널 모델링 및 결함,얼룩 위치 확인 

## Overview

터널 내부 주행 중 획득한 이미지와 IMU 데이터를 기반으로 터널 형상을 모델링하고,
AI 기반 결함 및 얼룩 탐지 결과를 3D 모델 상에 표시하는 시스템입니다.

<br>

## Result

<table align="center" border="1" cellspacing="0" cellpadding="5">

<tr>
<td colspan="2" align="center">

<img width="1000" src="https://github.com/user-attachments/assets/5c14d214-1f7d-4887-8c62-26685d1eee2e">

<br>

<b>터널 3D 모델링</b><br>
IMU 및 이동 데이터를 기반으로 생성한 터널 Point Cloud 모델

</td>
</tr>


<tr>

<td align="center" valign="top">

<img width="450" height="300" style="object-fit: cover;"
src="https://github.com/user-attachments/assets/ac8b433c-32f5-464f-8b83-6539c7dc9636">

<br>

<b>터널 결함 및 얼룩 Point Mapping</b><br>
AI 탐지 결과를 3D 터널 모델 위에 표시하여<br>
결함 위치를 확인

</td>


<td align="center" valign="top">

<img width="450" height="300" style="object-fit: cover;"
src="https://github.com/user-attachments/assets/8c0760ff-6358-4b94-886a-bf3c14910e82">

<br>

<b>결함 Point 클릭 결과</b><br>
선택한 결함 위치의 상세 정보 확인

</td>

</tr>

</table>


<br>

## Installation

### 사전 요구사항

- Python 3.12 이상
- pip (Python 패키지 관리자)

### 1. 저장소 클론

```bash
git clone https://github.com/sub-sway/Tunnel-Modelling-generator-with-picture.git
cd Tunnel-Modelling-generator-with-picture
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv tunnel_env

# 활성화 (Windows)
tunnel_env\Scripts\activate

# 활성화 (macOS/Linux)
source tunnel_env/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

`requirements.txt`에 포함된 주요 패키지:
- `numpy` — 수치 계산 및 포인트클라우드 생성
- `opencv-python` — 결함 이미지 처리
- `trimesh` — 3D 메시 생성 및 OBJ 저장


<br>

## Usage

### 방법 1: 웹 브라우저 뷰어 (generate_tunnel.py)

터널 포인트클라우드를 생성하고 웹 브라우저에서 3D 뷰어를 실행합니다.

```bash
python generate_tunnel.py
```

실행 결과:
- `viewer/data/tunnel_points.json` — 터널 포인트클라우드 데이터
- `viewer/data/defects.json` — 결함 위치 및 정보
- 로컬 서버(`http://127.0.0.1:9000`)가 자동 시작되고 브라우저가 열림
- 종료: `Ctrl+C`

<br>

## Project Structure

```
Tunnel-Modelling-generator-with-picture/
├── generate_tunnel.py    # 웹 뷰어용 터널 생성 스크립트
├── requirements.txt      # Python 의존성 패키지
├── defect_images/        # 결함 사진 (실제 촬영 이미지로 교체 가능)
│   ├── crack_01.jpg
│   ├── leak_02.jpg
│   └── spalling_03.jpg
└── viewer/               # 웹 기반 3D 뷰어 (generate_tunnel.py 실행 시 생성)
    └── data/
        ├── tunnel_points.json
        └── defects.json
```
