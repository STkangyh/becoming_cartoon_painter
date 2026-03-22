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
    # 흑백 이미지로 변환
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # 노이즈 제거 (우리가 배운 Median Filter 사용!)
    # 소금-후추 노이즈를 지워주어 깔끔한 선을 얻게 해줍니다.
    gray_blur = cv.medianBlur(gray, 7)

    # Adaptive Thresholding (적응형 이진화) 적용
    # 조명이 달라도 국소적인 영역을 기준으로 검은색 테두리(0)와 흰색 배경(255)을 분리합니다.
    edges = cv.adaptiveThreshold(
        gray_blur, 255, 
        cv.ADAPTIVE_THRESH_MEAN_C, 
        cv.THRESH_BINARY, 
        blockSize=9, C=9
    )

    # =========================================
    # Step 2: 색상 단순화하기 (Bilateral Filter)
    # =========================================
    # 에지(경계선)는 보존하면서 내부의 질감만 뭉개주는 고급 필터입니다.
    # 만화처럼 색이 칠해진 효과를 줍니다. (반복 적용하면 효과가 더 큽니다)
    color = cv.bilateralFilter(img, d=9, sigmaColor=300, sigmaSpace=300)
    
    # =========================================
    # Step 3: 선과 색상 합성하기
    # =========================================
    # 색상이 단순화된 이미지 위에 까만색 스케치 선(edges 맵)을 덮어씌웁니다.
    cartoon = cv.bitwise_and(color, color, mask=edges)

    # 결과 출력
    cv.imshow("Original Image", img)
    cv.imshow("Cartoon Style", cartoon)

    cv.waitKey(0)
    cv.destroyAllWindows()

# 실행 예시 (본인의 이미지 파일 경로로 변경하세요)
# cartoonize_image('my_photo.jpg')