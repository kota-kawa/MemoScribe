# MemoScribe - Personal Life Secretary

MemoScribe is a privacy-first personal life secretary that turns your notes, logs, documents, and preferences into grounded answers and writing support. It is designed as a portfolio-grade product: clear architecture, strong data governance, and explainable outputs with citations.

## Why it stands out (for hiring evaluation)

- **Grounded AI with citations**: every response includes evidence from your own data, demonstrating reliable RAG practices.
- **Three-layer knowledge pipeline**: Raw → Digest → Memory keeps provenance and makes retrieval explainable.
- **Privacy-by-design**: local/self-hosted workflow with granular control over what is sent to the LLM.
- **Production-minded architecture**: Django + PostgreSQL + pgvector + Celery/Redis with clear domain boundaries.
- **LLM optional**: core features function without an LLM, showing robust fallback design.

## Key Features

- 📝 **Notes**: Markdown note creation and editing
- 📅 **Daily Logs**: record events with auto-generated digests
- 📄 **Documents**: upload PDF/Text/Markdown with extraction and search
- ✅ **Tasks**: priority and due-date task management
- ⚙️ **Preferences**: personal rules and policies
- 💬 **Assistant**: grounded answers from your data
- ✍️ **Writing Support**: rewrite, email drafting, scheduling suggestions

## Tech Stack

- Python 3.12
- Django 5.x
- PostgreSQL 16 + pgvector
- Celery + Redis
- OpenAI API (or compatible API)

## Quick Start (Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/MemoScribe.git
cd MemoScribe
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env to set API keys and settings
```

Key settings:
- `DJANGO_SECRET_KEY`: Django secret key (must change for production)
- `LLM_API_KEY`: OpenAI API key (required for LLM features)
- `PII_MASKING`: PII masking toggle (default true)

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. (Optional) Load demo data

```bash
docker compose exec web python manage.py seed_demo
```

Demo user: `demo` / `demo1234`

### 6. Open the app

http://localhost:8000

## Configuration

### Environment Variables

| Variable | Description | Default |
|--------|------|-----------|
| `DJANGO_SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `POSTGRES_*` | PostgreSQL connection settings | - |
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` |
| `LLM_PROVIDER` | LLM provider | `openai` |
| `LLM_API_KEY` | LLM API key | - |
| `LLM_MODEL` | LLM model | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `SEND_NOTES` | Send notes to LLM | `true` |
| `SEND_DIGESTS` | Send digests to LLM | `true` |
| `SEND_DOCS` | Send documents to LLM | `false` |
| `SEND_RAW_LOGS` | Send raw logs to LLM | `false` |
| `PII_MASKING` | PII masking | `true` |
| `LLM_ENABLED` | Enable LLM features | `true` |

### Privacy Controls

From `/settings/`, you can:

- Choose what data types are sent to the LLM
- Toggle PII masking
- Turn LLM features on/off

## Development

### Run tests

```bash
docker compose exec web pytest
```

```bash
docker compose exec web pytest --cov=.
```

### Code quality

```bash
docker compose exec web ruff check .
```

```bash
docker compose exec web black .
```

## Architecture

```
MemoScribe/
├── config/           # Django project settings
├── core/             # Shared utilities, LLM providers
├── notes/            # Notes
├── logs/             # Daily logs, digests
├── documents/        # Document management
├── tasks/            # Task management
├── preferences/      # Preferences, user settings
├── assistant/        # Chat assistant
├── retrieval/        # RAG, embeddings, search
├── audits/           # Audit logs
├── templates/        # HTML templates
├── static/           # Static assets
└── tests/            # Tests
```

## How RAG Works

1. **Indexing targets**
   - Note bodies
   - Digests (summaries, topics, actions)
   - Document chunks
   - Tasks
   - Preferences

2. **Retrieval flow**
   - Embed the user query
   - Retrieve top-k via pgvector cosine similarity
   - Provide results as LLM context

3. **Citations**
   - Responses always include sources
   - If evidence is insufficient, the assistant asks follow-up questions

## License

MIT License

## Contributing

Issues and pull requests are welcome.

<details>
<summary>日本語</summary>

# MemoScribe - Personal Life Secretary

MemoScribeは、メモ・日常ログ・文書・好みを安全に蓄積し、根拠付きの回答や文章作成を支援する「自分専用の秘書」Webアプリです。就職活動のポートフォリオとして、設計の妥当性・運用視点・説明可能性を重視しています。

## 評価が高くなるポイント

- **根拠提示型AI**: 回答は必ず引用付き。RAGの実装力を明示。
- **三層の知識パイプライン**: Raw → Digest → Memoryでプロセスを可視化。
- **プライバシー設計**: ローカル/セルフホスト前提、送信データを細かく制御。
- **運用前提の構成**: Django + PostgreSQL + pgvector + Celery/Redisで堅牢な構成。
- **LLM非依存**: LLMが無い環境でも機能が動作する設計。

## 主な機能

- 📝 **メモ管理**: Markdown対応のメモ作成・編集
- 📅 **日常ログ**: 日々の出来事を記録し自動ダイジェスト化
- 📄 **文書管理**: PDF/テキスト/Markdownの取り込み・検索
- ✅ **タスク管理**: 期限・優先度付きのタスク整理
- ⚙️ **好み・ルール**: 個人のポリシーや好みを登録
- 💬 **アシスタント**: 根拠付き回答
- ✍️ **文章生成**: メール作成、リライト、予定提案

## 技術スタック

- Python 3.12
- Django 5.x
- PostgreSQL 16 + pgvector
- Celery + Redis
- OpenAI API（または互換API）

## クイックスタート（Docker Compose）

### 1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/MemoScribe.git
cd MemoScribe
```

