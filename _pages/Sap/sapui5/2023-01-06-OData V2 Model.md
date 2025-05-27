---
title: "OData V2 Model"

categories:
  - sap
tags:
  - SAP
  - SAP-ui5
  - V2-Model

date: 2023-01-06
thumbnail: "/assets/img/thumbnail/sap_thumbnail.png"
---

# oData V2 model

oData V2 모델을 사용하면 oData Service로 부터 데이터 제어를 가져올 수 있다.

oData V2 모델은 서버측의 모델이며 데이터 셋은 단지 서버에서 사용가능하고 클라이언트들은 단순히 요청된 데이터만 알 수 있다. 각 정렬과 필터링 작동은 서버 위에 올라간다. 클라이언트는 서버에 요청을 보내고 응답한 데이터를 보인다.

백앤드 요청은 바인딩 목록, 컨텍스트 바인딩들, 그리고 CRUD 함수들이 ODataModel에 의해 제공된다. 속성 바인딩은 요청이 되지 않는다.

OData model은 현재 2.0 버전까지 지원한다.

2가지 버전의 OData 모델은 `sap.ui.model.odata.ODataModel` 과 `sap.ui.model.odata.v2.ODataModel`을 참조한다. `v2.ODataModel`은 기능이 더해졌고, 참조된 이 모델 안에서 새로운 기능을 참조만 할 것이다. `sap.ui.model.odata.ODataModel`은 지원되지 않으며 **SAP는 `v2.ODataModel` 만 사용할 것을 추천한다.**

