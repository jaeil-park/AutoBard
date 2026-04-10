# 개발 과업 현황 (todo.md)

## Phase 1: 기반 구축 [x]

- [x] Antigravity 환경 내 API 키 보안 설정 (`.env`)
- [x] FFmpeg 라이브러리 설치 및 연동 확인
- [x] 텍스트 전처리기 구현 (지문/대사 분리 로직)

## Phase 2: 에셋 생성 엔진 [x]

- [x] OpenAI TTS API 연동 (아저씨 보이스 선정 및 테스트)
- [x] DALL-E 3 / Midjourney API 기반 이미지 생성 프롬프트 자동화
- [x] SRT 자막 파일 자동 생성 모듈 구현

## Phase 3: 영상 렌더링 자동화 [x]

- [x] MoviePy/FFmpeg 기반 이미지+오디오 합치기
- [x] 이미지 줌인/줌아웃(Ken Burns) 효과 코딩
- [x] 하단 미니멀 자막 오버레이 구현 (프리텐다드 32pt)

## Phase 4: 멀티 플랫폼 배포 [x]

- [x] YouTube API 통합 업로드 모듈 (OAuth2 + 비공개 기본 설정)
- [x] TikTok / Instagram API 업로드 (인증 프로세스 완료)
- [x] 숏폼(Shorts/Reels)용 세로형(9:16) 변환 로직 추가
- [x] 전체 파이프라인 main.py 오케스트레이터 완성
