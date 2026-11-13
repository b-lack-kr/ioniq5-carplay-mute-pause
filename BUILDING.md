# 소스 빌드와 검증


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

아래 설치 검사는 1.1.1을 대상으로 작성된 과거 테스트입니다. HMG 엔진의 호스트 모드와 모의 Android IPC를 사용하며 1.1.2나 다른 차종의 실제 설치를 검증하지 않습니다. 공식 1.1.1·1.1.0·1.0.0 설치 ZIP과 자신이 보유한 대상 펌웨어의 `HKMC_DiPO.odex`를 입력으로 사용합니다. 차량·USB·작성자 키에는 접근하지 않습니다.

```sh
python3 tests/test_upgrade.py \
  --archive ../IONIQ5_CarPlay_Mute_Pause_1.1.1_USB.zip \
  --old-archive ../IONIQ5_CarPlay_Mute_Pause_1.0.0_USB.zip \
  --old-110-archive ../IONIQ5_CarPlay_Mute_Pause_1.1.0_USB.zip \
  --java-home "$JAVA_HOME" --hmg-source ../HMG-API-1.0.1 \
  --firmware-odex ../owned-firmware/HKMC_DiPO.odex
```

내부 개발용 이전 서명본을 별도로 가진 경우 `--old-unbranded`로 추가할 수 있습니다. 생략하면 해당 한 사례만 건너뜁니다.

