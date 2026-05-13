# 11주차 실습 기록

## 오늘 한 것

- Pyinstaller 설치 및 빌드
- `resource_path(_asset)` 함수 적용
- `--add-data` 옵션으로 `sprites`, `sounds`, `backgrounds` 포함
- `.exe` 실행 확인

---

## `resource_path()` 를 써야 하는 이유

`resource_path(_asset)`을 써야 하는 이유는 제 컴퓨터에서의 파일 위치, 남이 exe 파일을 실행될 때의 파일 위치가 다르기 때문입니다.

개발을 할 때에는 모든 파일이 내 프로젝트 폴더 안에 얌전히 있지만, exe로 실행하였을 때에는 Pyinstaller가 게임 실행에 필요한 파일들을 사용자의 임시 폴더인 `Temp`에 압축을 풉니다. 그러나 프로그램 내부의 `__file__` 변수는 여전히 엉뚱한 곳을 바라보기 때문에 압축이 풀린 진짜 이미지 파일들이 들어있는 임시 폴더를 보지 못합니다.

그래서 `resource_path(_asset)` 함수가 하는 일은 두 상황을 모두 체크하는 역할을 합니다.

`if hasattr(sys, '_MEIPASS'):` 으로 구분하여 지금 exe에서 실행 중이니 임시 폴더에서 파일을 찾으라는 명령으로 바꿉니다.

때문에 이 함수를 쓰지 않으면 사용자가 게임을 실행해도 EXE 파일 바로 옆에 asset을 찾으려 해도 없기 때문에 오류가 생겨 바로 꺼지게 됩니다.

---

## 빌드 명령어

```bash
pyinstaller --noconfirm --onedir -w --add-data "sprites;sprites" --add-data "sounds;sounds" --add-data "backgrounds;backgrounds" parryer.py
```

| 옵션 | 설명 |
|------|------|
| `--noconfirm` | 묻지 않고 진행하라. |
| `--onedir` | 한 폴더에 모아라. |
| `-w` | 터미널을 숨겨라. |
| `--name="Parryer"` | 프로그램의 이름은 Parryer로 하라. |
| `--add-data "폴더명;폴더명"` | 외부 파일을 이 경로로 포함하라. |
| `parryer.py` | 이 파일을 빌드업하라. |

---

## AI 활용 내역

비교 대상 명령어:

```bash
# 첫 번째 명령어
pyinstaller --noconfirm --onedir -w --add-data "sprites;sprites" --add-data "sounds;sounds" --add-data "backgrounds;backgrounds" parryer.py
```

```bash
# 두 번째 명령어
pyinstaller --onefile --windowed --add-data "assets;assets" --name=MyGame game.py
```

**Q. 두 파일의 주요 차이점은 무엇인가요?**

두 명령어의 가장 핵심적인 차이는 결과물이 파일 하나로 나오느냐(`--onefile`), 아니면 폴더 형태로 나오느냐(`--onedir`)입니다.

| 구분 | 첫 번째 명령어 (`--onedir`) | 두 번째 명령어 (`--onefile`) |
|------|---------------------------|---------------------------|
| **형태** | `parryer` 폴더 안에 EXE와 여러 라이브러리 | `MyGame.exe` 파일 딱 하나 |
| **실행 속도** | 빠름 (압축이 풀려 있어 바로 실행됨) | 느림 (실행할 때마다 압축을 풀기 때문) |
| **디버깅** | 쉬움 (`_internal` 폴더에서 에셋 확인 가능) | 어려움 (내부 파일 구조 확인 불가) |
| **관리** | 조금 복잡함 (폴더 전체를 압축해서 전달해야 함) | 깔끔함 (파일 한 개만 전달하면 됨) |
| **에셋** | `sprites`, `sounds` 등 세부 폴더별로 관리 | `assets` 폴더 하나로 묶어서 관리 |

**Q. 어떤 상황에 무엇을 써야 할까요?**

- **과제 제출용 / 최종 배포용:** 만약 "파일 하나로 깔끔하게 내라"는 조건이 있다면 `--onefile`이 좋습니다.
- **개발 단계 / 고사양 게임:** 에러를 잡고 있거나, 이미지/사운드 파일이 수십 메가바이트(MB) 이상이라면 `--onedir`이 훨씬 쾌적합니다.
