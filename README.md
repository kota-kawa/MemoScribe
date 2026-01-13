[English](README.en.md) | 日本語

# MemoScribe - Personal Life Secretary

自分専用の秘書（Personal Life Secretary）は、ユーザーが入力・アップロードしたあらゆる情報を安全に蓄積し、LLMとRAG（検索＋生成）で"根拠付き"の回答・文章作成・アドバイス・振り返りを提供する個人向けWebアプリです。

## 特徴

- **根拠付き回答**: 生成結果には必ず参照したメモ/ログ/文書の引用を表示
- **3層データ構造**: Raw（原文）→ Digest（構造化要約）→ Memory（検索対象）
- **プライバシー重視**: ローカル/セルフホスト前提、外部送信は最小限
- **LLM ON/OFF対応**: LLMがなくても基本機能が動作

## 機能

- 📝 **メモ管理**: Markdown対応のメモ作成・編集
- 📅 **日常ログ**: 日々の出来事を記録、自動でダイジェスト生成
- 📄 **文書管理**: PDF/テキスト/Markdownをアップロード、テキスト抽出・検索
- ✅ **タスク管理**: 優先度・期限付きタスク管理
- ⚙️ **好み・ルール**: 個人の好みやポリシーを設定
- 💬 **アシスタント**: 蓄積データに基づく根拠付き回答
- ✍️ **文章生成**: メール作成、リライト、予定提案

## 技術スタック

- Python 3.12
- Django 5.x
- PostgreSQL 16 + pgvector
- Celery + Redis
- OpenAI API（または互換API）

## クイックスタート

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

### ローカル開発

```bash
# 依存関係インストール
pip install -r requirements.txt

# データベースマイグレーション
python manage.py migrate

# 開発サーバー起動
python manage.py runserver
```

### テスト実行

```bash
# pytest実行
docker compose exec web pytest

# カバレッジ付き
docker compose exec web pytest --cov=.
```

### コード品質

```bash
# ruffでリント
ruff check .

# blackでフォーマット
black .
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

MIT License

## 貢献

Issue、Pull Requestを歓迎します。
