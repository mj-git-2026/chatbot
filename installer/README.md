# SmartOffice Integration Installer

Vue 3 + Vite 기반의 통합 소프트웨어 설치 관리자입니다.

## 주요 기능

- **설치 상태 확인**: 각 소프트웨어의 설치 경로를 내부적으로 세팅하고 파일 존재 여부 체크
- **프로세스 모니터링**: 해당 프로그램이 실행 중인지 프로세스 상태 확인
- **일괄 설치**: 체크박스로 설치할 항목 선택 후 일괄 설치
- **재스캔**: 설치 상태 및 프로세스 실행 여부 재확인
- **진행률 표시**: 다운로드/설치 진행률 실시간 표시
- **자동 실행**: 재부팅 시 자동 실행 옵션

## 설치 경로 설정

`src/data/applications.js`에서 각 소프트웨어의 설치 경로와 프로세스명을 설정합니다.

```js
{
  installPath: 'C:\\Program Files\\SmartOffice\\SmartOfficeManager.exe',
  processName: 'SmartOfficeManager.exe',
}
```

## 실행 방법

```bash
cd installer
npm install
npm run dev
```

## 빌드

```bash
npm run build
```

> **참고**: 실제 파일 시스템 접근 및 프로세스 확인은 Electron 또는 Node.js 백엔드와 연동이 필요합니다.
> 현재 버전은 UI 시뮬레이션으로 동작합니다.
