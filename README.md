# VitaFlow 简历流

VitaFlow 是一个智能简历生成与优化平台，支持在线编辑、AI 生成与诊断、JD 匹配优化、多主题预览，以及 PDF/Word 导出。

## 功能

- 模块化简历编辑与实时预览
- AI 内容生成、简历诊断和 JD 匹配优化
- 多套模板及字体、颜色、间距等样式配置
- PDF、Word 导出
- MinIO / 阿里云 OSS 文件存储
- 账号注册、邮箱验证与 JWT 登录

## 技术栈

- 后端：FastAPI、SQLAlchemy、Alembic、MySQL、LangChain、LangGraph
- 前端：Vue 3、TypeScript、Vite、Pinia、Tailwind CSS
- 导出与存储：Playwright、WeasyPrint、python-docx、MinIO、阿里云 OSS

## 项目结构

```text
VitaFlow/
├── backend/    # FastAPI API、数据库迁移、AI 与导出服务
└── frontend/   # Vue 3 前端
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8+
- MinIO（可选，也可使用阿里云 OSS）

### 1. 数据库

```sql
CREATE DATABASE vitaflow DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m playwright install chromium
uvicorn app.main:app --reload
```

根据本地环境修改 `backend/.env`。至少需要配置数据库连接和 `JWT_SECRET_KEY`；使用 AI、邮箱验证或对象存储时，还需填写相应服务的凭据。

后端默认运行在 `http://127.0.0.1:8000`。

### 3. 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

前端默认运行在 `http://localhost:5173`。

## 配置说明

完整配置及注释见：

- [`backend/.env.example`](backend/.env.example)
- [`frontend/.env.example`](frontend/.env.example)

常用配置包括：

| 配置 | 用途 |
| --- | --- |
| `DB_*` | MySQL 连接 |
| `JWT_SECRET_KEY` | 登录令牌签名 |
| `SMTP_*` | 注册验证码邮件 |
| `AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL` | OpenAI 兼容模型服务 |
| `STORAGE_PROVIDER` | `minio` 或 `aliyun_oss` |
| `PDF_RENDERER` | `chromium`、`auto` 或 `weasyprint` |
| `VITE_API_BASE_URL` | 前端访问的 API 地址 |

生产环境请关闭 `APP_DEBUG`，使用强随机 `JWT_SECRET_KEY`，并通过环境变量或密钥管理服务注入所有凭据。不要提交 `.env`、用户简历、导出文件或上传文件。

## 构建

```bash
cd frontend
npm run build
```

构建产物位于 `frontend/dist`。生产环境可由 Nginx 托管前端静态文件，并将 `/api` 反向代理到 FastAPI。

## 许可证

本项目采用 [MIT License](LICENSE)。
