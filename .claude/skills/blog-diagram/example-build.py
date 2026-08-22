#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from gen import build

# 이 스크립트 기준으로 레포 루트를 거슬러 올라간다 (worktree 에서도 동작)
OUT = Path(__file__).resolve().parents[3] / "_includes" / "diagrams"

D = [
    dict(
        slug="backend-roadmap--s1",
        title="1단계 기초",
        desc="인터넷 동작 원리와 HTTP, DNS 를 익힌 뒤 HTML·CSS·JavaScript 기초로 이어지는 구간.",
        zones=[
            {"name": "인터넷 기초", "seq": True, "nodes": [
                {"t": "인터넷 동작 원리"}, {"t": "HTTP"}, {"t": "도메인 · 호스팅"},
                {"t": "DNS"}, {"t": "브라우저 동작 원리"}]},
            {"name": "프론트엔드 기초", "seq": True, "nodes": [
                {"t": "HTML"}, {"t": "CSS"}, {"t": "JavaScript"}]},
        ]),
    dict(
        slug="backend-roadmap--s2",
        title="2단계 언어와 버전 관리",
        desc="백엔드 언어를 하나 고르고 Git 과 저장소 호스팅으로 넘어가는 구간. 언어는 택 1 이다.",
        zones=[
            {"name": "백엔드 언어 · 택 1", "nodes": [
                {"t": "JavaScript · Python · Go", "s": "추천"},
                {"t": "Java · C# · PHP · Ruby · Rust", "s": "대안"}]},
            {"name": "버전 관리", "nodes": [
                {"t": "Git"}, {"t": "GitHub", "s": "추천"}, {"t": "GitLab", "s": "대안"}]},
        ]),
    dict(
        slug="backend-roadmap--s3",
        title="3단계 데이터베이스와 API",
        desc="관계형 DB 에서 공통 개념, API 스타일, 인증으로 이어지는 구간. PostgreSQL 만 추천이고 나머지는 대안이다.",
        zones=[
            {"name": "관계형 DB", "nodes": [
                {"t": "PostgreSQL", "s": "추천"},
                {"t": "MySQL · MariaDB · SQLite", "s": "대안"},
                {"t": "MS SQL · Oracle", "s": "대안"}]},
            {"name": "같이 익히는 개념", "nodes": [
                {"t": "마이그레이션"}, {"t": "N+1 문제"}]},
            {"name": "API 스타일", "nodes": [
                {"t": "REST · JSON API", "s": "추천"},
                {"t": "GraphQL · gRPC · SOAP", "s": "순서 무관"}]},
            {"name": "인증", "nodes": [
                {"t": "JWT"}, {"t": "OAuth"}, {"t": "Basic · Token · Cookie"},
                {"t": "OpenID · SAML", "s": "순서 무관"}]},
        ]),
    dict(
        slug="backend-roadmap--s4",
        title="4단계 캐싱, 웹 서버, 보안",
        desc="캐싱과 웹 서버를 거쳐 웹 보안으로 이어지는 구간. Redis 와 Nginx 가 추천이다.",
        zones=[
            {"name": "캐싱", "nodes": [
                {"t": "Redis", "s": "추천"}, {"t": "Memcached", "s": "대안"}, {"t": "HTTP 캐싱"}]},
            {"name": "웹 서버", "nodes": [
                {"t": "Nginx", "s": "추천"}, {"t": "Apache · Caddy · MS IIS", "s": "대안"}]},
            {"name": "웹 보안", "nodes": [
                {"t": "HTTPS · SSL/TLS"}, {"t": "CORS · CSP"}, {"t": "OWASP Top 10"},
                {"t": "bcrypt · scrypt", "s": "해시"}]},
        ]),
    dict(
        slug="backend-roadmap--s5",
        title="5단계 AI",
        desc="LLM 기초에서 AI 코딩 도구를 거쳐 AI 기능 개발로 이어지는 구간. 2026년에 새로 들어온 단계다.",
        focal=None,
        zones=[
            {"name": "기초", "nodes": [
                {"t": "LLM 동작 원리"}, {"t": "임베딩 · 벡터"}, {"t": "RAG"}]},
            {"name": "AI 코딩 도구", "nodes": [
                {"t": "Claude Code", "s": "추천"}, {"t": "Cursor · Copilot", "s": "대안"},
                {"t": "프롬프팅 기법"}]},
            {"name": "AI 기능 개발", "nodes": [
                {"t": "Agents · MCP"}, {"t": "스트리밍"},
                {"t": "구조화된 출력 · Function Calling"}]},
        ]),
    dict(
        slug="backend-roadmap--s6",
        title="6단계 심화",
        desc="테스트에서 DB 심화, 메시지 브로커와 검색엔진, 아키텍처 패턴으로 이어지는 구간.",
        zones=[
            {"name": "테스트", "nodes": [{"t": "단위"}, {"t": "통합"}, {"t": "기능"}]},
            {"name": "DB 심화", "nodes": [
                {"t": "트랜잭션 · ACID"}, {"t": "정규화"}, {"t": "ORM"}, {"t": "인덱스"}]},
            {"name": "메시지 브로커 · 검색엔진", "nodes": [
                {"t": "Kafka", "s": "추천"}, {"t": "RabbitMQ", "s": "대안"},
                {"t": "Elasticsearch", "s": "추천"}, {"t": "Solr", "s": "대안"}]},
            {"name": "아키텍처 패턴", "nodes": [
                {"t": "모놀리식"}, {"t": "마이크로서비스"}, {"t": "SOA · 서버리스"},
                {"t": "서비스 메시"}, {"t": "12 Factor App"}]},
        ]),
    dict(
        slug="backend-roadmap--s7",
        title="7단계 규모 대응",
        desc="실시간 데이터에서 DB 확장, NoSQL 을 거쳐 대규모 서비스 대응으로 이어지는 구간.",
        zones=[
            {"name": "실시간 데이터", "nodes": [
                {"t": "WebSocket"}, {"t": "SSE"}, {"t": "롱/숏 폴링"}]},
            {"name": "DB 확장", "nodes": [
                {"t": "인덱스"}, {"t": "복제"}, {"t": "샤딩"}, {"t": "CAP 정리"}]},
            {"name": "NoSQL", "nodes": [
                {"t": "MongoDB · Redis", "s": "추천"},
                {"t": "DynamoDB · Cassandra", "s": "대안"},
                {"t": "Neo4j · ClickHouse", "s": "대안"}]},
            {"name": "대규모 서비스 대응", "nodes": [
                {"t": "관측성 · 모니터링"}, {"t": "서킷 브레이커"},
                {"t": "스로틀링"}, {"t": "우아한 성능 저하"}]},
        ]),
]

for d in D:
    p = OUT / f"{d['slug']}.svg"
    h = build(d["zones"], p, d["title"], d["desc"], focal_zone=d.get("focal"))
    print(f"{p.name:34} h={h}")
