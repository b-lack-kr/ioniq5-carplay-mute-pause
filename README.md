# IONIQ 5 CarPlay Mute Pause 1.1.1

by blackr

CarPlay 음악을 재생하다가 차량 음소거 버튼을 누르면 일시정지합니다. **음소거를 해제하거나 볼륨을 조절해 음소거가 풀리면, 이 모드가 멈춘 음악을 다시 재생합니다.** 음소거 전부터 일시정지돼 있던 음악은 자동 재생하지 않습니다.

**[USB 설치 ZIP](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.1/IONIQ5_CarPlay_Mute_Pause_1.1.1_USB.zip)** · [소스 ZIP](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.1/IONIQ5_CarPlay_Mute_Pause_1.1.1_SOURCE.zip) · [SHA-256](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/download/v1.1.1/SHA256SUMS.txt) · [변경 기록](CHANGELOG.md)

## 지원 환경

한국 사양 아이오닉 5 Gen5W `NEEV.KOR.S5W_M.V039.001.260902`, NEMESIS, **HMG-API 1.0.1 이상** 및 해당 DiPO 훅 맵과 활성화된 Hooks가 필요합니다. HMG-API 1.0.2 이상도 버전 조건을 충족하므로 1.0.1로 내릴 필요가 없습니다. 정식 숫자 버전(`major.minor.patch`)만 허용하며, 1.0.1 미만·잘못된 형식·시험판 접미사가 붙은 버전은 거부합니다. 대상 펌웨어·서명·Hooks 검사는 그대로 유지합니다.

음소거·자동 재생 기능은 1.1.0과 동일합니다. 2026년 11월 5일 기준 1.1.0을 아이오닉 5 23MY와 TP-Link Archer T3U Nano에서 차량 소유자가 확인했습니다. 1.1.1의 변경은 설치 버전 검사와 업데이트 허용 목록이며, 모든 상위 HMG-API에서 실차 검증했다는 의미는 아닙니다.

이 패키지는 음소거 동작만 설치·업데이트합니다. 동글 무선 연결과 TBT는 [무선 CarPlay 1.0.2](https://github.com/b-lack-kr/ioniq5-external-wirelss-carplay/releases/tag/v1.0.2)를 **별도로 설치**하세요. 두 패키지는 각각 설치·업데이트·제거할 수 있습니다.

**CarPlay 전용이며 Android Auto는 지원하지 않습니다.** 동일 펌웨어라도 다른 CarPlay 패키지와 함께 사용하는 조합은 실차 검증하지 않았습니다.

## 설치·업데이트·제거

GitHub [1.1.1 릴리스](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/tag/v1.1.1)의 **Assets**에서 **`IONIQ5_CarPlay_Mute_Pause_1.1.1_USB.zip`**을 다운로드하세요. `SOURCE.zip`이나 GitHub의 `Source code` ZIP은 차량 설치용 파일이 아닙니다.

1. USB의 기존 설치 파일과 기록을 백업합니다. 설치 ZIP을 풀고 `NEMESIS.data`와 `packages` 두 항목을 USB 최상위에 복사합니다. `packages` 안의 ZIP은 풀지 않습니다.
2. 주차 상태에서 내비 부팅이 끝나면 USB를 차량 데이터 포트에 꽂습니다. NEMESIS에서 **Yes**를 누르고 **Operation completed successfully**까지 기다립니다.
3. USB를 빼고 내비를 재부팅합니다. 기존 음소거 1.0.0·1.1.0은 삭제하지 않고 업데이트할 수 있으며, 꺼짐 상태와 설정을 유지합니다. 특히 HMG-API를 1.0.2 이상으로 올린 상태에서는 이전 음소거 패키지의 제거 검사에 막힐 수 있으므로 **삭제하지 말고 1.1.1로 업데이트**하세요. CarPlay 본체는 재설치하지 않아도 됩니다.
4. 제거하려면 NEMESIS의 **My Packages → IONIQ 5 CarPlay Mute Pause → Uninstall**을 누른 뒤 내비를 재부팅합니다.

## 동작 범위

- 음소거 버튼과 볼륨 조절 후 실제 음소거 상태를 확인합니다. 빠른 연속 입력으로 재생 명령이 중복되지 않게 처리합니다.
- 휴대전화의 일시정지 응답보다 음소거 해제가 먼저 도착하는 경우도 기다렸다가 재개합니다.
- CarPlay 연결이 바뀌거나 확인된 수동 미디어 키 입력, 통화·Siri·다른 오디오 모드가 있으면 자동 재개 예약을 취소합니다.
- 휴대전화에서 이미 멈춘 곡에 다시 일시정지를 누르는 등 모든 조작 의도를 차량의 재생 상태만으로 구분할 수는 없습니다.

[소스 빌드·검증 안내](BUILDING.md)

이 모드는 AGPL-3.0을 따릅니다. [라이선스](LICENSE) · [HMG-API 기여자 고지](HMG-API-NOTICE.md)
