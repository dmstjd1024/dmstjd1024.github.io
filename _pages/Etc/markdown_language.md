---
title:  "Markdown 문법"

categories:
  - etc
tags:
  - markdown

date: 2025-05-30
thumbnail: "/assets/img/thumbnail/markdown_thumbnail.webp"
---

# Markdown 문법
 게시물 작성하면서, Markdown을 많이 사용할텐데, 요약집처럼 정리해보았다.

제목
======
```markdown
# 제목 1
## 제목 2
### 제목 3
#### 제목 4
##### 제목 5
###### 제목 6
```

# 제목 1
## 제목 2
### 제목 3
#### 제목 4
##### 제목 5
###### 제목 6

`<h1>`, `<h2>`는 다음과 같이 표현할 수도 있습니다.

```markdown
제목 1
======

제목 2
------
```

제목 1
======

제목 2
------


------

강조
======
```markdown
이텔릭체 : *별 기호* 혹은 _언더바_
볼드 :  **별 기호** 혹은 __언더바__
__*이텔릭체*와 볼드__ 혼용 가능

취소선 : ~~물결 기호~~ 
밑줄 : 직접 `<u></u>` <u>밑줄</u> 사용
```

이텔릭체 : *별 기호* 혹은 _언더바_
볼드 :  **별 기호** 혹은 __언더바__
__*이텔릭체*와 볼드__ 혼용 가능

취소선 : ~~물결 기호~~
밑줄 : 직접 `<u></u>` <u>밑줄</u> 사용

-----

목록
======
```markdown
`-`로 시작하는 순서가 없는 목록으로 구분합니다.

1. 순서가 있는 항목
1. 순서가 있는 항목
    - 순서가 없는 항목
    - 순서가 없는 항목
1. 순서가 있는 항목
1. 순서가 있는 항목

- 순서가 없는 항목
- 순서가 없는 항목
    - 순서가 없는 항목
    - 순서가 없는 항목
```

`-`로 시작하는 순서가 없는 목록으로 구분합니다.

1. 순서가 있는 항목
1. 순서가 있는 항목
    - 순서가 없는 항목 (4depth)
    - 순서가 없는 항목 (4depth)
1. 순서가 있는 항목
1. 순서가 있는 항목

- 순서가 없는 항목
- 순서가 없는 항목
    - 순서가 없는 항목
    - 순서가 없는 항목

링크
======
```markdown
[이름](링크)
[이름](링크 "설명")
[이름][참조]

[참조]: 링크
[참조]: 링크 "설명"
```
링크 문법 구조

```markdown
[GOOGLE](https://google.com)

[NAVER](https://naver.com "링크 설명(title)을 작성하세요.")

[상대적 참조](../users/login)

[Dribbble][Dribbble Link]

[GitHub][1]

문서 안에서 [참조 링크]를 그대로 사용할 수도 있습니다.
다음과 같이 문서 내 일반 URL이나 꺾쇠 괄호(`< >`, Angle Brackets)안의 URL은 자동으로 링크를 사용합니다.

구글 홈페이지: https://google.com
네이버 홈페이지: <https://naver.com>

[Dribbble Link]: https://dribbble.com
[1]: https://github.com
[참조 링크]: https://naver.com "네이버로 이동합니다!"

```

