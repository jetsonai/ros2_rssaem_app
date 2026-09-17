#!/usr/bin/env python3
# Copyright 2024 JetsonAI CO., LTD.
#
# 카메라 설정 공용 모듈 (config.py)
#
# 젯슨(Orin/Nano)의 CSI 카메라(nvarguscamerasrc)와 일반 PC의 USB 웹캠(index 0)을
# 실행 환경에 따라 자동으로 골라서 cv2.VideoCapture 를 열어주는 헬퍼입니다.
#
# cam_node.py / webcam_pub.py / webcam_comp_pub.py 는 모두
#     gst_str = ("nvarguscamerasrc ! ...")
#     self.cap = cv2.VideoCapture(gst_str)
# 형태로 젯슨 전용 문자열을 하드코딩하고 있었는데, 이 모듈을 import 해서
#     from config import get_capture
#     self.cap = get_capture()
# 로 바꾸면 같은 코드가 젯슨에서도, 일반 PC(랩탑 웹캠 등)에서도 그대로 동작합니다.
#
# 사용법
# ------
#   from config import get_capture
#
#   cap = get_capture()                    # 자동 감지 (젯슨이면 CSI, 아니면 USB index 0)
#   cap = get_capture(force="jetson")      # 강제로 젯슨 CSI 카메라 사용
#   cap = get_capture(force="usb")         # 강제로 USB 웹캠(index 0) 사용
#   cap = get_capture(force="usb", device_id=1)  # /dev/video1 사용
#
# 코드 수정 없이 실행 시점에 강제로 지정하고 싶다면 환경변수를 쓰면 됩니다.
#   CAMERA_BACKEND=jetson 또는 usb   -> 백엔드 강제 지정 (자동 감지보다 우선)
#   CAMERA_DEVICE_ID=0               -> USB 웹캠 device index
#   CAMERA_WIDTH / CAMERA_HEIGHT / CAMERA_FPS / CAMERA_FLIP_METHOD
#
#   예) 일반 PC에서 강제로 USB 웹캠 1번 사용하도록 실행
#       CAMERA_BACKEND=usb CAMERA_DEVICE_ID=1 ros2 run cv_basics cam_node

import os
import cv2


# ---------------------------------------------------------------------------
# 기본 설정값 (필요하면 여기 값을 바꾸거나, 위의 환경변수로 오버라이드 하세요)
# ---------------------------------------------------------------------------
DEFAULT_WIDTH = int(os.environ.get("CAMERA_WIDTH", 640))
DEFAULT_HEIGHT = int(os.environ.get("CAMERA_HEIGHT", 480))
DEFAULT_FPS = int(os.environ.get("CAMERA_FPS", 60))
DEFAULT_FLIP_METHOD = int(os.environ.get("CAMERA_FLIP_METHOD", 2))
DEFAULT_DEVICE_ID = int(os.environ.get("CAMERA_DEVICE_ID", 0))


def is_jetson() -> bool:
    """현재 보드가 Jetson(Orin/Nano 등)인지 판별합니다."""
    # 1) 젯슨 전용 파일이 있는지 확인 (가장 확실한 방법)
    if os.path.exists("/etc/nv_tegra_release"):
        return True
    # 2) 디바이스 트리 모델명에 'NVIDIA Jetson' 문자열이 있는지 확인
    try:
        with open("/proc/device-tree/model", "r") as f:
            if "NVIDIA Jetson" in f.read():
                return True
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return False


def build_gst_str(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                   fps=DEFAULT_FPS, flip_method=DEFAULT_FLIP_METHOD) -> str:
    """젯슨 CSI 카메라(nvarguscamerasrc)용 GStreamer 파이프라인 문자열을 만듭니다."""
    return (
        "nvarguscamerasrc ! "
        f"video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, "
        f"format=(string)NV12, framerate=(fraction){fps}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )


def get_camera_source(force: str = None, device_id: int = None,
                       width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                       fps=DEFAULT_FPS, flip_method=DEFAULT_FLIP_METHOD):
    """
    사용할 카메라 소스를 결정해서 (source, backend) 튜플로 반환합니다.

    - source  : cv2.VideoCapture 에 넘길 값 (GStreamer 문자열 또는 정수 device index)
    - backend : cv2.VideoCapture 에 넘길 backend 플래그 (cv2.CAP_GSTREAMER 또는 None)

    force 인자나 CAMERA_BACKEND 환경변수("jetson"/"usb")가 있으면 그것을 우선하고,
    없으면 is_jetson() 으로 자동 판별합니다.
    """
    backend_env = os.environ.get("CAMERA_BACKEND")  # "jetson" 또는 "usb"
    choice = force or backend_env
    if choice is not None:
        choice = choice.strip().lower()

    use_jetson = {"jetson": True, "usb": False}.get(choice)
    if use_jetson is None:
        use_jetson = is_jetson()

    if use_jetson:
        gst_str = build_gst_str(width=width, height=height, fps=fps, flip_method=flip_method)
        return gst_str, cv2.CAP_GSTREAMER

    dev_id = device_id if device_id is not None else DEFAULT_DEVICE_ID
    return dev_id, None


def get_capture(force: str = None, device_id: int = None,
                 width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                 fps=DEFAULT_FPS, flip_method=DEFAULT_FLIP_METHOD) -> cv2.VideoCapture:
    """카메라를 열어서 cv2.VideoCapture 객체를 반환합니다.

    젯슨이면 nvarguscamerasrc GStreamer 파이프라인으로, 아니면
    cv2.VideoCapture(device_id) 로 엽니다 (open 실패 여부는 호출부에서
    cap.isOpened() 로 기존처럼 확인하면 됩니다).
    """
    source, backend = get_camera_source(
        force=force, device_id=device_id,
        width=width, height=height, fps=fps, flip_method=flip_method,
    )

    if backend is not None:
        cap = cv2.VideoCapture(source, backend)
    else:
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


if __name__ == "__main__":
    # 간단한 자체 테스트: python3 config.py
    print(f"Jetson 감지 여부 : {is_jetson()}")
    src, backend = get_camera_source()
    if backend is not None:
        print("사용할 백엔드    : Jetson CSI (nvarguscamerasrc)")
        print("GStreamer 문자열 :", src)
    else:
        print("사용할 백엔드    : 일반 USB 웹캠")
        print("device index     :", src)
