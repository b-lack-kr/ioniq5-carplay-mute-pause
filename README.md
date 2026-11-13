# CarPlay Mute Pause 1.1.2

by blackr

차량에서 음소거하면 CarPlay 음악을 일시정지하고, 음소거 해제나 볼륨 조절로 소리가 다시 켜지면 이 모드가 멈춘 음악을 다시 재생합니다. 음소거 전부터 일시정지돼 있던 음악은 자동 재생하지 않습니다.

[1.1.2 릴리스 및 USB 설치 파일](https://github.com/b-lack-kr/ioniq5-carplay-mute-pause/releases/tag/v1.1.2) · [변경 기록](CHANGELOG.md)

## 지원 환경

NEMESIS, HMG-API 1.0.1 이상과 활성화된 Hooks가 필요합니다. 1.1.2는 차량 모델명 제한을 제거하지만 `tcc803x`, Android 4.4.2, 호환되는 DiPO 빌드 및 HMG-API 훅 맵 검사는 그대로 유지합니다. 다른 차종 또는 펌웨어에서 작동이 확인된 것은 아닙니다. CarPlay 전용이며 Android Auto 동작은 확인되지 않았습니다.

아이오닉 5 23MY에서 기존 음소거 기능이 확인됐습니다. 다른 CarPlay 패키지와의 조합은 별도 확인이 필요합니다.

## 설치

1. 릴리스의 `CarPlay-Mute-Pause-1.1.2-compatible-USB.zip`을 다운로드합니다. USB를 백업하고 ZIP 안의 `NEMESIS.data`와 `packages`를 FAT32 또는 exFAT USB 최상위에 압축 해제합니다. `packages` 안의 ZIP은 풀지 않습니다.
2. 주차 후 차량 내비게이션이 부팅되면 USB를 데이터 포트에 꽂고 NEMESIS 확인 창에서 Yes를 누릅니다. 설치가 끝나면 내비게이션을 재부팅합니다.
3. 기존 관련 모드를 삭제한 후 설치하는 경우 HMG-API에서 Apply changes를 눌러 적용하고 내비게이션을 재부팅한 뒤 설치합니다. NEMESIS와 HMG-API 자체는 삭제하지 않습니다.

동글 무선 연결은 별도이며, 올인원에 이미 이 패키지가 있으면 중복 설치할 필요가 없습니다. [올인원 릴리스](https://github.com/b-lack-kr/ioniq5-external-wirelss-carplay/releases/tag/v1.1.3)

[소스 빌드 안내](BUILDING.md) · [AGPL-3.0 라이선스](LICENSE) · [HMG-API 기여자 고지](HMG-API-NOTICE.md)
