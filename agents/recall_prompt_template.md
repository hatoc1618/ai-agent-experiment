# Task Spawn 時の recall テンプレート

このテンプレートは、Agent タスク発行時に自動的に recall を呼び出すための標準プロンプトです。

## 用途

Task spawning 時、以下のセクションを prompt 冒頭に挿入してください：

```markdown
## 📚 セッション開始時の知識参照

**このタスクを開始する前に、LLMLogger から前回の知識を参照してください。**

### 実行手順

1. 以下のコマンドで stats を確認：
   ```
   mcp__llmlogger__recall_stats()
   ```

2. knowledge_cards ≥ 50 件の場合、以下を実行：
   ```
   mcp__llmlogger__recall(query="project:{PROJECT_NAME} {TASK_KEYWORD}", k=3)
   ```

3. 返却結果から以下を確認：
   - **resolved**: 前回解決したエラーパターン → 同じ問題の重複を避ける
   - **artifacts**: 既存ファイル → DRY 原則に従い、再利用可能な部分を優先
   - **open_questions**: 未解決課題 → このタスクで解決可能か検討

### クエリ例

| タスク内容 | recall クエリ |
|-----------|-------------|
| 認証機能の実装 | `query="project:auth authentication jwt"` |
| パフォーマンス最適化 | `query="project:optimization performance cache"` |
| エラーハンドリング | `query="project:error handling exception"` |
| テスト実装 | `query="project:test pytest unit"` |

---

```

## 設計パターン別テンプレート

### パターンA: 実装タスク（新機能追加）

```markdown
## 🔍 前回の知識から学ぶ

**このタスク開始前に：**

```
recall_stats()
  → knowledge_cards が 50+ であれば、下記を実行

recall(query="project:{PROJECT} {FEATURE_NAME}", k=3)
  → artifacts に「同じ機能の前バージョン」がないか確認
  → open_questions に「この機能に関連する未解決課題」がないか確認
```

**そのうえで、以下を実装してください：**
```

---

### パターンB: バグ修正タスク

```markdown
## 🔍 同じバグが前に起きていないか確認

**このタスク開始前に：**

```
recall_stats()
  → 知識カードを確認

recall(query="project:{PROJECT} error:{ERROR_TYPE} bug:{BUG_SYMPTOM}", k=5)
  → resolved に「同じエラーの解決履歴」がないか確認
  → 前回はどう解決したか、参考にする
```

**この情報を踏まえて、修正を実装してください：**
```

---

### パターンC: 検証・テストタスク

```markdown
## 🔍 前回のテスト知見を活用

**このタスク開始前に：**

```
recall_stats()
  → knowledge_cards を確認

recall(query="project:{PROJECT} test case edge_case", k=3)
  → resolved に「前回検出したバグ」がないか確認
  → artifacts に「テストコード」がないか確認
```

**前回の失敗事例を踏まえて、テストを設計してください：**
```

---

## Task spawn コード例（Python）

```python
# Agent 側での recall 統合例
from agents.recall_manager import get_recall_context

async def spawn_task(task_name: str, task_description: str):
    # 1. recall コンテキストを取得
    context = await get_recall_context(
        query=f"project:{current_project} {task_name}",
        k=3
    )

    # 2. prompt に recall コンテキストを埋め込む
    prompt = f"""
{RECALL_PROMPT_TEMPLATE}

【前回のセッション知見】
{context['resolved']}

{context['artifacts']}

{context['open_questions']}

【本タスク】
{task_description}
"""

    # 3. Agent をスポーン
    agent = Agent.spawn(
        task_name=task_name,
        prompt=prompt
    )

    return agent
```

---

## LLMLogger 統合チェックリスト

実装時に以下を確認してください：

- [ ] agents/*.md ファイルに recall セクション追加済み
- [ ] recall クエリが project タグを含む
- [ ] recall_stats() の件数チェックロジックあり
- [ ] fallback（recall 失敗時）の動作定義あり
- [ ] Task spawn テンプレートが 3パターン以上に対応
- [ ] ドキュメントに使用例が明記されている

---

**作成日**: 2026-03-07
**バージョン**: Phase C MVP v1.0
