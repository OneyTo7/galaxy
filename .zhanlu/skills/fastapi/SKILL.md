---
name: fastapi
description: FastAPI 生产级分层架构与外部集成最佳实践：Router→Service→Repository→Provider 边界、ACL/bulkhead/idempotency、领域异常、DI；适配本项目 DDD 限界上下文。
---

# FastAPI 生产架构 Skill

> 本项目适配：四层对应 `app/contexts/<限界上下文>/{router,service,repository}.py` 与 `providers/`；模块间走 service 接口、不跨上下文直查表（DDD 边界）。

## 分层架构（Router → Service → Repository → Provider）

导入只向下流，层间硬边界不可跨越。

### Router（`app/contexts/<ctx>/router.py`）
- Handler 薄：≤10 行可执行代码
- 允许导入：fastapi、schemas、core.deps、service
- 禁止导入：sqlalchemy、httpx、models、repository
- 每个端点声明 `response_model=` 保 OpenAPI 一致
- 业务端点 `user_id: str = Depends(get_current_user_id)`
- Handler 只解析输入、调一个 service 方法、返回响应

GOOD:
```python
@router.post("/submissions", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    req: SubmissionCreate,
    user_id: str = Depends(get_current_user_id),
    svc: SubmissionService = Depends(get_submission_service),
) -> SubmissionResponse:
    sub = await svc.create(user_id=user_id, code=req.code, lang=req.lang)
    return SubmissionResponse.from_domain(sub)
```

BAD（业务逻辑 + SQL 在 router）:
```python
@router.post("/submissions")
async def create(req: SubmissionCreate, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(...).one()
    ...
```

### Service（`app/contexts/<ctx>/service.py`）
- 禁止导入：sqlalchemy、httpx、boto3、redis、FastAPI Request/Response/HTTPException
- 构造注入 Protocol 类型依赖，非具体类
- 抛领域异常（如 `MisconceptionParseError`），不抛 HTTPException

GOOD:
```python
from app.contexts.diagnose.repositories import DiagnoseRepoProtocol
class DiagnoseService:
    def __init__(self, repo: DiagnoseRepoProtocol):
        self._repo = repo
```

BAD:
```python
from sqlalchemy.orm import Session
class DiagnoseService:
    def __init__(self, db: Session): ...   # 依赖了基础设施
```

### Repository（`app/contexts/<ctx>/repository.py`）
- 唯一允许导入 sqlalchemy 的层
- 实现 Protocol，返回领域对象而非 ORM 模型
- 多租户：查询按 user_id 范围限定

### Provider（`app/contexts/<ctx>/providers/`，如调 MoMA）
- 唯一允许直接 import httpx 的层
- 返回 `GenerateResult | ProviderError`，绝不返回原始 dict
- 每个外部服务用独立 httpx.AsyncClient（bulkhead）

## 文件大小

| LOC | 状态 | 动作 |
| --- | --- | --- |
| 0–399 | 绿 | 无 |
| 400–599 | 黄 | 规划拆分，加 TODO(decompose) |
| 600+ | 红 | 阻止合并，先拆 |

满足任一则转 package：跨 400 且下改动破 500；含 2+ 不相干子域；混 HTTP 与 worker；2+ 调用方各只引一个符号。

## 外部集成

### 反腐层（ACL）
Provider 返回 `GenerateResult | ProviderError`，不返回 dict。

```python
@dataclass(frozen=True)
class GenerateResult:
    misconception_type: str
    evidence: str
    knowledge_point: str
    confidence: float

class ProviderError(Exception):
    def __init__(self, message, *, retryable: bool, code: str | None = None): ...
```

### 每 Provider 独立 bulkhead
每个外部服务用独立 httpx.AsyncClient + 独立 Limits，禁止共享。lifespan 关闭清理。

GOOD:
```python
MOMA_HTTP = httpx.AsyncClient(
    base_url=settings.MOMA_ENDPOINT,
    timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
)

@asynccontextmanager
async def lifespan(app):
    yield
    await MOMA_HTTP.aclose()
app = FastAPI(lifespan=lifespan)
```

BAD: `HTTP = httpx.AsyncClient()` 多 provider 共享 → 无隔离。

### 幂等键
有副作用操作接受 `idempotency_key: UUID`，重试前先查。

### 结构化日志
用 contextvars 贯穿 provider/user_id/request_id，JSON formatter 自动拾取。

## 反模式（见到即拒）
1. service 方法签名含 `db: Session` → 用 Protocol repo
2. service 里 `from app.models import` → repo 返回领域类型
3. 函数内 new httpx.AsyncClient → 用共享 per-provider client
4. service 里 `raise HTTPException` → 抛领域异常
5. router 里 `db.query` → 移到 service 再 repo
6. provider 返回 dict → ACL 违反
7. 共享 httpx.AsyncClient → bulkhead 违反
8. service 里访问 `result["vendor"]["x"]` → ACL 违反
9. `logger.info(f"{user_id} ...")` → 结构化 extra={}
10. 副作用操作无 idempotency_key → 重复风险

## 依赖注入
用 FastAPI `Depends()` + `app/core/deps.py` 工厂函数。不要装 DI 容器（dependency-injector/punq）。

```python
def get_diagnose_service(db: Session = Depends(get_db)) -> DiagnoseService:
    return DiagnoseService(repo=SQLAlchemyDiagnoseRepo(db))
```

## 领域异常
Service 抛领域错误，Router 映射 HTTP。

```python
# contexts/diagnose/exceptions.py
class MisconceptionParseError(Exception): ...
class MoMAUnavailableError(Exception): ...

# contexts/diagnose/router.py
try:
    result = await svc.diagnose(...)
except MoMAUnavailableError:
    raise HTTPException(503, detail="诊断暂不可用")
```