| 기능  | v2.ODataModel | ODataModel |
| :------------: | :-----------: | :-------------------: |
| OData version 지원    | 2.0          | 2.0 |
| JSON format    | Yes      | Yes               |
| XML format     | Yes  | Yes |
| 양방향 바인딩 지원 | 속성 변경만 가능  | 하나의 엔티티 속성만 동시변경 가능 |
| 기본 바인딩 | 단방향 | 단방향 |
| 클라이언트 사이드 정렬, 필터링 | [Yes](https://sapui5.hana.ondemand.com/#/api/sap.ui.model.odata.OperationMode) | NO |
| batch | 모든 요청들은 배치될 수 있다. | 단지 메뉴얼 배치 요청만 가능|
| 데이터 캐시 | 모델 안의 모든 데이터가 캐시된다.| 메뉴얼적 요청된 데이터는 캐시되지 않는다.|
| 자동 새로고침 | yes | yes |
| 메세지 핸들링 | yes | no |

다른 도메인이나 사이트에서의 백앤드가 엑세스 하는 것을 막는 Same-Origin-Policy 보안개념을 유의해야한다.

패치 데이터의 서비스 요청들은  데이터 바인딩을 제어를 위해 정의를 기반으로하여 자동으로 만들어졌다. 

ODataModel 생성자   
`new sap.ui.model.odata.v2.ODataModel(vServiceUrl, mParameters?)`  
`vServiceUrl` : 추가된 URL 파라미터들은 모든 요청을 덧붙일 것이다.
만약 오브젝트를 전달하고 싶을 땐, 이것은 두번째 파라미터 오브젝트로써 해석될 것이다. 그땐 mParameter.serviceUrl은 필수 파라미터가 된다.

## 모델 인스턴스 생성
하나의 OData 모델 인스턴스는 단지 하나의 OData service를 커버할 수 있다.
다양한 서비스를 엑세스 하기 위해선 다양한 OData Model을 인스턴스 해야한다.

```
// "ODataModel" required from module "sap/ui/model/odata/v2/ODataModel"
var oModel = new ODataModel("http://services.odata.org/Northwind/Northwind.svc/");
var oModel = new ODataModel({serviceUrl: "http://services.odata.org/Northwind/Northwind.svc"});
```
ODataModel 인스턴스를 생성할 때 서비스 메타데이터를 검색하라는 요청이 전송된다.

## Service Metadata

서비스 메타데이터는 서비스 URL 별로 캐싱된다. 같은 서비스에서 사용하는 여러 OData 모델은 이 메타데이터를 공유할 수 있다.

첫번째 모델 인스턴스만 메타데이터 요청을 작동한다. JSON 서비스 메타데이터 응답은 `getServiceMetadata()` 라는 OData 모델 인스턴스의 메소드를 호출함으로 엑세스 될 수 있다.
```
var oMetadata = oModel.getServiceMetadata();
```
v2.ODataModel 안에서 서비스 메타데이터는 비동기식으로 불러지며 동기식으로 불러올 수 없다. 로딩이 끝났을 때, `metadataLoaded` 이벤트가 붙는다.


## 추가 URL 파라미터

OData Service는, URL 파라미터를 설정해서 사용할 수 있다. UI5는 각각의 바인딩에 따라서 파라미터들을 자동적으로 설정한다.

인증토큰이나 일반 설정 옵션들 같은 경우엔 요청 URL에 요소들을 추가할 수 있다.

몇몇 파라미터들은 모든 요청에 포함되선 안되며, $expand 또는 $select와 같은 특정 목록이나 컨텍스트 바인딩에 추가되어야한다. 바인딩 메서드는 특별한 바인딩을 위한 모든 요청을 포함할 수 있는 파라미터 맵을 전달하는 옵션을 제공한다. OData 모델은 현재 $expand와 $select를 지원한다.

URL 파라미터들을 요청하는데 2가지 방법이 있다.

### 파라미터들을 service URL에 추가

```
new ODataModel("http://myserver/MyService.svc/?myParam=value&myParam2=value");
```

이 파라미터들은 OData 서버에 보내지는 모든 요청이 포함될 것이다.

### mparameter map과 함께 URL 파라미터 전달

$metadata 요청(metadataUrlParams)이 사용되며 게다가 데이터 요청에 포함된 URL 파라미터(serviceUrlParams)를 전달할 수 있다. 파라미터들은 Map 형식으로 보내진다.

```
// "ODataModel" required from module "sap/ui/model/odata/v2/ODataModel"
var oModel = new ODataModel({ 
    serviceUrl: "http://services.odata.org/Northwind/Northwind.svc",    
    serviceUrlParams: {
        myParam: "value1",
        myParam2: "value2"
    },
    metadataUrlParams: {
        myParam: "value1",
        myParam2: "value2"
    }
});
```

## HTTP HEADER

각 요청에 보내어지는 커스텀 헤더를 추가할 수 있다.

### 맵 파라미터와 함꼐 커스텀 헤더로 전달

```
var oModel = new sap.ui.model.odata.v2.ODataModel({
    headers: {
        "myHeader1" : "value1",
        "myHeader2" : "value2"
    }
});
```

### 모델 인스턴스를 글로벌 커스템헤더로 셋팅

```
oModel.setHeaders({"myHeader1" : "value1", "myHeader2" : "value2"});
```

커스텀 헤더 추가 시 이전 모든 커스텀 헤더들은 지워진다. 일부 헤더들은 private이며 즉, OData모델 내부적으로 설정되어 설정할 수 없다.

## 엔티티 주소 : 바인딩 경로 구문

OData 모델의 바인딩 경로 구문은 특정 엔티티들이나 엔티티 집합을 엑세스한 OData 안의 사용되는 서비스 URL과 상대적 URL 경로와 일치한다.

서비스의 메타데이터 안에 정의된 OData 서비스의 구조에 따른 OData에 의해 제공되어진다.

필터들과 같은 URL 파라미터들은 바인딩 경로를 추가할 수 없다. 바인딩 경로는 절대적이거나 상대적이다. 절대적 바인딩 경로는 즉시 리졸브 되지만, 상대경로는 절대경로에서 절대적 바인딩 경로를 자동적으로 전환될 수 있을 때 리졸브 될 수 있다. 만약 예를 들어 속성이 상대 경로에 바인딩 되고 그 부모 제어가 절대적 경로에 바운드 된다면, 상대적 경로는 절대적 경로를 통해 해결될 수 있다.

OData Model 내 바인딩 샘플은 Northwind 데모 서비스에서 부터 가져온다.

- 절대적 바인딩 경로

```
"/Customers"
"/Customers('ALFKI')/Address"
```
- 컨텍스트에서 확인할 수 있는 상대적 바인딩 경로

```
"CompanyName"
"Address"
"Orders"
```

- 전체 경로

```
"/Customer('ALFKI')/CompanyName"
"/Customer('ALFKI')/Address"
"/Customer('ALFKI')/Orders"
```

- 단일 엔티티 또는 엔티티들의 컬렉션이 사용되는 탐색 속성

```
"/Customers('ALFKI')/Orders"
"/Products(1)/Supplier"
```

## OData Model로부터 데이터 엑세스

OData 서비스에서 요청한 데이터는 OData 모델에 캐시된다. `getProperty()` 메서드에 의해 엑세스 될 수 있으며, 엔티티 객체 또는 값을 리턴한다. 이 메서드는 백앤드로부터 요청한 데이터가 아니며, 단지 미리 요청되거나 캐시된 엔티티들로 엑세스 될 수 있다.
```
oModel.getProperty("/Customer('ALFKI')/Address")
```

이 메소드들로 싱글엔티티들과 속성들을 엑세스 할 수 있다. 엔티티 집합들을 엑세스하면, 바인딩 목록으로 읽기 전용 엔티티들을 바인딩 컨텍스트로 가져올 수 있다. 이 메서드가 리턴한 값들은 JSON 모델 안에서 참조된 것이 아닌 카피된 데이터이다.

## 엔티티 생성
`createEntity()` 메서드를 호출하면 명시된 엔티티 집합에 대한 엔티티들을 호출한다. 이 메서드는 새로 만들어진 엔티티를 가리키는 컨텍스트 객체를 반환한다.

이 어플리케이션은 이러한 객체들을 바인딩 할 수 있고 양뱡향으로 데이터들을 변경할 수 있다. `submitChanges()` 라고 불리는 메서드를 호출하면, OData 백앤드 안에 엔티티들을 저장한다. 변경을 초기화하려면 `deleteCreateEntry()` 함수를 부르면 된다. 
```
var oContext = oModel.createEntry(
        "/Products",
        { properties:
            { ID:99,
              Name:"Product",
              Description:"new Product",
              ReleaseDate:new  Date(), 
              Price:"10.1", 
              Rating:1
            }
        }
);  // 명시된 속성들과 값을 가진 제품들의 엔티티 생성

oForm.setBindingContext(oContext); // 엔티티 바인딩

oModel.submitChanges({success: mySuccessHandler, error: myErrorHandler}); // Odata 백앤드 안에 엔티티 저장

entity oModel.deleteCreatedEntry(oContext); // 변경 취소 시 호출
```
만약 엔티티들을 submit 하면 컨텍스트는 모델에 import 된 새로운 데이터를 모델로 가져온다. 새로운 엔티티를 가리킨다.

## CRUD 작동  

OData 모델은 OData Service에서 메뉴얼적인 작업을 허용한다. 메뉴얼적 작업이 데이터를 반환할 때는 Odata 모델 데이터의 캐시가 import 된다. 모든 작업들은 필수적 sPath 파라미터와 mParameters Map을 선택적으로 요구한다.

 또한, 생성, 수정 메소드들은 데이터 객체가 생성되거나 변경될 때 OData 파라미터를 필수적으로 요구한다. 각각의 작업은 요청 중단을 사용할 수 있는 중단함수를 포함한 객체를 반환한다. 만약 요청이 중단되어 에러 핸들러가 호출된다면, 이것은 성공 또는 에러 핸들러가 모든 요청에 대해 호출되도록 보장한다. 이것은 또한 헤더 데이터, URL 파라미터, 또는 eTag에 대해 추가적으로 보낼 수 있도록 한다.

- 엔티티들 생성
create 함수는 OData 모델의 생성이 명시된 OData service의 POST 요청을 작동시킨다. 어플리케이션은 새로운 엔티티와 생성된 엔티티 데이터를 엔티티 셋으로 가진다. 

```
var oData = { ProductId: 999, ProductName: "myProduct" } // 엔티티 데이터
oModel.create("/Products", oData, {success: mySuccessHandler, error: myErrorHandler}); // 엔티티들을 create()를 통해 명시된 모델로 생성한다.
```

- 엔티티 읽기
read 함수는 GET 요청으로 작동된다. 이 경로는 OData model에 의해 생성에서 명시된 OData service로 부터 가져온다. 이 가져온 데이터는 성공여부에 따라 success handler와 error handler로 나뉜다.

```
oModel.read("/Products(999)", {success: mySuccessHandler, error: myErrorHandler});
```

- 엔티티 수정 
update 함수는 PUT/MERGE 요청으로 작동하며 성공적으로 요청이 된 후에는 model 안에서 refresh 된 데이터를 자동으로 가져온다.

```
oModel.update("/Products(999)", oData, {success: mySuccessHandler, error: myErrorHandler});
```

- 엔티티 삭제
delete 함수는 DELETE 요청으로 작동하며, 어플리케이션에서는 삭제해야할 엔트리의 경로를 명시해야한다.

```
oModel.remove("/Products(999)", {success: mySuccessHandler, error: myErrorHandler});
```

- 변경 후 refresh  

모델은 변화된 엔티티들을 의존하여 자동적으로 refresh를 바인딩하는 메커니즘을 제공한다. 만약 create, update, remove 함수를 수행하면, 그 고유의 모델은 바인딩을 확인하며 이를 위해 refresh를 작동한다. 만약 그 모델이 배치모드에서 실행되면, 새로고친 요청은 같은 배치 요청 안의 변화들과 함께 묶이게 된다. `setRefreshAfterChange(false)` 호출에 의해 자동으로 비활성화 할 수 있다. 만약 자동 고침이 비활성화 되었을 때, 어플리케이션은 각각의 바인딩들을 새로고쳐야 한다. 

- 자식 엔티티 생성  

부모 엔티티에 새로운 자식 엔티티 생성은 한번의 싱글 API 요청으로 가능하지 않다. 이를 만들려면 부모, 자식의 생성 엔티티 API 호출을 연결하면 만들 수 있고 아래의 샘플은 판매 주문과 주문 항목을 모두 생성한다.

```
var oParentContext, oModel = this.getView().getModel(); 

oParentContext = oModel.createEntry("SalesOrderSet", { //부모 엔티티 생성
	properties : {
		 // 새로운 판매 주문을 위한 속성
	},
	success : function () { // 부모(oParentContext)가 생성되었을 때
		oChildContext = oModel.createEntry("ToLineItems", { //자식 엔티티 생성
			context : oParentContext, // context에 부모의 컨텍스트 저장
			properties : { 
				// 새로운 판매 주문에 의한 새로운 아이템들의 속성
			},
			success : function () {
				// ...
			}
		});
		oModel.submitChanges(); // OData 백앤드에 저장
	}
});

oModel.submitChanges(); // OData 백앤드에 저장

```

## 동시성 제어 와 ETags

OData는 optimistic한 동시성 제어를 HTTP ETags를 사용한다. ETag는 모든 CRUD 요청을 위해서 parameter map으로 전달될 수 있다. 만약 ETag가 전달되지 않으면, 미리 로드된 경우, 캐시된 엔티티가 사용된다.

## XSRF Token

CSRF 를 해결하기 위해 OData 서비스는 데이터 변경 시 XSRF 토큰을 필요로 한다. 이 경우 서버에서 가져온 토큰을 같이 서버에 보내야 하며 OData 모델은 메타데이터를 읽을때, XSRF 토큰을 가져와 header에 넣어 자동으로 토큰을 전송한다. 토큰이 유효하지 않을때엔, OData Model에서 refreshToken 함수를 호출하여 패치될 수 있다. 이 토큰은 루트 URL 서비스의 호출과 함께 가져오며 서비스 다큐먼트와 함께 응답한다. 유효한 토큰을 가져오려면 응답이 캐싱되지 않았는지 확인해야한다.

## 모델의 새로고침

refresh 함수는 OData 모델의 모든 데이터를 새로고침한다. 각각의 바인딩은 서버로부터 데이터를 다시 읽는다. 리스트 또는 컨텍스트 바인딩 경우, 백앤드에서 새로운 요청이 작동된다. 만약 XSRF 토큰이 유효하지 않으면, 서비스 다큐먼트에서 읽기 요청을 다시 가져와야 한다. 메뉴얼 CRUD 요청들로 임포트된 데이터는 자동으로 리로드 되지 않는다.

## 배치 프로세싱

ODataModel v2는 2가지 다른 방법으로 batch processing을 지원한다.

1. 기본 : 쓰레드안에 모든 요청들은 배치 요청들로 수집되고 다뤄진다. 즉, 요청은 현재 스택이 종료된 후에 타임아웃 요청을 보낸다. 이것은 바인딩에 의해 작동된 요청들로부터 모든 메뉴얼적 CRUD 요청들을 포함한다.

2. 지연 : 요청들은 저장되며 어플리케이션의 의해 호출되는 `submitChanges()` 과 함께 submit 되어질 수 있다. 이것은 또한 바인딩으로 부터 요청들이 작동될 뿐만 아니라, 모든 메뉴얼적 CRUD 요청들이 포함된다.

모델이 요청을 다루는 방법은 결정할 수 없다. 그래서 SAPUI5는 groupId를 제공한다. 각각의 컨텍스트와 바인딩 리스트 그리고 각각 메뉴얼 요청들에 그룹 아이디를 지정할 수 있다. 같은 그룹안에 속하는 모든 요청들은 하나의 요청 안에서 다뤄질 수 있다. 그룹아이디가 없는 요청은 기본 배치 그룹 안에서 다뤄진다. 변경을 위해 chageSetId 를 사용할 수 있다. 같은 changeSetId에 포함된 각 변경들은 배치 요청안에서 하나의 changeSet으로 다뤄진다. 기본적으로, 모든 변화들은 고유의 changeSet을 가진다.

`setDefiredGroup()` 메서드를 사용하여 이전에 정의된 그룹의 서브셋을 지연으로 설정할 수 있다. (`setChangeGroups()` , `getChangeGroups()` 에도 동일 시 적용)

그룹에 속한 모든 요청들은 요청 queue안에 저장된다. 
지연된 배치 그룹은 `submitChanges()` 메소드를 통해 메뉴얼적으로 전송되어야한다. 만약 `submitChanges()`를 호출할 때 배치 그룹아이디를 명시하지 않으면, 모든 지연된 배치 그룹들이 전송된다.

```
- 그룹들의 서브셋을 지연으로 설정
	var oModel = new ODataModel(myServiceUrl);

- 바인딩한 groupId를 전송한다.
	{path:"/myEntities", parameters: {groupId: "myId"}}

- 지연한 groupId 설정
	1. 그룹 가져오기
		var aDeferredGroups = oModel.getDeferredGroups();
	2. 리스트에 그룹 아이디 추가
		aDeferredGroups = aaDeferredGroups.concat(["myId"]);
	3. 지연된 모든 그룹들을 설정
		oModel.setDeferredGroups(aDeferredGroups);
	4. 지연된 모든 그룹 전송
		oModel.submitChanges({success: mySuccessHandler, error: myErrorHandler});
```

# 양방향 바인딩

v2.oDataModel은 양방향 바인딩을 지원한다. 기본적으로 모든 변경들은 지연으로 설정된 `changes` 라는 배치그룹에 수집된다.

`changes` 로 전송하려면, `submitChanges()` 함수를 사용한다. changes 데이터는 복사 데이터로 만들어진다. 이것은 이전 데이터를 가져와 백앤드에 새 요청을 보내지 않고도 `changes`를 재설정 할 수 있다. `resetChanges()` 써서 모든 `changes` 저장공간을 리셋할 수 있다. 또한 엔티티 경로 배열이 있는 `resetChanges()` 함수를 호출하여 특정 엔티티만 리셋할 수 있다.

model에서 `setChangeGroups()` 를 사용하면, 다른 배치 그룹안에 있는 다른 엔티티들 또는 타입들을 위한 `changes`도 수집할 수 있다. 
```
var oModel = new ODataModel(myServiceUrl); 
	oModel.setDeferredGroups(["myGroupId", "myGroupId2"]); 
	oModel.setChangeGroups({ 
		"EntityTypeName": {
			 groupId: "myGroupId", // 
			 changeSetId: "ID", // 선택사항 (Id 변경)
			 single: true, /*optional, can be true or false*/ 
		}
	});
oModel.submitChanges({groupId: "myGroupId", success: mySuccessHandler, error: myErrorHandler});

```
같은 배치 그룹 안에서 모든 엔티티 타입을 위한 `changes` 수집은 '*'를 EntityType으로 사용한다. 만약 `change`가 지연으로 설정하지 않으면, `changes`는 즉시 백앤드에 보내어진다. 단일 파라미터를 true 또는 false로 설정에 의해 , 고유의 `change` 설정 안에 각각의 `change` 결과들이거나 `changes`가 하나의 `change` 설정을 수집할 것인지를 정의한다. 모델은 단지 single의 설정이 false 일 때만 changeSetId를 처리한다.
```
var oModel = new ODataModel(myServiceUrl);

oModel.setProperty("/myEntity(0)", oValue);

oModel.resetChanges(["/myEntity(0)"]);
```

## 바인딩별 매개변수

OData 프로토콜은 명시적으로 다른 URL 파라미터이다.

위에서 설명한 파라미터들 뿐만 아니라 바인딩 안에 파라미터들을 사용할 수 있다.

- Expand parameter

확장 파라미터는 어플리케이션에서 그들의 네비게이션 속성들과 함께 연결된 엔티티들을 읽는 걸 허락한다.  

```
oControl.bindElement("/Category(1)", {expand: "Products"}); 

oTable.bindRows({
    path: "/Products",
    parameters: {expand: "Category"}
});

```
예로 Category(1) 의 모든 제품들은 서버 응답안에 inline으로 내장되어 하나의 요청만 부른다. 모든 Products 위한 카테고리는 각각의 product 위한 응답에 inline으로 내장되어있다.

- Select parameter

선택 파라미터는 어플리케이션이 엔티티를 요청할 때 읽는 속성들의 서브셋으로 정의하는 것을 허락한다.
```
oControl.bindElement("/Category(1)", {expand: "Products", select: "Name,ID,Products"}); 
oTable.bindRows({ path: "/Products", parameters: {select: "Name,Category"} });
```
예를 들어 `Name`, `ID` 그리고 `ofCategory(1)` 속성 뿐만 아니라 제품에 내장된 모든 속성들도 응답한다. 이 속성과 카테고리는 각각의 제품에 포함되며 카테고리 속성은 관련된 카테고리 항목에 대한 링크를 포함한다.

 - Custom query options

서비스 작동을 위한 input 파라미터로서 커스텀 쿼리 옵션들을 사용할 수 있다. list 바인딩이 생성될 때, 커스텀 파라미터를 명시한다.
```
oTable.bindRows({
		path: "/Products",
		parameters: { 
		custom: { // 커스텀 파라미터 명시
			param1: "value1",
			param2: "value2"
		}
	},
	template: rowTemplate
});
```

만약 `bindElement()`를 사용하면, 아래와 같이 파라미터를 명시할 수 있다.
```
oTextField.bindElement("/GetProducts", {
	custom: {
		"price" : "500"
	}
});
```

## 바인딩 의존 최적화

OData V2 모델 에서 생성자는 `preliminaryContext` 라 불리는 flag를 지원한다. 이 옵션이 true 이면, 모델은 더 적은 $batch 요청 종속적 바인딩에 대한 OData 호출을 다를 수 있게 된다.

### 소개  


부모 바인딩이 의존 바인딩에 설정된 컨텍스트에 해당하는 OData 엔티티를 읽는다면 다른 바인딩(부모바인딩) 에 의존한다.

기본적으로 종속 바인딩을 위한 데이터는 바인딩 컨텍스트를 위한 데이터를 부모 바인딩를 통해 읽은 후에만 읽는다.

부모 바인딩이 컨텍스트 바인딩인 경우, 2개의 읽기 요청을 하나의 번들링으로 퍼포먼스를 증가시킬 수 있다. 바인딩과 연결된 단일 컨텍스트는 예비의 컨텍스트를 명시하여 수행할 수 있다. 이를 위해 부모 바인딩 구성에 `createPreliminaryContext` 파라미터 설정이 필요하다. 의존적 리스트 또는 컨텍스트 바인딩은 데이터를 읽기 전에 preliminaryContext 경로를 사용하여 데이터를 읽어 그들 자신의 요청을 위한 경로 구성을 주문 할 수 있다. 의존 바인딩의 생성을 `usePreliminaryContext` 파라미터를 설정해 수행한다.

### 설정과 사용

OData V2 model을 생성할 떄 preliminaryContext 파라미터를 설정할 수있다. 이 모델을 위해 생성된 모든 바인딩의 preliminary 컨텍스트를 전환한다.

- 모든 컨텍스트 바인딩은 `createPreliminaryContext` 파라미터를 true로 가진다.
- 모든 컨텍스트 바인딩과 모든 바인딩 목록은 `usePreliminaryContext` 파라미터를 true로 설정한다.

ODataContextBinding 생성자 또는 ODataListBinding 생성자에 해당하는 파라미터들의 기본을 무시할 수 있다.
게다가 모델에 일반적 `preliminaryContext` 파라미터를 사용하지 않을 수도 있다. (모든 바인딩에 영향을 미친다)

그러나 이러한 매개변수 사용하는 바인딩 인스턴스와 부모쌍에 대한 `preliminaryContext`를 바꾼다.

예를 들면, 부모 바인딩인 "/Product{1}" 경로를 가진 컨텍스트 바인딩을 보여준다.(`sap.m.Panel` 경로로 바인딩된 컨텍스트들을 생성) 'Supplier' 경로를 가진 의존적 관련 바인딩은 product의 모든 supplier를 보여주는 테이블로 생성된다. ( `sap.ui.table.Table` 제어 위한 행 을 생성)
![](https://sapui5.hana.ondemand.com/docs/topics/loioe2fe691bea0f4181b6d835c11c92e9ba_LowRes.png)

**싱글 바인딩 예제** 

표에 따르면, `preliminaryContext`들을 사용하지 않고, Binding 0 위한 하나의 요청, 그리고 나중에 Binding 1 위한 하나, 두개 연속으로 OData 요청들이 이슈가 된다.

| 요청 넘버 | 요소 |
|:--:|:--:|
|1| GET Product(1) |
|1| GET Product(1)/Supplier |

아래에서 보여주는 바인딩 매개변수를 설정하여 요청을 최적화 할 수 있다.
![](https://sapui5.hana.ondemand.com/docs/topics/loio57a4d12d4e5d41ecb74298a55b60d0fb_LowRes.png)

**싱글 바인딩 예제 최적화**

여기 Binding 1은 Binding 0이 생성될 때 `preliminaryContext`를 사용하며, 그리고 이와같이 요청 URL 은 다이렉트로 해결될 수 있다.
| 요청 넘버 | 요소 |
|:--:|:--:|
|1| GET Product(1),GET Product(1)/Supplier|

## 함수 임포트
ODataModel은 `callFunction()` 메소드에 의해 임포트나 또는 액션 함수들의 부르는 것을 지원한다.
```
oModel.callFunction("/GetProductsByRating",{method:"GET", urlParameters:{"rating":3}, success:fnSuccess, error: fnError})
```

만약 `callFunction()` 요청이 지연되면, `submitChangesmethod()`를 통해 전송되어 질 수 있다.

### 파라미터를 가져오는 함수의 바인딩

OData Model V2는 파라미터들을 가져오는 함수에 대해 바인딩을 지원한다. 엔티티 속성에 대해 바인딩을 지원하는 `createEntry()` 메서드와 비슷하다. `callFunction()` 메서드는 promise를 가진 핸들을 반환한다. 그 promise는 바인딩된 컨텍스트가 성공적으로 생성되거나 또는 거부될 때 해결된다.

```
var oHandle = oModel.callFunction("/GetProductsByRating", {urlParameters: {rating:3}});
oHandle.contextCreated().then(function(oContext) {
	oView.setBindingContext(oContext); 
});
```

만약 함수가 결과 데이터를 가져오면, 그때 그 결과 데이터는 엑세스 되고 컨텍스트 사용 속성 $result 에 대해 묶인다.
```
<form:SimpleForm>
	<core:Title text="Parameters" />
	<Label text="Rating" />
	<Input value="{rating}" />
	<Button text="Submit" press=".submit" />
	<core:Title text="Result" />
	<List items="{$result}">
	<StandardListItem title="{Name}" />
	</List>
</form:SimpleForm>
```

## 언어

SAPUI5는 현재 언어의 컨셉으로 사용한다. 이 언어는 자동적으로 OData V2 model에 의해 OData service로 전달된다. 이 이유로 어플리케이션은 언어 자체를 하드 코드로 해서 안된다. 예로 커스텀 쿼리 옵션에 'sap-language' URL 파라미터를 명시해서는 안된다.

## OData V2위한 메타 모델

`sap.ui.model.odata.ODataMetaModel`의 구현은 OData V2 metadata, 그리고 V4 어노테이션 둘다 통일된 엑세스로 제공한다.

메타모델은 기존 `sap.ui.model.odata.ODataMetadata` 기반으로 사용하며 엔티티나 또는 속성에 직접적으로 상승하는 기존 `sap.ui.model.odata.ODataAnnotations`로부터의 OData Version 4.0을 병합한다.

### 기본 구조

`sap.ui.model.odata.ODataMetadata` 의 기본 구조는 코드 스니핑에 따라서 보여진다. 이것은 엔티티 모델이 중첩되는 가장 중요한 요소가 어떻게 되는지 보여준다.
각각의 요소들은 약간의 네임스페이스로 부터 XML 속성 값의 확장성을 가질 수 있다. 아래 코드스니핑은 이러한 확장성들이 어떻게 저장되고 처리되는 지를 보여준다.

```
"dataServices": {
    "schema": [{
      "association": [{
        "end": []
      }],
      "complexType": [{
        "property": []
      }],
      "entityContainer": [{
        "associationSet": [{
          "end": []
        }],
        "entitySet": [],
        "functionImport": [{
          "parameter": []
        }]
      }],
      "entityType": [{
        "property": [],
        "navigationProperty": []
      }]
    }]
  }
```

### 객체, 속성 엑세스

OData 메타 모델 안에 객체들은 배열로 처리된다. 예로 '/dataService/schema'는 각각 스키마가 엔티티 타입, 등등의 배열과 함께 엔티티 타입 속성을 가지는 스키마들의 배열이다. 그래서 '/dataServices/schema/0/entityType/16'은 'MySchema' 네임스페이스가 스키마 내 이름이 'Order'인 엔티티 타입의 경로가 될 수 있다.

그러나 이 경로들은 안정적이지 않다. 만약 낮은 인덱스를 가진 엔티티 타입이 스키마로부터 제거되었을 때, 'Order' 경로는 '/dataServices/schema/0/entityType/15/' 로 변한다. index가 변하는 문제를 피하기 위해서 getObject 나 getProperty는 인덱스를 위한, XPath 같은 쿼리를 지원한다. 각각의 인덱스는 대괄호 안 쿼리에 의해 대체될 수 있다.  

예를 들어 
```
경로를 사용하는 스키마 주소
/dataServices/schema/[${namespace}==='MySchema']

경로를 사용하는 엔티티 주소
/dataServices/schema/[${namespace}==='MySchema']/entityType/[${name}==='Order']
```
를 지정하여 사용할 수 있다.

대괄호 안의 구문은 바인딩 구문의 표현식이랑 일치한다. 쿼리는 결과가 true로 될 때까지 각 객체들을 위해 실행된다. 그 다음 객체가 선택되면 
이 경로를 복잡한 바인딩 구문을 사용하여 바인딩 식에 끼워넣는다. 
```
`${path:'...'}`.
Example: `{:= ${path:'target>extensions/[${name} === \'semantics\']/value'} === 'email'}`
```

이러한 각 쿼리들은 자체적으로 포함되어있다. 쿼리는 관련 경로를 통해서 현재 후보의 속성에 언급할 수 있다. 그러나 XML 탬플릿 안에서 이용가능한 ${meta>} 와 같은 변수들은 언급할 수 없다.

### 확장자

확장 배열과 SAP 사용해 단순 속성의 객체로 변환: 이전에 속성 이름들을 추가 ex) 8번쨰 라인 참조
```
1  {
2    "name": "BusinessPartnerID",
3    "extensions": [{
4      "name": "label",
5      "value": "Bus. Part. ID",
6      "namespace": "http://www.sap.com/Protocols/SAPData"
7    }],
8    "sap:label": "Bus. Part. ID"
9  }
```

### OData V4 어노테이션

엔티티 모델의 각각 요소는 어노테이션을 달 수 있다. 기존 `sap.ui.model.odata.ODataAnnotations` 로 부터의 어노테이션은 해당 요소에 직접적으로 병합된다.  
아래 코드는 위에서 설명한 것처럼 기존 `sap.ui.model.odata.ODataMetadata`로부터의 구조를 보여준다.
```
"dataServices" : {
    "schema" : [{
        "namespace" : "GWSAMPLE_BASIC",
        "entityType" : [{
            "name" : "Product",
            "property" : [{
                "name" : "ProductID",
                "type" : "Edm.String",
                "nullable" : "false",
                "maxLength" : "10"
            }, {
                "name" : "SupplierName",
                "type" : "Edm.String",
                "maxLength" : "80",
                "extensions" : [{
                  "name" : "label",
                  "value" : "Company Name",
                  "namespace" : "http://www.sap.com/Protocols/SAPData"
                }, {
                  "name" : "creatable",
                  "value" : "false",
                  "namespace" : "http://www.sap.com/Protocols/SAPData"
                }, {
                  "name" : "updatable",
                  "value" : "false",
                  "namespace" : "http://www.sap.com/Protocols/SAPData"
                }],
                "sap:label" : "Company Name",
                "sap:creatable" : "false",
                "sap:updatable" : "false"
                "Org.OData.Core.V1.Computed" : {
                    "Bool" : "true"
                }
            }, {
                "name" : "WeightMeasure",
                "type" : "Edm.Decimal",
                "precision" : "13",
                "scale" : "3",
                "Org.OData.Measures.V1.Unit" : {
                    "Path" : "WeightUnit"
                }
            }, {
                "name" : "WeightUnit",
                "type" : "Edm.String",
                "maxLength" : "3"
            }],
            "com.sap.vocabularies.UI.v1.DataPoint" : {
                "Value" : {
                    "Path" : "WeightMeasure",
                    "EdmType" : "Edm.Decimal"
                }
            },
            "com.sap.vocabularies.UI.v1.Identification" : [{
                "Value" : {"Path" : "ProductID"}
            }, {
                "Value" : {"Path" : "SupplierName"}
            }, {
                "Value" : {"Path" : "WeightMeasure"}
            }]
        }]
    }]
}
```
### OData Meta Model의 향상

각 sap:label 과 같이 기본 용어에 해당하는 SAP-specific OData 어노테이션에 쉽게 접근하는데다가, 어노테이션은 기존 `sap.ui.model.odata.ODataAnnotations`의 OData 버전 4.0 어노테이션 안에서 정의 되지 않았을 때에서만 믹스된다.

### OData V2 내 통화 및 단위 정의

양이나 치수 는 CLDR에 정의된 것 보다 다른 통화, 또는 단위가 필요할 수 있다.

`The sap.ui.model.odata.type.Currency` 그리고 `sap.ui.model.odata.type.Unit` 데이터 타입들은 통화 코드 그리고 단위를 커스터마이징 할 때 코드목록을 사용할 수 있다.

통화 또는 유닛 커스터마이징 하는 코드 목록의 경우 어노테이션들 정의해야한다.

OData V4 시나리오와 대조적으로 OData V2는 코드 리스트 서비스를 허용하지 않는다. 모든 메터데이터 정보는 기본 metadata.xml 파일에 포함되어야 하며, 코드리스트 URL은 단지 이 파일만을 가리켜야 한다. 이것은 다음과 같이 URL 속성을 명시하여 수행된다.

`<PropertyValue Property="Url" String="./$metadata"/>`

`com.sap.vocabularies.CodeList.v1.CurrencyCodes` 또는 `com.sap.vocabularies.CodeList.v1.UnitsOfMeasure` 어노테이션이 참조된 코드리스트는 이것들이 필요하다.

 - 유일한 키 속성인 내부 코드
 - 의존적 언어 설명
 - 특정 단위 숫자 속성
 - 옵션 : 내부 코드 대신 보여지는 외부 코드
 - 옵션 : 표준 코드
키 속성 문서화:
- 설명 속성을 가리키는 `com.sap.vocabularies.Common.v1.Text`
- 숫자 속성을 가리키는 `com.sap.vocabularies.Common.v1.UnitSpecificScale`  
- 표준 코드를 가리키는 `com.sap.vocabularies.CodeList.v1.StandardCode`

어노테이션 안의 경로 속성은 엔티티 타입 안 속성들을 참조해야하는 것을 명심해야한다. 네비게이션 속성을 포함하는 경로는 지원되지 않는다.

대체키가 가능할 때 타입은 통화 또는 단위의 키로서 대신 사용한다. 이 경우엔, 그 서비스는 통화 또는 단위 속성안에서 대체 키 묘사를 포함해야 한다. 대체키가 주석이 달리지 않았을 땐, 키는 데이터 안에서 사용, 예상된다. 최대 하나의 키를 가져야 하며, 키와 대체키는 정확히 하나여야 한다.

`com.sap.vocabularies.CodeList.v1.StandardCode` 로서 문서화된 속성은 `sap.ui.model.odata.type.Currency` 에서  ISO 코드로  해석된다. 그리고 통화 상징을 찾는데 사용된다. 이 통화 상징은 데이터 입력에 사용된다.

service's metadata.xml 파일 내 통화 코드와 단위 코드 리스트 문서
```
...
<edmx:Include Namespace="com.sap.vocabularies.Common.v1" Alias="SAP__common"/>
<edmx:Include Namespace="Org.OData.Core.V1" Alias="SAP__core"/>
<edmx:Include Namespace="com.sap.vocabularies.CodeList.v1" Alias="SAP__CodeList"/>
...
<EntityType Name="Product">
    ...
    <Property Name="WeightMeasure" Type="Edm.Decimal" Precision="13" Scale="3" />
    <Property Name="WeightUnit" Type="Edm.String" MaxLength="3" />
    <Property Name="CurrencyCode" Type="Edm.String" Nullable="false" MaxLength="5" />
    <Property Name="Price" Type="Edm.Decimal" Precision="16" Scale="3" /> 
    ...
</EntityType>
...
<EntityType Name="SAP__Currency" sap:content-version="1">
<Key>
    <PropertyRef Name="CurrencyCode"/>
</Key>
    <Property Name="CurrencyCode" Type="Edm.String" Nullable="false" MaxLength="5" sap:label="Currency" sap:semantics="currency-code"/>
    <Property Name="ISOCode" Type="Edm.String" Nullable="false" MaxLength="3" sap:label="ISO Code"/>
    <Property Name="Text" Type="Edm.String" Nullable="false" MaxLength="15" sap:label="Short Text"/>
    <Property Name="DecimalPlaces" Type="Edm.Byte" Nullable="false" sap:label="Decimals"/>
</EntityType>
 
<EntityType Name="SAP__UnitOfMeasure" sap:content-version="1">
<Key>
    <PropertyRef Name="UnitCode"/>
</Key>
    <Property Name="UnitCode" Type="Edm.String" Nullable="false" MaxLength="3" sap:label="Internal UoM" sap:semantics="unit-of-measure"/>
    <Property Name="ISOCode" Type="Edm.String" Nullable="false" MaxLength="3" sap:label="ISO Code"/>
    <Property Name="ExternalCode" Type="Edm.String" Nullable="false" MaxLength="3" sap:label="Commercial"/>
    <Property Name="Text" Type="Edm.String" Nullable="false" MaxLength="30" sap:label="UoM Text"/>
    <Property Name="DecimalPlaces" Type="Edm.Int16" sap:label="Decimal Places"/>
</EntityType>
...
<EntityContainer Name="GWSAMPLE_BASIC_Entities" m:IsDefaultEntityContainer="true" sap:message-scope-supported="true" sap:supported-formats="atom json xlsx">
<EntitySet Name="ProductSet" EntityType="GWSAMPLE_BASIC.Product" sap:content-version="1"/>
...
<EntitySet Name="SAP__Currencies" EntityType="GWSAMPLE_BASIC.SAP__Currency" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:pageable="false" sap:content-version="1"/>
<EntitySet Name="SAP__UnitsOfMeasure" EntityType="GWSAMPLE_BASIC.SAP__UnitOfMeasure" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:pageable="false" sap:content-version="1"/>
...
<Annotations
    xmlns="http://docs.oasis-open.org/odata/ns/edm"
    Target="GWSAMPLE_BASIC.GWSAMPLE_BASIC_Entities"> 
    <Annotation Term="SAP__CodeList.CurrencyCodes">
        <Record>
            <PropertyValue Property="Url" String="./$metadata"/>
            <PropertyValue Property="CollectionPath" String="SAP__Currencies"/>
        </Record>
    </Annotation>
    <Annotation Term="SAP__CodeList.UnitsOfMeasure">
        <Record>
            <PropertyValue Property="Url" String="./$metadata"/>
            <PropertyValue Property="CollectionPath" String="SAP__UnitsOfMeasure"/>
        </Record>
    </Annotation>
</Annotations>

<Annotations Target="SAP__self.Currency/CurrencyCode">
    <Annotation Term="Common.Text" Path="Text" />
    <Annotation Term="Common.UnitSpecificScale" Path="DecimalPlaces" />
    <Annotation Term="CodeList.StandardCode" Path="ISOCode" />
</Annotations>
  
<Annotations
    xmlns="http://docs.oasis-open.org/odata/ns/edm"
    Target="GWSAMPLE_BASIC.SAP__UnitOfMeasure/UnitCode">
    <Annotation Term="Common.Text" Path="Text" />
    <Annotation Term="Common.UnitSpecificScale" Path="DecimalPlaces" />
    <Annotation Term="CodeList.StandardCode" PropertyPath="ISOCode" />
    <Annotation Term="CodeList.ExternalCode" PropertyPath="ExternalCode" />
</Annotations>
  
<Annotations 
    xmlns="http://docs.oasis-open.org/odata/ns/edm"
    Target="GWSAMPLE_BASIC.SAP__UnitOfMeasure">
    <Annotation Term="Core.AlternateKeys">
      <Collection>
        <Record>
          <PropertyValue Property="Key">
            <Collection>
              <Record>
                <PropertyValue Property="Name" PropertyPath="ExternalCode" />
                <PropertyValue Property="Alias" String="ExternalCode" />
              <Record>
            </Collection>
          </PropertyValue>
        <Record>
      </Collection>
    </Annotation>
</Annotations>
...
```
위 메타데이터를 통해 `sap.ui.model.odata.type.Currency` 와 `sap.ui.model.odata.type.Unit` 같은 입력 필드의 데이터 타입을 사용할 수 있다. 데이터 타입들은 금액 또는 측정을 첫번째로, 통화코드 또는 단위를 두번째로, 그리고 커스텀한 코드리스트 정보를 세번째로 하여 정보를 합쳐 사용한다.

```
...
<Input value="{
   mode:'TwoWay', 
   parts:[
      'WeightMeasure', 
      'WeightUnit', 
      {
         mode:'OneTime', 
         path:'/##@@requestUnitsOfMeasure', 
         targetType:'any'}], 
   type:'sap.ui.model.odata.type.Unit'}"/>
...
<Input value="{
   mode:'TwoWay', 
   parts:[
      'Price', 
      'CurrencyCode', 
      {
         mode:'OneTime', 
         path:'/##@@requestCurrencyCodes', 
         targetType:'any'}], 
   type:'sap.ui.model.odata.type.Currency'}"/>
...
```

코드리스트는 브라우저 세션 및 코드목록 URL당 한번만 자동으로 요청된다.



