"""
YouTube OAuth2 연결 테스트
music-publisher에서 가져온 client_secret.json으로 인증 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.youtube_uploader import YouTubeUploader


def main():
    print("--- YouTube OAuth2 연결 테스트 ---")
    print("1. client_secret.json 로드 중...")

    uploader = YouTubeUploader()

    print("2. OAuth2 인증 시작 (브라우저가 열립니다)...")
    print("   → Google 계정으로 로그인 후 권한 허용을 클릭해 주세요.")
    print("   → 처음 한 번만 필요하며 이후 자동 토큰 갱신됩니다.\n")

    try:
        youtube = uploader.authenticate()
        # 사용자 채널 정보 가져오기 (quota 소모 최소: read only)
        response = youtube.channels().list(
            part="snippet,statistics",
            mine=True
        ).execute()

        if response.get("items"):
            ch = response["items"][0]
            name = ch["snippet"]["title"]
            subs = ch["statistics"].get("subscriberCount", "N/A")
            videos = ch["statistics"].get("videoCount", "N/A")
            print(f"✅ 인증 성공!")
            print(f"   채널명: {name}")
            print(f"   구독자: {subs}명")
            print(f"   영상 수: {videos}개")
            print(f"\n   토큰이 'youtube_token.pickle'에 저장되었습니다.")
            print(f"   이제 AutoBard에서 YouTube 업로드가 가능합니다!")
        else:
            print("⚠️ 인증은 성공했지만 채널 정보를 가져올 수 없습니다.")

    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
