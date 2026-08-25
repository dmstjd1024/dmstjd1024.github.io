---
title: "도커 교과서 6장"

categories:
 - Docker
tags:
  - Docker

date: 2026-08-19
thumbnail: "/assets/img/thumbnail/docker_thumbnail.png"
---
도커 볼륨을 이용한 퍼시스턴트 스토리지
=====
-----

지금까지는 컨테이너를 만들고 지우는 걸 아무렇지 않게 했다.
그런데 **DB처럼 데이터를 보관해야 하는 프로그램**이라면 이야기가 달라진다.

## 컨테이너 속 데이터가 사라지는 이유

컨테이너 안에 파일을 하나 만들어보자.

```docker
docker container run --name data-test -d diamol/base sleep 3600
docker container exec data-test sh -c 'echo "중요한 데이터" > /data.txt'
docker container exec data-test cat /data.txt
```

```
중요한 데이터
```

잘 저장된 것처럼 보인다. 이제 컨테이너를 지우고 **같은 이미지로 다시 실행**해보자.

```docker
docker container rm -f data-test
docker container run --rm diamol/base cat /data.txt
```

```
cat: can't open '/data.txt': No such file or directory
```

**파일이 사라졌다.**

3장에서 이미지 레이어는 **읽기 전용**이라고 했다.
그럼 컨테이너에서 파일을 어떻게 쓸 수 있었을까?

컨테이너가 시작될 때 도커는 이미지 레이어들 위에
**쓰기 가능한 레이어(writable layer)를 하나 더 얹는다.**

```
[ 쓰기 가능 레이어 ]  ← 컨테이너가 만든 파일은 여기에
[ 이미지 레이어 3  ]  ← 읽기 전용
[ 이미지 레이어 2  ]  ← 읽기 전용
[ 이미지 레이어 1  ]  ← 읽기 전용
```

이 쓰기 레이어는 **컨테이너와 수명을 같이한다.**
컨테이너를 지우면 쓰기 레이어도 같이 지워지고, 그 안의 데이터도 사라진다.

> 이미지 레이어는 여러 컨테이너가 공유하기 때문에 읽기 전용이어야 한다.
> 한 컨테이너가 이미지를 고칠 수 있다면 다른 컨테이너까지 영향을 받는다.

그래서 데이터를 남기려면 **컨테이너 바깥에 저장**해야 한다.
방법은 두 가지다. **볼륨**과 **마운트**.

## 도커 볼륨을 사용하는 컨테이너 실행하기

볼륨(Volume)은 **도커가 관리하는 저장 공간**이다.
컨테이너와 별개로 존재하기 때문에 컨테이너를 지워도 남는다.

```docker
docker volume create verify-vol
```

컨테이너를 실행할 때 `-v [볼륨명]:[컨테이너 경로]` 로 연결한다.

```docker
docker container run --rm -v verify-vol:/app/data diamol/base \
  sh -c 'echo "볼륨에 저장한 데이터" > /app/data/data.txt'
```

`--rm` 옵션 때문에 이 컨테이너는 **실행이 끝나자마자 삭제**됐다.
그런데도 데이터가 남아 있는지, 완전히 새 컨테이너로 확인해보자.

```docker
docker container run --rm -v verify-vol:/app/data diamol/base cat /app/data/data.txt
```

```
볼륨에 저장한 데이터
```

**살아남았다.** 컨테이너는 두 번 다 사라졌지만 볼륨의 파일은 그대로다.

### 볼륨은 어디에 저장될까

```docker
docker volume inspect verify-vol
```

```json
{
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/verify-vol/_data",
    "Name": "verify-vol",
    "Scope": "local"
}
```

`Mountpoint` 가 실제 저장 위치다.
다만 **맥이나 윈도에서는 이 경로로 직접 찾아갈 수 없다.**
도커가 리눅스 가상 머신 안에서 돌기 때문에, 저 경로는 VM 내부의 경로다.

즉 볼륨은 **도커에게 맡기고 도커 명령으로만 다루는 저장소**라고 보면 된다.

### Dockerfile 의 VOLUME 인스트럭션

이미지 자체에 "이 경로는 볼륨으로 쓰겠다"고 선언할 수도 있다.

```docker
FROM diamol/base
VOLUME /app/data
```

이 이미지로 컨테이너를 실행하면, `-v` 를 안 써도 볼륨이 자동으로 만들어진다.

```docker
docker container run --name vol-auto -d vol-demo sleep 60
docker volume ls
```

```
DRIVER    VOLUME NAME
local     aa13676e6d257959a28c56e39a14137c2f41332eb8b5d0a1d47991a063c37aeb
local     verify-vol
```

이름이 **해시값인 볼륨**이 생겼다. 이를 익명 볼륨이라고 한다.

여기에 함정이 있다. 컨테이너를 지워도 이 볼륨은 **남는다.**

```docker
docker container rm -f vol-auto
docker volume ls    # 해시 볼륨이 여전히 있다
```

컨테이너를 만들고 지우기를 반복하면 이런 볼륨이 계속 쌓인다.
쓰지 않는 볼륨은 아래 명령으로 정리한다.

```docker
docker volume prune
```

## 파일 시스템 마운트를 사용하는 컨테이너 실행하기

바인드 마운트(bind mount)는 **호스트 컴퓨터의 디렉터리를 컨테이너에 직접 연결**한다.
볼륨과 달리 내가 아는 경로를 쓰기 때문에, 파일을 직접 열어보고 고칠 수 있다.

사용법은 볼륨과 같은 `-v` 인데, 볼륨 이름 대신 **경로**를 적는다.

```docker
docker container run --rm -v "$(pwd)/hostdir:/app/data" diamol/base \
  cat /app/data/from-host.txt
```

