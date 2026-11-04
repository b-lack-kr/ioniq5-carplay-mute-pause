# IONIQ 5 CarPlay Mute Pause 1.0.0
by blackr

CarPlay에서 음악을 재생할 때 운전대 음소거 버튼으로 차량이 음소거되면 플레이어에 일시정지를 요청합니다. 음소거를 해제한 뒤에는 직접 재생합니다.

**[USB 설치 ZIP 내려받기](https://github.com/ssyeonn/ioniq5-carplay-mute-pause/releases/download/v1.0.0/IONIQ5_CarPlay_Mute_Pause_1.0.0_USB.zip)** · [SHA-256 확인](https://github.com/ssyeonn/ioniq5-carplay-mute-pause/releases/download/v1.0.0/SHA256SUMS.txt)

## 지원 환경

한국 사양 아이오닉 5 Gen5W `NEEV.KOR.S5W_M.V039.001.260902`, NEMESIS, HMG-API 1.0.1 및 활성화된 Hooks가 필요합니다. 이 패키지는 CarPlay의 운전대 음소거 동작만 추가합니다. 동글 무선 연결과 TBT도 설치하려면 음소거 패키지가 포함된 [외장 Wi-Fi 무선 CarPlay 통합판](https://github.com/ssyeonn/ioniq5-external-wirelss-carplay)을 사용하세요.

## 설치와 제거

1. 설치 ZIP을 PC에서 풀고 그 안의 `NEMESIS.data`와 `packages` 폴더를 빈 USB의 최상위에 복사합니다. `packages` 안의 ZIP은 그대로 둡니다.
2. 주차 상태에서 부팅이 끝난 뒤 USB를 차량 데이터 포트에 꽂습니다. NEMESIS 확인창에서 **Yes**를 누르고 설치 완료를 기다립니다.
3. USB를 빼고 내비를 재부팅한 뒤 CarPlay에서 곡을 재생해 시험합니다.
4. 제거할 때는 NEMESIS의 **My Packages → IONIQ 5 CarPlay Mute Pause → Uninstall**을 누르고 내비를 재부팅합니다.

## 소스 빌드

Python 3.9 이상, JDK 17, Android API 34의 `android.jar`, R8/D8 JAR 및 [HMG-API v1.0.1 소스](https://github.com/VysseCodes/HMG-API/tree/v1.0.1)를 준비합니다. 출력 DEX의 최소 API는 19입니다. 아래 예시는 macOS 또는 Linux 셸에서 사용합니다.

```sh
python3 build.py \
  --java-home "$JAVA_HOME" \
  --android-jar "$ANDROID_HOME/platforms/android-34/android.jar" \
  --d8 "$R8_JAR" \
  --hmg-source ../HMG-API-1.0.1 \
  --sign-key ../local-author/mute.key --generate-key \
  --out ../mute-build
```

이미 작성자 개인키와 공개키를 보유한 경우 `--generate-key`를 생략합니다. 저장소와 출력 폴더 외부에 키를 두세요. 자체 빌드는 지정한 작성자 키로 서명하므로 공식 릴리스와 서명 및 파일 해시가 달라집니다. 비어 있는 출력 폴더를 지정하세요.

이 모드는 AGPL-3.0을 따릅니다. [라이선스](LICENSE) · [HMG-API 기여자 고지](HMG-API-NOTICE.md)
