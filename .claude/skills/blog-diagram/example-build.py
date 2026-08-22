#!/usr/bin/env python3
"""로드맵 글의 1~7단계 도식을 생성한다.

roadmap.sh/backend 의 세부 노드 132개를 하나도 합치지 않고 각각 상자로 그린다.
토픽 23개는 존(묶음) 라벨이 된다.

표시 규칙: '추천'이 132개 중 72개로 다수라 달지 않는다.
예외인 '대안'·'순서 무관'만 단다.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from gen import build

# 이 스크립트 기준으로 레포 루트를 거슬러 올라간다 (worktree 에서도 동작)
OUT = Path(__file__).resolve().parents[3] / "_includes" / "diagrams"

D = [
    dict(
        slug='backend-roadmap--s1',
        title='1단계 기초',
        desc='인터넷 동작 원리와 HTTP, DNS 를 익힌 뒤 HTML·CSS·JavaScript 기초로 이어지는 구간.',
        zones=[
            {"name": '인터넷 기초', "nodes": [
                {"t": '인터넷 동작 원리'}, {"t": 'HTTP'}, {"t": '도메인'},
                {"t": '호스팅'}, {"t": 'DNS'}, {"t": '브라우저 동작 원리'},
            ]},
            {"name": '프론트엔드 기초', "nodes": [
                {"t": 'HTML'}, {"t": 'CSS'}, {"t": 'JavaScript', "s": '순서 무관'},
            ]},
        ]),
    dict(
        slug='backend-roadmap--s2',
        title='2단계 언어와 버전 관리',
        desc='백엔드 언어를 하나 고르고 Git 과 저장소 호스팅으로 넘어가는 구간. 언어는 택 1 이다.',
        zones=[
            {"name": '백엔드 언어 · 택 1', "nodes": [
                {"t": 'JavaScript'}, {"t": 'Go'}, {"t": 'Python'},
                {"t": 'Ruby', "s": '대안'}, {"t": 'Java', "s": '대안'}, {"t": 'C#', "s": '대안'},
                {"t": 'PHP', "s": '대안'}, {"t": 'Rust', "s": '대안'},
            ]},
            {"name": '버전 관리', "nodes": [
                {"t": 'Git'}, {"t": 'GitHub'}, {"t": 'GitLab', "s": '대안'},
            ]},
        ]),
    dict(
        slug='backend-roadmap--s3',
        title='3단계 데이터베이스와 API',
        desc='관계형 DB 에서 API 스타일, 인증, 웹 보안으로 이어지는 구간. PostgreSQL 만 추천이고 나머지는 대안이다.',
        zones=[
            {"name": '관계형 DB', "nodes": [
                {"t": '마이그레이션'}, {"t": 'MySQL', "s": '대안'}, {"t": 'PostgreSQL'},
                {"t": 'MariaDB', "s": '대안'}, {"t": 'SQLite', "s": '대안'}, {"t": 'MS SQL', "s": '대안'},
                {"t": 'Oracle', "s": '대안'}, {"t": 'N+1 문제'},
            ]},
            {"name": 'API 스타일', "nodes": [
                {"t": 'REST'}, {"t": 'JSON API'}, {"t": 'SOAP', "s": '순서 무관'},
                {"t": 'gRPC', "s": '순서 무관'}, {"t": 'GraphQL', "s": '순서 무관'}, {"t": 'OpenAPI 명세', "s": '순서 무관'},
            ]},
            {"name": '인증', "nodes": [
                {"t": '인증'}, {"t": 'JWT'}, {"t": 'OAuth'},
                {"t": 'Basic 인증'}, {"t": 'Token 인증'}, {"t": 'Cookie 인증'},
                {"t": 'OpenID', "s": '순서 무관'}, {"t": 'SAML', "s": '순서 무관'},
            ]},
        ]),
    dict(
        slug='backend-roadmap--s4',
        title='4단계 캐싱, 웹 서버, 보안',
        desc='캐싱과 웹 서버를 거쳐 웹 보안으로 이어지는 구간. Redis 와 Nginx 가 추천이다.',
        zones=[
            {"name": '캐싱', "nodes": [
                {"t": 'Redis'}, {"t": 'Memcached', "s": '대안'}, {"t": 'HTTP Caching'},
            ]},
            {"name": '웹 서버', "nodes": [
                {"t": 'Nginx'}, {"t": 'Apache', "s": '대안'}, {"t": 'Caddy', "s": '대안'},
                {"t": 'MS IIS', "s": '대안'},
            ]},
            {"name": '웹 보안', "nodes": [
                {"t": '웹 보안'}, {"t": 'MD5'}, {"t": 'SHA'},
                {"t": 'scrypt'}, {"t": 'bcrypt'}, {"t": 'HTTPS'},
                {"t": 'OWASP 위험'}, {"t": 'CORS'}, {"t": 'SSL/TLS'},
                {"t": 'CSP'}, {"t": '서버 보안'},
            ]},
        ]),
    dict(
        slug='backend-roadmap--s5',
        title='5단계 AI',
        desc='2026년판에 새로 들어온 구간. LLM 기초에서 코딩 도구를 거쳐 AI 기능 개발로 이어진다.',
        zones=[
            {"name": '기초', "nodes": [
                {"t": 'LLM 동작 원리'}, {"t": '기존 코딩과의 차이'}, {"t": '임베딩'},
                {"t": '벡터'}, {"t": 'RAG'},
            ]},
            {"name": 'AI 코딩 도구', "nodes": [
                {"t": 'Claude Code'}, {"t": 'Cursor', "s": '대안'}, {"t": 'Copilot', "s": '대안'},
                {"t": 'Antigravity', "s": '대안'}, {"t": '프롬프팅 기법'}, {"t": 'Agents'},
                {"t": 'MCP'}, {"t": 'Skills'},
            ]},
            {"name": '적용 분야', "nodes": [
                {"t": '코드 리뷰'}, {"t": '리팩터링'}, {"t": '문서 생성'},
            ]},
            {"name": 'AI 기능 개발', "nodes": [
                {"t": '스트리밍'}, {"t": '구조화된 출력'}, {"t": 'Function Calling'},
                {"t": 'Gemini'}, {"t": 'OpenAI'}, {"t": 'Anthropic'},
            ]},
        ],
        focal=0),
    dict(
        slug='backend-roadmap--s6',
        title='6단계 심화',
        desc='테스트와 CI/CD 에서 DB 심화, 메시지 브로커, 검색엔진, 아키텍처 패턴으로 이어지는 구간.',
        zones=[
            {"name": '테스트', "nodes": [
                {"t": '통합 테스트'}, {"t": '단위 테스트'}, {"t": '기능 테스트'},
            ]},
            {"name": 'DB 심화', "nodes": [
                {"t": '트랜잭션'}, {"t": 'ORM', "s": '순서 무관'}, {"t": 'ACID'},
                {"t": '정규화'}, {"t": '장애 유형'}, {"t": '성능 프로파일링'},
            ]},
            {"name": '메시지 브로커 · 검색엔진', "nodes": [
                {"t": 'Kafka'}, {"t": 'RabbitMQ', "s": '대안'}, {"t": 'Elasticsearch'},
                {"t": 'Solr', "s": '대안'},
            ]},
            {"name": '아키텍처 패턴', "nodes": [
                {"t": '모놀리식'}, {"t": '마이크로서비스'}, {"t": 'SOA'},
                {"t": '서버리스'}, {"t": '서비스 메시'}, {"t": '12 Factor App'},
                {"t": 'LXC'},
            ]},
        ]),
    dict(
        slug='backend-roadmap--s7',
        title='7단계 규모 대응',
        desc='실시간 데이터와 DB 확장, NoSQL 을 거쳐 대규모 서비스 대응으로 이어지는 구간.',
        zones=[
            {"name": '실시간 데이터', "nodes": [
                {"t": 'SSE'}, {"t": 'WebSocket'}, {"t": '롱·숏 폴링'},
            ]},
            {"name": 'DB 확장', "nodes": [
                {"t": '인덱스'}, {"t": '복제', "s": '순서 무관'}, {"t": '샤딩', "s": '순서 무관'},
                {"t": 'CAP 정리', "s": '순서 무관'},
            ]},
            {"name": 'NoSQL', "nodes": [
                {"t": 'Firebase'}, {"t": 'RethinkDB', "s": '대안'}, {"t": 'MongoDB'},
                {"t": 'CouchDB', "s": '대안'}, {"t": 'Redis'}, {"t": 'DynamoDB', "s": '대안'},
                {"t": 'ClickHouse'}, {"t": 'Cassandra', "s": '대안'}, {"t": 'ScyllaDB', "s": '대안'},
                {"t": 'Neo4j'}, {"t": 'AWS Neptune', "s": '대안'}, {"t": 'DGraph', "s": '대안'},
                {"t": 'Influx DB'}, {"t": 'TimescaleDB', "s": '대안'},
            ]},
            {"name": '대규모 서비스 대응', "nodes": [
                {"t": '관측성'}, {"t": '계측'}, {"t": '모니터링'},
                {"t": '텔레메트리'}, {"t": '우아한 성능 저하'}, {"t": '스로틀링'},
                {"t": '백프레셔'}, {"t": '부하 분산'}, {"t": '서킷 브레이커'},
            ]},
        ]),
]

for spec in D:
    out = OUT / f"{spec['slug']}.svg"
    h = build(spec["zones"], out, spec["title"], spec["desc"],
              focal_zone=spec.get("focal"))
    n = sum(len(z["nodes"]) for z in spec["zones"])
    print(f"{out.name}  높이 {h}  노드 {n}")

print("총 노드", sum(len(z["nodes"]) for s in D for z in s["zones"]))