[GOOGLE](https://google.com)

[NAVER](https://naver.com "링크 설명(title)을 작성하세요.")

[상대적 참조](../users/login)

[Dribbble][Dribbble Link]

[GitHub][1]

문서 안에서 [참조 링크]를 그대로 사용할 수도 있습니다.
다음과 같이 문서 내 일반 URL이나 꺾쇠 괄호(`< >`, Angle Brackets)안의 URL은 자동으로 링크를 사용합니다.

구글 홈페이지: https://google.com
네이버 홈페이지: <https://naver.com>

[Dribbble Link]: https://dribbble.com
[1]: https://github.com
[참조 링크]: https://naver.com "네이버로 이동합니다!"

이미지
======
```markdown
![대체텍스트](이미지주소)
![대체텍스트](이미지주소 "설명")
![대체텍스트][참조]

[참조]: 이미지주소
[참조]: 이미지주소 "설명"
```

```markdown
![대체 텍스트(Alternative Text)](https://picsum.photos/1000/400 "링크 설명(Title)")
![이미지입니다!][Image]

[Image]: https://picsum.photos/500/300 "이미지입니다!"
```

이미지에 링크 추가
```markdown
[![EUNSEONG.DEV](/assets/img/favicon.webp)](https://dmstjd1024.github.io/)
```

[![EUNSEONG.DEV](/assets/img/favicon.webp)](https://dmstjd1024.github.io/)

코드 강조
======
```markdown
`background` 혹은 `background-image` 속성으로 요소에 배경 이미지를 삽입할 수 있습니다.
```
`background` 혹은 `background-image` 속성으로 요소에 배경 이미지를 삽입할 수 있습니다.

블록
======
````markdown
// 연속 백틱 3개 시작, 종료 구조
```언어이름
내용
```
````

```javascript
function add(a, b = 1) {
  console.log(a, b)
  return a + b
}
```

```bash
$ npm run dev
```

```python
s = "Python syntax highlighting"
print s
```

```plaintext
No language indicated, so no syntax highlighting. 
But let's throw in a <b>tag</b>.
```

백틱 기호 사용
=====
```markdown
\`
<code>\`</code>
```
\`
<code>\`</code>

표
=====

```markdown
| 헤더 | 헤더 | 헤더 |
|---|---|---|
| 셀 | 셀 | 셀 |
| 셀 | 셀 | 셀 |

헤더 | 헤더 | 헤더
---|---|---
셀 | 셀 | 셀
셀 | 셀 | 셀
```

| 값 | 의미 | 기본값 |
|---|:---:|---:|
| `static` | 유형(기준) 없음 / 배치 불가능 | `static` |
| `relative` | 요소 자신을 기준으로 배치 |  |
| `absolute` | 위치 상 부모(조상)요소를 기준으로 배치 |  |
| `fixed` | 브라우저 창을 기준으로 배치 |  |
| `sticky` | 스크롤 영역 기준으로 배치 |  |


| 값 | 의미 |
|---|---|
| 버티컬바 출력 | \| |
| 인라인 코드 강조 | `\|` |

인용문
=====
```markdown
> 인용문 - 남의 말이나 글에서 직접 또는 간접으로 따온 문장.
> _(네이버 국어 사전)_

BREAK!

> 인용문을 작성하세요!
>> 중첩된 인용문(nested blockquote)을 만들 수 있습니다.
>>> 중중첩 인용문 1
>>> 중중첩 인용문 2
>>> 중중첩 인용문 3
```

> 인용문 - 남의 말이나 글에서 직접 또는 간접으로 따온 문장.
> _(네이버 국어 사전)_

BREAK!

> 인용문을 작성하세요!
>> 중첩된 인용문(nested blockquote)을 만들 수 있습니다.
>>> 중중첩 인용문 1
>>> 중중첩 인용문 2
>>> 중중첩 인용문 3

원시 HTML
=====
```markdown
<img width="150" src="http://gstatic.com/webp/gallery/4.jpg" alt="Prunus" title="마크다운은 이미지의 크기를 지정할 수 없으므로, 크기 지정을 위해서는 <img> 태그를 사용해야 합니다.">

![Prunus](http://www.gstatic.com/webp/gallery/4.jpg)
```

<img src="http://gstatic.com/webp/gallery/4.jpg" alt="Prunus" title="마크다운은 이미지의 크기를 지정할 수 없으므로, 크기 지정을 위해서는 <img> 태그를 사용해야 합니다." height="200">

![Prunus](http://www.gstatic.com/webp/gallery/4.jpg)

수평선
=====
```markdown
---

***

___
```

---

***

___


줄바꿈
=====
```markdown
동해물과 백두산이 마르고 닳도록 
하느님이 보우하사 우리나라 만세
무궁화 삼천리 화려 강산    <!--띄어쓰기 2번--> 대한
사람 대한으로 길이 보전하세<br>
끝!
```

동해물과 백두산이 마르고 닳도록
하느님이 보우하사 우리나라 만세
무궁화 삼천리 화려 강산    <!--띄어쓰기 2번--> 대한
사람 대한으로 길이 보전하세<br>
끝!

주석
=====
```markdown
-- 시작 --
[//]: # (주석은 이렇게 작성합니다.)
[//]: # (이 주석은 렌더링되지 않습니다.)


[//]: # (주석은 이렇게 작성합니다.)
[//]: # (이 주석은 렌더링되지 않습니다.)
-- 끝 --
```

-- 시작 --

[//]: # (주석은 이렇게 작성합니다.)
[//]: # (이 주석은 렌더링되지 않습니다.)


[//]: # (주석은 이렇게 작성합니다.)
[//]: # (이 주석은 렌더링되지 않습니다.)

-- 끝 --

ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
 
