---
title:  "JVM, 자바 코드 실행 과정"

categories:
  - java
tags:
  - java
  - 백기선 Live Study

date: 2023-01-06
thumbnail: "/assets/img/thumbnail/java_thumbnail.png"
---

# 목적

---


자바 소스 파일(.java)을 JVM으로 실행하는 과정 이해하기


남궁성님이 출판하신 JAVA의 정석를 기반으로 작성하려고 한다.



# 학습할 것




### JVM이란 무엇인가
---

JVM이란 java를 실행하기 위한 가상 머신이다. 여기서 '가상머신' 대신 '가상 컴퓨터'라고 부르는게 이해하기 좋다.

자바로 작성된 애플리케이션은 모두 이 가상 컴퓨터에서 실행되기 때문에 Java Application이 실행되기 위해선 반드시 JVM이 필요하다.

일반 Application의 코드는 OS만 거쳐 하드웨어로 전달되는데 Java Application은 JVM을 한 번 더 거치며 실행 될 때 하드웨어에 맞게 컴파일을 진행한다.

그렇다고 JVM 하나로 통합되는게 아니라 각 OS에 맞는 JVM이 실행된다 (ex : Window용 JVM, Macintosh용 JVM, Linux용 JVM )

이래서 자바는 Write once, run anywhere (한번 작성시 어디서든 실행된다.) 라는 장점이 있다.

### 컴파일 하는 방법

---
개발 툴을 이용해 .java 파일을 생성하고 build시 java Compiler의 javac라는 명령어를 사용해 .class 파일을 생성합니다. (이 .class는 파일은 아직은 어셈블리어가 아닌 자바 바이트 코드 입니다)
이 파일은 클래스 로더에 의해서 JVM 내로 로드되고 Execution Engine에 의해 기계어로 해석되어 메모리에 배치되게 됩니다. 그리고 Stack Area, Method Heap Area, PC Register Area 에 올라간 파일들은 클래스 메소드 호출이 발생하면 영역의 Method들 정보를 읽어 매개변수, 지역변수 리턴값등이 Stack에 의해 처리되게 됩니다. 그리고 메소드 실행 끝나면 Stack영역에서는 자동으로 제거됩니다. 이후 Garbage Collector가 실행되어 메모리를 정리해주게 됩니다.


### 바이트코드란 무엇인가
---

자바의 바이트 코드란 JVM이 이해할 수 있는 언어로 변환된 자바 소스 코드이며, 자바 컴파일러에 의해 변환되는 코드의 명령어 크기가 1바이트라서 자바 바이트 코드라고 불리고 있다.

바이트 코드의 확장자는 .class이며 가상머신만 설치되어 있다면, 어떤 운영체제에서라도 실행될 수 있습니다.



### JIT 컴파일러란 무엇이며 어떻게 동작하는지
---

일단 JIT(Just In Time) 컴파일러란 동적 번역 이라 할 수 있으며 실제로 프로그램을 실행하는 기점에서 기계어로 번역하는 컴파일러이다.

여기서 원래 컴퓨터 프로그램을 만드는 방법은 2가지가 있는데 인터프리트 방식과 컴파일 방식으로 나눌 수 있다.

Interpreter는 실행 중 프로그래밍 언어를 읽어가면서 해당 기능에 대응하는 기계어 코드를 실행한다.

반명 정적 compile은 실행하기 전에 프로그램 코드를 기계어로 번역한다.

여기서 JIT는 두가지를 혼합한 방식이라고 볼 수 있는데 실행시점에서 Interpreter 방식으로 기계어 코드를 생성하면서 그 코드를 '캐싱'하여 같은 함수가 여러번 불릴 때 캐싱된 데이터를 사용해 매번 기계어 코드를 생성하는 것을 방지한다.

이래서 한번만 실행되는 코드는 Interpreter 방식이 유리하며 JVM은 메소드가 얼마나 자주 수행되는 지를 체크하여 컴파일을 수행한다.



### JVM 구성 요소
---

JVM은 ClassLoader, Execution Engine, RuntimeData Areas로 구성된다.

- ClassLoader 란

JVM 내로 클래스 파일을 load하고 link를 통해 배치를 수행하는 모듈로 Runtime 시에 동적으로 클래스를 로드한다.

자바는 동적코드, 컴파일 타임이 아니라 런타임에 참조한다.

즉 ,클래스를 처음으로 참조할 때 해당 클래스를 load하고 link한다.

- Execution Engine 란

class loader를 통해 배치된 클래스를 실행시킨다.

클래스 파일(바이트 코드)은 비교적 인간이 보기 쉬운 형태이기 때문에 기계가 실행할 수 있는 형태로 변경시키는데 이때, JIT와 Interpreter 두가지 방식을 사용한다.

- Garbage Collector

동적으로 할당된 메모리 중 사용되지 않은 메모리를 반환하다.

실행 시기는 JVM이 OS에 메모리를 추가적으로

- Runtime Data Area

Excution Engine에게 해석된 프로그램은 Runtime Data Area에 배치되어 돌아간다. 이 때 Runtime Data Area는 3가지 구조를 갖는다.

1. Method Area : 클래스영역으로 인터페이스, 클래스, 메소드, 필드 등의 모든 정보가 들어가 있다. 여기는 모든 쓰레드들이 공유하며 new를 통해 동적으로 생성 시 저장되므로 Garbage Collector 의 대상이다.
2. Heap : 생성된 인스턴스가 있는 공간으로 Garbage Collector의 대상이며 Heap 정렬을 통해 사용빈도가 높은 인스턴스를 Root Node로 올려서 히트율을 올리는 방식이다. 모든 쓰레드들이 공유한다.
3. JVM Stacks : 호출스택이라 불리며 메소드가 실행 시 필요한 공간을 제공, 매개변수나 지역변수 등의 임시데이터를 저장한다. 메소드가 끝나면 메모리공간은 반환된다. 쓰레드마다 1개 씩 갖는다.
4. PC Registers : 일종의 스택으로서 Thread 생성될 때의 공간으로 Thread가 어떠한 명령을 실행하게 될지에 대한 부분을 기록한다. Java는 Stacks-Base 방식으로 작동하는데 JVM은 CPU에 직접 Instruction을 수행하지 않고 Stack에서 Operand를 뽑아내 이를 별도의 메모리 공간에 저장하는 방식을 취하는데 이 공간을 PC라고 한다.

### JDK와 JRE의 차이
---

- JDK

  자바 개발을 위해 필요한 도구, JRE에서 제공하는 실행 환경뿐만 아니라 자바 개발에 필요한 여러가지 명령어 그리고 컴파일러를 포함했다.  

- JRE

  Java Runtime Environment 의 약자로 자바 실행환경이다. JRE는 자바 프로그램을 동작시킬 때 필요한 라이브러리 파일, java 명령, 및 기타 인프라를 포함하여 컴파일된 Java 프로그램을 실행하는데 필요한 모든 패키지