### 2. 環境変数を設定

```bash
cp .env.example .env
# .env を編集してAPIキーなどを設定
```

主な設定項目:
- `DJANGO_SECRET_KEY`: Djangoのシークレットキー（本番環境では必ず変更）
- `LLM_API_KEY`: OpenAI APIキー（LLM機能を使う場合）
- `PII_MASKING`: PIIマスキング（デフォルトtrue）

### 3. Docker Composeで起動

```bash
docker compose up --build
```

### 4. スーパーユーザーを作成

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. （オプション）デモデータを投入

```bash
docker compose exec web python manage.py seed_demo
```

デモユーザー: `demo` / `demo1234`

### 6. ブラウザでアクセス

http://localhost:8000

## 設定

### 環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `DJANGO_SECRET_KEY` | Djangoシークレットキー | - |
| `DEBUG` | デバッグモード | `False` |
| `ALLOWED_HOSTS` | 許可ホスト | `localhost,127.0.0.1` |
| `POSTGRES_*` | PostgreSQL接続設定 | - |
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` |
| `LLM_PROVIDER` | LLMプロバイダ | `openai` |
| `LLM_API_KEY` | LLM APIキー | - |
| `LLM_MODEL` | LLMモデル名 | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | 埋め込みモデル | `text-embedding-3-small` |
| `SEND_NOTES` | メモをLLMに送信 | `true` |
| `SEND_DIGESTS` | ダイジェストをLLMに送信 | `true` |
| `SEND_DOCS` | 文書をLLMに送信 | `false` |
| `SEND_RAW_LOGS` | 生ログをLLMに送信 | `false` |
| `PII_MASKING` | PIIマスキング | `true` |
| `LLM_ENABLED` | LLM機能有効化 | `true` |

### プライバシー設定

設定画面（/settings/）で以下を制御できます：

- LLMに送信するデータ種類の選択
- PIIマスキングのON/OFF
- LLM機能のON/OFF

## 開発

### テスト実行

```bash
docker compose exec web pytest
```

```bash
docker compose exec web pytest --cov=.
```

### コード品質

```bash
docker compose exec web ruff check .
```

```bash
docker compose exec web black .
```

## アーキテクチャ

```
MemoScribe/
├── config/           # Djangoプロジェクト設定
├── core/             # 共通ユーティリティ、LLMプロバイダ
├── notes/            # メモ管理
├── logs/             # 日常ログ、ダイジェスト
├── documents/        # 文書管理
├── tasks/            # タスク管理
├── preferences/      # 好み・ルール、ユーザー設定
├── assistant/        # チャットアシスタント
├── retrieval/        # RAG、埋め込み、検索
├── audits/           # 監査ログ
├── templates/        # HTMLテンプレート
├── static/           # 静的ファイル
└── tests/            # テスト
```

## RAG（検索拡張生成）の仕組み

1. **インデックス対象**
   - メモ本文
   - ダイジェスト（要約・トピック・アクション）
   - 文書チャンク
   - タスク
   - 好み・ルール

2. **検索フロー**
   - ユーザー質問を埋め込みベクトル化
   - pgvectorでコサイン類似度検索
   - 上位k件を取得
   - LLMに文脈として提供

3. **引用表示**
   - 回答には必ず根拠（引用）を表示
   - 根拠不足の場合は追加質問を提示

## ライセンス

Apache License 2.0

## 貢献

Issue、Pull Requestを歓迎します。

</details>
