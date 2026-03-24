import cv2 as cv
import numpy as np

def analyze_image(img):
    """
    이미지 특성을 분석해서 각 파라미터의 추천 초기값을 반환합니다.
    """
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    h, w  = img.shape[:2]
    mean  = float(np.mean(gray))
    std   = float(np.std(gray))
    mpx   = (h * w) / 1_000_000

    print(f"  해상도    : {w}x{h} ({mpx:.1f} MP)")
    print(f"  평균 밝기 : {mean:.1f}")
    print(f"  대비(std) : {std:.1f}")

    # ── center (샤프닝 중앙값) ──────────────────────────────
    # 대비가 낮으면 샤프닝을 강하게(center 크게), 높으면 약하게
    if std < 40:
        center = 9.5   # 대비 낮음 → 더 강한 샤프닝
    elif std < 70:
        center = 9.0   # 보통 (최종값 반영)
    else:
        center = 9.0   # 대비 높음

    # ── neighbor (엣지 강조) ───────────────────────────────
    # 해상도가 높을수록 세밀한 엣지가 많으므로 약하게
    if mpx > 4:
        neighbor = 1.8
    elif mpx > 1:
        neighbor = 2.2
    else:
        neighbor = 2.0   # 최종값 반영

    # ── edge thickness ─────────────────────────────────────
    # 해상도가 높을수록 선을 조금 더 두껍게 해야 눈에 잘 보임
    if mpx > 4:
        thickness = 1
    elif mpx > 1:
        thickness = 1
    else:
        thickness = 1

    # ── contrast (addWeighted alpha) ───────────────────────
    # 대비가 낮으면 contrast를 높게
    if std < 40:
        contrast = 1.8
    elif std < 50:
        contrast = 1.0   # 최종값 반영 (std=41.1)
    elif std < 65:
        contrast = 0.8   # 최종값 반영 (std=56~60)
    elif std < 70:
        contrast = 1.5   # 최종값 반영 (std=60.2→1.4, std=65.2→1.5 평균)
    else:
        contrast = 1.7   # 최종값 반영 (std=73.2)

    # ── brightness (addWeighted beta) ──────────────────────
    # 어두운 이미지 → 밝게(+), 밝은 이미지 → 어둡게(-)
    if mean < 80:
        brightness = -21   # 최종값 반영 (mean=55.7)
    elif mean < 100:
        brightness = 10    # 최종값 반영 (mean=88.1)
    elif mean < 112:
        brightness = -97   # 최종값 반영 (mean=111.4)
    elif mean < 115:
        brightness = -48   # 최종값 반영 (mean=112.5)
    elif mean < 126:
        brightness = -38   # 최종값 반영 (mean=124.9)
    elif mean < 130:
        brightness = -54   # 최종값 반영 (mean=127.1)
    else:
        brightness = -50   # 7번 이미지(mean=142.3) 밝기 개선 반영

    return center, neighbor, thickness, contrast, brightness


def cartoonize_image(img_path):
    # 1. 이미지 불러오기
    img = cv.imread(img_path)
    if img is None:
        print("이미지를 찾을 수 없습니다.")
        return

    # 이미지 분석 → 추천 초기값 계산
    init_center, init_neighbor, init_thickness, init_contrast, init_brightness = analyze_image(img)

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
    # Step 2: Sharpening Filter
    # =========================================
    # 커널 구조:
    #   [  0,  -nb,   0 ]
    #   [ -nb,  ct, -nb ]
    #   [  0,  -nb,   0 ]
    # ct  = 중앙값 (center)  : 클수록 원본 강조
    # nb  = 주변값 (neighbor): 클수록 엣지 강조

    ct         = init_center
    nb         = init_neighbor
    thickness  = init_thickness
    contrast   = init_contrast
    brightness = init_brightness

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

    cv.imshow("Original Image", img)
    cv.imshow("Cartoon Style", cartoon)
    cv.waitKey(0)
    cv.destroyAllWindows()

# 실행 예시 (본인의 이미지 파일 경로로 변경하세요)
try:
    for i in range(1, 11):
        path = f'./image/{i}.jpeg'
        print(f"\n{'='*40}")
        print(f"  [{i}/10] {path}")
        print(f"{'='*40}")
        cartoonize_image(path)
except KeyboardInterrupt:
    print("\n프로그램을 종료합니다.")
    cv.destroyAllWindows()