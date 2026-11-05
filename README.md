# IONIQ 5 CarPlay Mute Pause 1.1.0

by blackr

CarPlay 음악을 재생하다가 차량 음소거 버튼을 누르면 일시정지합니다. **음소거를 해제하거나 볼륨을 조절해 음소거가 풀리면, 이 모드가 멈춘 음악을 다시 재생합니다.** 음소거 전부터 일시정지돼 있던 음악은 자동 재생하지 않습니다.

**[USB 설치 ZIP](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.0/IONIQ5_CarPlay_Mute_Pause_1.1.0_USB.zip)** · [소스 ZIP](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.0/IONIQ5_CarPlay_Mute_Pause_1.1.0_SOURCE.zip) · [SHA-256](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.0/SHA256SUMS.txt) · [변경 기록](CHANGELOG.md)

## 지원 환경

한국 사양 아이오닉 5 Gen5W `NEEV.KOR.S5W_M.V039.001.260902`, NEMESIS, HMG-API 1.0.1 및 해당 DiPO 훅 맵과 활성화된 Hooks가 필요합니다. 2026년 11월 5일 기준 아이오닉 5 23MY와 TP-Link Archer T3U Nano를 사용하는 차량 소유자에게서 실차 정상 동작 확인을 받았습니다. 다른 차량과 펌웨어에 대한 검증을 의미하지 않습니다.

이 패키지는 음소거 동작만 설치·업데이트합니다. 동글 무선 연결과 TBT도 설치하려면 같은 음소거 1.1.0이 포함된 [무선 CarPlay 통합판](https://github.com/b-lack-kr/ioniq5-external-wirelss-carplay/releases/tag/v1.0.1)을 사용하세요.

## 설치·업데이트·제거

1. USB의 기존 설치 파일과 기록을 백업합니다. 설치 ZIP을 풀고 `NEMESIS.data`와 `packages` 두 항목을 USB 최상위에 복사합니다. `packages` 안의 ZIP은 풀지 않습니다.
2. 주차 상태에서 내비 부팅이 끝나면 USB를 차량 데이터 포트에 꽂습니다. NEMESIS에서 **Yes**를 누르고 **Operation completed successfully**까지 기다립니다.
3. USB를 빼고 내비를 재부팅합니다. 기존 음소거 1.0.0은 삭제하지 않고 업데이트할 수 있으며, 꺼짐 상태와 설정을 유지합니다. 기존 음소거 패키지를 삭제한 뒤 신규 설치하는 것도 가능합니다. CarPlay 본체는 재설치하지 않아도 됩니다.
4. 제거하려면 NEMESIS의 **My Packages → IONIQ 5 CarPlay Mute Pause → Uninstall**을 누른 뒤 내비를 재부팅합니다.

## 동작 범위

- 음소거 버튼과 볼륨 조절 후 실제 음소거 상태를 확인합니다. 빠른 연속 입력으로 재생 명령이 중복되지 않게 처리합니다.
- 휴대전화의 일시정지 응답보다 음소거 해제가 먼저 도착하는 경우도 기다렸다가 재개합니다.
- CarPlay 연결이 바뀌거나 확인된 수동 미디어 키 입력, 통화·Siri·다른 오디오 모드가 있으면 자동 재개 예약을 취소합니다.
- 휴대전화에서 이미 멈춘 곡에 다시 일시정지를 누르는 등 모든 조작 의도를 차량의 재생 상태만으로 구분할 수는 없습니다.

## 소스 빌드

Python 3.9 이상, JDK 17, Android API 34의 `android.jar`, R8/D8 JAR 및 [HMG-API v1.0.1 소스](https://github.com/VysseCodes/HMG-API/tree/v1.0.1)를 준비합니다. 출력 DEX의 최소 API는 19입니다.

```sh
python3 build.py \
  --java-home "$JAVA_HOME" \
  --android-jar "$ANDROID_HOME/platforms/android-34/android.jar" \
  --d8 "$R8_JAR" \
  --hmg-source ../HMG-API-1.0.1 \
  --sign-key ../local-author/mute.key --generate-key \
  --out ../mute-build
```

이미 작성자 키를 보유한 경우 `--generate-key`를 생략합니다. 키는 저장소와 출력 폴더 밖에 두세요. 자체 빌드는 지정한 키로 서명하므로 공식 릴리스와 서명 및 해시가 다릅니다. 비어 있는 출력 폴더를 지정하세요.

## 검증

`tests/PauseGateTest.java`는 시간·음소거·재생 상태를 모의해 56개 조건을 검사합니다. `tests/MutePauseTest.java`는 대상 메서드 접근과 물리 키 구분을 확인합니다. 차량 없이 JDK로 실행할 수 있습니다.

```sh
mkdir -p ../mute-tests
javac --release 8 -d ../mute-tests \
  mute/java/kr/ioniq5/mutepause/PauseGate.java \
  mute/java/kr/ioniq5/mutepause/Player.java \
  mute/java/kr/ioniq5/mutepause/KeyStroke.java \
  tests/PauseGateTest.java tests/MutePauseTest.java \
  tests/com/daudio/app/dipo/service/DipoService.java
java -cp ../mute-tests kr.ioniq5.mutepause.PauseGateTest
java -cp ../mute-tests kr.ioniq5.mutepause.MutePauseTest
```

설치 검사는 HMG 엔진의 호스트 모드를 사용하고 Android IPC는 모의합니다. 공식 1.0.0·1.1.0 설치 ZIP과 자신이 보유한 대상 펌웨어의 `HKMC_DiPO.odex`를 입력으로 사용합니다. 차량·USB·작성자 키에는 접근하지 않습니다.

```sh
python3 tests/test_upgrade.py \
  --archive ../IONIQ5_CarPlay_Mute_Pause_1.1.0_USB.zip \
  --old-archive ../IONIQ5_CarPlay_Mute_Pause_1.0.0_USB.zip \
  --java-home "$JAVA_HOME" --hmg-source ../HMG-API-1.0.1 \
  --firmware-odex ../owned-firmware/HKMC_DiPO.odex
```

내부 개발용 이전 서명본을 별도로 가진 경우 `--old-unbranded`로 추가할 수 있습니다. 생략하면 해당 한 사례만 건너뜁니다.

이 모드는 AGPL-3.0을 따릅니다. [라이선스](LICENSE) · [HMG-API 기여자 고지](HMG-API-NOTICE.md)
