# 🎨 Becoming Cartoon Painter

일반 사진을 만화 스타일로 변환하는 Python 이미지 처리 프로젝트입니다.  
OpenCV만을 사용하며, 이미지 특성을 자동으로 분석해 최적의 파라미터를 적용합니다.

---

## 📁 프로젝트 구조

```
becomingCartoonDesigner/
├── main.py
└── image/
    └── (변환할 이미지 파일)
```

---

## ⚙️ 요구 사항

- Python 3.x
- OpenCV
- NumPy

```bash
pip install opencv-python numpy
```

---

## 🚀 실행 방법

```bash
python3 main.py
```

`main.py` 하단의 이미지 경로를 변환할 파일로 수정하세요.

```python
cartoonize_image('./image/myImage.jpeg')
```

---

## 🔧 동작 원리

### Step 1 — 스케치 선(Edge) 추출

| 처리 | 설명 |
|---|---|
| `cvtColor` | 흑백 변환 |
| `medianBlur` | Median Filter로 노이즈(소금-후추) 제거 |
| `adaptiveThreshold` | 조명 차이에 강인한 적응형 이진화로 검은 테두리 추출 |
| `erode` | Erosion으로 선 두께 조정 |

### Step 2 — Sharpening Filter

Bilateral Filter(스무딩) 대신 **Sharpening Kernel**을 사용하여 색을 뭉개지 않고 경계를 선명하게 강조합니다.

$$\begin{bmatrix} 0 & -nb & 0 \\ -nb & ct & -nb \\ 0 & -nb & 0 \end{bmatrix}$$

- **`ct` (center)**: 중앙값. 클수록 원본 색감 유지
- **`nb` (neighbor)**: 주변값. 클수록 엣지 강조

### Step 3 — 선과 색상 합성

`bitwise_and`로 색상 이미지 위에 스케치 선을 마스크로 덮어씌우고,  
`addWeighted`로 대비(contrast)와 밝기(brightness)를 최종 보정합니다.

---

## 🤖 자동 파라미터 분석 (`analyze_image`)

실행 시 이미지의 특성을 분석하여 각 파라미터의 최적값을 자동으로 계산합니다.

| 분석 항목 | 계산 방법 | 영향을 주는 파라미터 |
|---|---|---|
| **평균 밝기** (`mean`) | `np.mean(gray)` | `brightness` |
| **대비** (`std`) | `np.std(gray)` | `center`, `contrast` |
| **해상도** (`mpx`) | `width × height / 1,000,000` | `neighbor`, `thickness` |

### 파라미터 추천 기준 (실제 이미지 테스트로 축적된 값)

**brightness** — 평균 밝기 기준:

| mean 범위 | brightness |
|---|---|
| < 80 | -21 |
| < 100 | +10 |
| < 112 | -97 |
| < 115 | -48 |
| < 126 | -38 |
| < 130 | -54 |
| ≥ 130 | -111 |

**contrast** — 대비(std) 기준:

| std 범위 | contrast |
|---|---|
| < 40 | 1.8 |
| < 50 | 1.0 |
| < 65 | 0.8 |
| < 70 | 1.5 |
| ≥ 70 | 1.7 |

**neighbor** — 해상도(mpx) 기준:

| mpx 범위 | neighbor |
|---|---|
| > 4 MP | 1.8 |
| > 1 MP | 2.2 |
| ≤ 1 MP | 2.0 |

---

## 🛠️ 개발 과정 요약

1. **기본 만화 필터 구현** — Bilateral Filter + Adaptive Threshold + bitwise_and
    Bilateral Filter의 smoothing 기능이 만화 그림체의 역동적인 측면을 표현하는 데에 해친다고 생각하여 더 이상 사용하지 않기로 결정함.
2. **Sharpening Filter로 교체** — 스무딩 없이 선명한 엣지 강조
3. **실시간 조정 기능 추가** — OpenCV 트랙바로 파라미터 실시간 조정
4. **선 두께 조정 추가** — Erosion 반복 횟수로 1픽셀 단위 세밀 조정
5. **자동 분석 기능 추가** — 이미지 밝기·대비·해상도 분석 후 추천값 자동 적용
6. **파라미터 튜닝** — 다수의 이미지 테스트를 통해 분기별 최적값 누적 반영
7. **코드 정리** — 테스트용 코드 및 트랙바 제거, 자동화 완성
