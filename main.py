import cv2 as cv
import numpy as np

def cartoonize_image(img_path):
    # 1. 이미지 불러오기
    img = cv.imread(img_path)
    if img is None:
        print("이미지를 찾을 수 없습니다.")
        return

    # =========================================
    # Step 1: 스케치 선(Edge) 추출하기
    # =========================================
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray_blur = cv.medianBlur(gray, 3)
    edges = cv.adaptiveThreshold(
        gray_blur, 255,
        cv.ADAPTIVE_THRESH_MEAN_C,
        cv.THRESH_BINARY,
        blockSize=9, C=9
    )

    # =========================================
    # Step 2: Sharpening Filter - 트랙바로 실시간 조정
    # =========================================
    # 커널 구조:
    #   [  0,  -nb,   0 ]
    #   [ -nb,  ct, -nb ]
    #   [  0,  -nb,   0 ]
    # ct  = 중앙값 (center)  : 클수록 원본 강조
    # nb  = 주변값 (neighbor): 클수록 엣지 강조

    WINDOW = "Cartoon Style (trackbar로 조정)"
    cv.namedWindow(WINDOW)

    # 트랙바 초기값 (정수만 가능하므로 실제값 = 트랙바값 / 10)
    # center: 1~200 → 실제 0.1~20.0  (초기 50 → 5.0)
    # neighbor: 0~100 → 실제 0.0~10.0 (초기 10 → 1.0)
    # edge thickness: 0~20 → dilate 반복 횟수 (0 = 원본, 1픽셀씩 증가)
    # contrast x0.1: 1~30 → 실제 0.1~3.0  (초기 15 → 1.5)
    # brightness: -150~150 → addWeighted beta값 (초기 -110)
    cv.createTrackbar("center x0.1",    WINDOW,  50, 200, lambda x: None)
    cv.createTrackbar("neighbor x0.1",  WINDOW,  10, 100, lambda x: None)
    cv.createTrackbar("edge thickness", WINDOW,   0,  20, lambda x: None)
    cv.createTrackbar("contrast x0.1", WINDOW,  15,  30, lambda x: None)
    cv.createTrackbar("brightness+150", WINDOW,  40, 300, lambda x: None)  # 실제값 = 트랙바값 - 150

    print("=== Cartoon Filter 실시간 조정 ===")
    print("  center      트랙바: 샤프닝 중앙값")
    print("  neighbor    트랙바: 샤프닝 주변값 (엣지 강도)")
    print("  edge thickness   : 선 두께 0~20")
    print("  contrast    트랙바: 색상 대비 (x0.1)")
    print("  brightness  트랙바: 밝기 (-150~+150)")
    print("  ESC: 종료 (현재 값 터미널에 출력)")
    print("===================================")

    while True:
        ct         = cv.getTrackbarPos("center x0.1",    WINDOW) / 10.0
        nb         = cv.getTrackbarPos("neighbor x0.1",  WINDOW) / 10.0
        thickness  = cv.getTrackbarPos("edge thickness", WINDOW)
        contrast   = cv.getTrackbarPos("contrast x0.1", WINDOW) / 10.0
        brightness = cv.getTrackbarPos("brightness+150", WINDOW) - 150

        ct       = max(ct, 0.1)
        contrast = max(contrast, 0.1)

        # thickness=0이면 원본 edges 그대로, 1 이상이면 1픽셀 커널로 반복 침식
        if thickness == 0:
            thick_edges = edges
        else:
            kernel      = np.ones((3, 3), np.uint8)
            thick_edges = cv.erode(edges, kernel, iterations=thickness)

        sharpening_kernel = np.array([
            [  0, -nb,   0],
            [-nb,  ct, -nb],
            [  0, -nb,   0]
        ], dtype=np.float32)

        # =========================================
        # Step 3: 선과 색상 합성하기
        # =========================================
        color   = cv.filter2D(img, -1, sharpening_kernel)
        cartoon = cv.bitwise_and(color, color, mask=thick_edges)
        cartoon = cv.addWeighted(cartoon, contrast, np.zeros(cartoon.shape, cartoon.dtype), 1, brightness)

        # 현재 값을 이미지에 표시
        info = cartoon.copy()
        cv.putText(info, f"center={ct:.1f}  neighbor={nb:.1f}  edge={thickness}",
                   (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.putText(info, f"contrast={contrast:.1f}  brightness={brightness}",
                   (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.putText(info, "ESC: quit & print values",
                   (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.55, (200, 0, 200), 1)

        cv.imshow("Original Image", img)
        cv.imshow(WINDOW, info)

        key = cv.waitKey(30) & 0xFF
        if key == 27:  # ESC → 종료 및 현재 값 출력
            print("\n=== 최종 설정값 ===")
            print(f"  center     = {ct:.1f}")
            print(f"  neighbor   = {nb:.1f}")
            print(f"  thickness  = {thickness}")
            print(f"  contrast   = {contrast:.1f}")
            print(f"  brightness = {brightness}")
            print("==================")
            break

    cv.destroyAllWindows()

# 실행 예시 (본인의 이미지 파일 경로로 변경하세요)
try:
    cartoonize_image('./image/image.jpeg')
except KeyboardInterrupt:
    print("\n프로그램을 종료합니다.")
    cv.destroyAllWindows()