```
호스트에서 만든 파일
```

호스트에서 만든 파일이 컨테이너 안에서 그대로 보인다.
반대 방향도 된다.

```docker
docker container run --rm -v "$(pwd)/hostdir:/app/data" diamol/base \
  sh -c 'echo "컨테이너가 만든 파일" > /app/data/from-container.txt'

ls hostdir
```

```
from-container.txt  from-host.txt
```

컨테이너가 만든 파일이 **호스트에 그대로 나타났다.**
개발할 때 소스 코드를 마운트해두면, 이미지를 다시 빌드하지 않아도 수정이 반영되는 이유다.

### 읽기 전용으로 마운트하기

컨테이너가 호스트 파일을 건드리면 안 될 때는 `:ro` 를 붙인다.

```docker
docker container run --rm -v "$(pwd)/hostdir:/app/data:ro" diamol/base \
  sh -c 'echo "쓰기 시도" > /app/data/should-fail.txt'
```

```
sh: can't create /app/data/should-fail.txt: Read-only file system
```

설정 파일처럼 **읽기만 하면 되는 것**은 이렇게 막아두는 편이 안전하다.

### 볼륨과 바인드 마운트 비교

| | 볼륨(Volume) | 바인드 마운트(Bind Mount) |
|---|---|---|
| 관리 주체 | 도커 | 사용자 |
| 위치 | 도커가 정한 경로 | 내가 지정한 호스트 경로 |
| 호스트에서 접근 | 맥/윈도에서는 어려움 | 그냥 열면 됨 |
| 주 용도 | 운영 환경의 데이터 보관 | 개발 중 소스 코드 연결 |

## 파일 시스템 마운트의 한계점

마운트는 편리하지만 알아둬야 할 동작이 있다.

<div class="diagram">
{% include diagrams/docker6--mount-shadow.svg %}
</div>

### 1. 마운트하면 원래 있던 내용이 가려진다

컨테이너에 원래 있던 디렉터리 위에 마운트하면 어떻게 될까?

```docker
# 마운트 없이 /etc 를 본 경우
docker container run --rm diamol/base ls /etc
```

```
TZ  alpine-release  apk  ca-certificates  conf.d  crontabs  fstab ...
```

```docker
# /etc 에 호스트 디렉터리를 마운트한 경우
docker container run --rm -v "$(pwd)/hostdir:/etc" diamol/base ls /etc
```

```
from-container.txt  from-host.txt  hostname  hosts  resolv.conf
```

**원래 있던 파일이 전부 사라졌다.**
정확히는 지워진 게 아니라 **가려진 것**이다. 마운트를 빼면 다시 보인다.

(`hostname`, `hosts`, `resolv.conf` 는 도커가 컨테이너마다 따로 넣어주는 파일이다.)

### 2. 파일 하나만 마운트하면 가려지지 않는다

디렉터리가 아니라 **파일 하나**를 마운트하면 결과가 다르다.

```docker
docker container run --rm -v "$(pwd)/hostdir/from-host.txt:/etc/from-host.txt" \
  diamol/base ls /etc
```

```
TZ  alpine-release  apk  ca-certificates  conf.d ...
```

기존 파일들이 **그대로 남아 있다.**
설정 파일 하나만 바꿔 끼우고 싶을 때 쓰는 방법이다.

> 정리하면 — **디렉터리 마운트는 통째로 덮고, 파일 마운트는 그 파일만 끼워 넣는다.**

### 3. 그 외 주의할 점

- 호스트에 없는 경로를 마운트하면 도커가 **빈 디렉터리를 만들어버린다** (오타 주의)
- 리눅스에서는 호스트 파일의 소유자·권한 때문에 컨테이너가 쓰기에 실패할 수 있다
- 여러 컨테이너가 같은 경로에 동시에 쓰면 충돌한다 — 도커가 막아주지 않는다

## 컨테이너의 파일 시스템은 어떻게 만들어지는가?

지금까지 나온 걸 합치면 컨테이너의 파일 시스템은 이렇게 구성된다.

```
컨테이너에서 보이는 하나의 파일 시스템
├── 이미지 레이어      (읽기 전용, 여러 컨테이너가 공유)
├── 쓰기 가능 레이어   (컨테이너와 함께 사라짐)
├── 볼륨               (도커가 관리, 컨테이너보다 오래 삶)
└── 바인드 마운트      (호스트 디렉터리, 컨테이너와 무관하게 존재)
```

컨테이너 안에서는 이 모두가 **하나의 디스크처럼 보인다.**
하지만 수명은 제각각이다. 그래서 애플리케이션을 컨테이너로 옮길 때
**"이 데이터가 사라져도 되는가"** 를 경로마다 판단해야 한다.

| 데이터 성격 | 저장 위치 |
|---|---|
| 재시작하면 다시 만들어져도 되는 것 (캐시, 임시 파일) | 쓰기 레이어 그대로 |
| 보관해야 하는 것 (DB 데이터, 업로드 파일) | 볼륨 |
| 호스트와 주고받아야 하는 것 (개발 중 소스, 설정 파일) | 바인드 마운트 |

## 정리

- 컨테이너의 쓰기 레이어는 **컨테이너와 함께 사라진다** — 데이터를 남기려면 바깥에 저장한다
- **볼륨**은 도커가 관리하는 저장소. 컨테이너를 지워도 남는다
- **바인드 마운트**는 호스트 디렉터리 직접 연결. 개발 중 소스 코드 연결에 유용하다
- `VOLUME` 인스트럭션은 익명 볼륨을 만들고, **컨테이너를 지워도 남으니** 가끔 `docker volume prune` 한다
- 디렉터리를 마운트하면 원래 내용이 **가려지고**, 파일 하나만 마운트하면 그 파일만 바뀐다
