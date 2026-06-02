# Multi Agent Contract Review Backend

合同审查后端服务，基于 FastAPI 实现。

当前版本使用规则库、多 Agent 流程和可选 LLM 条款抽取完成合同初筛，包括：

- Clause Extraction Agent：优先调用 LLM 提取关键条款原文片段，失败时回退到关键词抽取
- Risk Analysis Agent：根据规则库识别风险
- Policy Check Agent：生成规则检查结果
- Human Review Agent：判断是否需要人工复核
- QA Agent：生成审计日志

## 规则库

当前规则库包含 8 条合同初筛规则：

| ruleId | 规则 | 风险等级 |
| --- | --- | --- |
| R003 | 付款节点检查 | medium |
| R005 | 验收条款检查 | high |
| R011 | 责任上限检查 | medium |
| R012 | 违约责任检查 | medium |
| R016 | 知识产权归属检查 | high |
| R020 | 单方解除权检查 | high |
| R025 | 保密条款检查 | medium |
| R030 | 争议解决条款检查 | medium |

## 启动

```bash
make dev
```

等价于：

```bash
uv run uvicorn app.main:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

## LLM 配置

后端使用 OpenAI-compatible SDK 调用 DeepSeek。复制 `.env.example` 为 `.env` 后填入密钥：

```bash
cp .env.example .env
```

```env
LLM_PROVIDER=deepseek
LLM_API_KEY=你的 DeepSeek API Key
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
LLM_TIMEOUT_SECONDS=30
```

如果未配置 `LLM_API_KEY`，或 LLM 调用失败，Clause Extraction Agent 会自动回退到关键词抽取，接口仍会返回审查结果。审计日志中会记录条款抽取来源。

## 接口

### Health Check

```http
GET /health
```

返回：

```json
{
  "status": "ok"
}
```

### Contract Review

```http
POST /contracts/review
```

请求体：

```json
{
  "contract_text": "乙方为甲方开发订单管理系统并交付源代码。"
}
```

返回字段包括：

- `taskId`
- `status`
- `score`
- `level`
- `summary`
- `agentSteps`
- `policyChecks`
- `risks`
- `humanReviewReasons`
- `auditLog`

## 开发验证

不跑完整测试时，可以先做轻量检查：

```bash
make check
```
