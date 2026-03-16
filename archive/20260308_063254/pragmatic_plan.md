# 実装コスト評価（Pragmatist）

> 立場：動作維持と最小変更コストを最重視する。「完璧さより動く仕組み」「理想より実装速度」を優先する。

---

## 1. Architect 案の評価表

| 要素 | コスト | 効果 | 優先度 | 判定 |
|------|--------|------|--------|------|
| ヘキサゴナルアーキテクチャ（Port/Adapter 分離） | 高 | 低（現時点） | 不要 | 後回し。アダプターが1種類しかない間は純粋なオーバーヘッド |
| `KnowledgeTopic` テーブル（階層構造・parent_topic） | 中 | 低 | 不要 | トピック名はフラットな文字列で十分。階層化は Phase 3 以降でいい |
| `KnowledgeEvent` テーブル（イベントログ） | 中 | 低 | 不要 | 状態の「現在値」だけ持てば十分。イベント履歴は最初は不要 |
| `current_knowledge` ビュー | 低 | 中 | あり | ただし GROUP BY ORDER BY の構文が SQLite で正しく動かない。要修正 |
| `KnowledgeRecord.confidence` フィールド | 低 | 中 | あり | ただし初期は 0.5/1.0 の二値で十分。浮動小数点の精度管理は後回し |
| `KnowledgeRecord.decay_rate` フィールド | 低 | 低（初期） | 後回し | フィールドを作るだけならコストゼロ。ロジックは Phase 3 まで触らない |
| `LexicalSignalExtractor`（ルールベース） | 低 | 高 | 必須 | CLAUDE.md に数行書くだけで実現できる。即やる |
| `SemanticSignalExtractor`（LLM 推定） | 高 | 中 | 後回し | LLM 呼び出しのレイテンシ・コスト増大。語彙ルールで 60% 拾えれば十分 |
| `BehaviorSignalExtractor`（bash ログ解析） | 高 | 中 | 後回し | 現状のインフラで bash ログを横断監視する仕組みがない |
| 3 チャンネルフィードバックループ（A/B/C） | 高 | 高 | 段階的 | Channel A（サイレント更新）だけ実装。B/C は後で足す |
| `TeachingStrategySelector` | 中 | 高 | Phase 2 | CLAUDE.md のプロンプト追記で代替可。コード実装は不要 |
| LLMLogger への `report_outcome` 統合 | 低 | 高 | 必須 | 既存インフラを使うだけ。コストほぼゼロ |
| CLAUDE.md への自動エクスポート（バッチ） | 中 | 高 | Phase 2 | 最初は手動更新で十分。自動化は Phase 2 |
| `KnowledgeTopic.related_topics`（関連グラフ） | 高 | 中 | Phase 3 | グラフ構造の管理コストが高い。Phase 3 まで触らない |
| 時間減衰モデル（`decay_rate` 有効化） | 高 | 中 | Phase 3 | 後回し |
| プロアクティブ提案エンジン | 高 | 高 | Phase 3 | 今は不要。動く基盤を先に作る |
| SOLID 原則に基づくモジュール分割（全体） | 高 | 低（現時点） | 不要 | ファイル 1 枚で書ける規模で SOLID は過剰設計 |

**総括：** Architect 案の約 60% は Phase 1 では不要。3 テーブル構成を 1 テーブルに圧縮し、シグナル抽出をコードではなく CLAUDE.md ルールで代替することで、Day 1 から動く仕組みが作れる。

---

## 2. 最小実装プラン（Day 1〜Week 1）

### Day 1：SQLite に 1 テーブルを追加する

既存の `knowledge.db` に以下だけ追加する。

```sql
CREATE TABLE IF NOT EXISTS user_knowledge (
    topic        TEXT NOT NULL,
    level        INTEGER NOT NULL DEFAULT 0,  -- 0=unknown 1=heard 2=practicing 3=mastered
    confidence   REAL NOT NULL DEFAULT 0.5,   -- 0.5=推定 / 1.0=明示確認済み
    raw_utterance TEXT,
    session_id   TEXT,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (topic)
);
```

**なぜこれだけか：**
- `knowledge_topics` テーブルは不要。`topic` は文字列で十分
- `knowledge_events` テーブルは不要。現在の状態だけ持てば教師として機能する
- `record_id` 等の UUID 管理は不要。`topic` を主キーにすれば UPSERT で済む
- `confidence` は 0.5（暗黙推定）/ 1.0（ユーザー明示）の二値から始める

**UPSERT パターン（Claude が実行するとき）：**

```sql
INSERT INTO user_knowledge (topic, level, confidence, raw_utterance, session_id)
VALUES ('tmux', 1, 0.5, 'tmux ってなに', 'session_abc')
ON CONFLICT(topic) DO UPDATE SET
    level = excluded.level,
    confidence = excluded.confidence,
    raw_utterance = excluded.raw_utterance,
    session_id = excluded.session_id,
    updated_at = CURRENT_TIMESTAMP;
```

### Day 1：CLAUDE.md に検知ルールを追加する

CLAUDE.md の適切なセクションに以下を追記する（数行）：

```markdown
## ユーザー知識レベルの自動記録

会話中に以下のパターンを検知したとき、knowledge.db の user_knowledge テーブルを更新すること。

### 検知ルール（LexicalSignal）

| パターン例 | 判定 | level |
|-----------|------|-------|
| 「〜ってなに」「知らなかった」「初めて聞いた」「〜とは？」 | UNKNOWN方向 | 0 |
| 「聞いたことある」「説明してもらった」「そういうものか」 | HEARD方向 | 1 |
| 「使ってみた」「やってみたら」「エラーが出た」「インストールした」 | PRACTICING方向 | 2 |
| 「自分で設定した」「人に説明した」「カスタマイズした」「応用した」 | MASTERED方向 | 3 |

### 記録タイミング
- 検知したその返答の中で記録（sqlite3 CLI か LLMLogger MCP 経由）
- confidence = 0.5（ルールベース推定）
- ユーザーが「まだわからん」「違う」と訂正した場合は confidence = 1.0 で上書き

### セッション開始時の参照
- recall(query="user_knowledge", k=5) で直近の知識状態を確認
- または SELECT topic, level FROM user_knowledge ORDER BY updated_at DESC LIMIT 10
- 知識状態に応じて説明の入り方を変える（已知の概念の再説明を省く）
```

### Week 1：これだけで何が実現できるか

| 教師機能 | 実現可否 | 備考 |
|---------|--------|------|
| 「前回 tmux を聞いていた」という記録の保持 | ○ | Day 1 から動く |
| 既知トピックへの過剰説明の抑制 | △ | CLAUDE.md 参照が機能すれば可能。精度 50〜70% |
| 「unknown な人への比喩説明」モード切替 | △ | プロンプトで誘導。自動切替ではなく意識的切替 |
| 誤判定の修正 | ○ | ユーザーが「まだわからん」と言えば上書き |
| セッション横断の知識継続 | ○ | LLMLogger recall と組み合わせで動く |
| 能動的な学習提案 | × | Phase 3 以降 |
| 説明の深さの自動調整（TeachingStrategySelector） | × | Phase 2 以降 |

**Pragmatist 評価：Week 1 の実装で「教師として機能する度合い」は 25〜30%。**
Architect の「20%」より若干高い根拠：CLAUDE.md ルールが機能した場合、説明入りの省略が即日動くため。

---

## 3. テスト戦略（現実的な範囲で）

### Architect 案の「自動推定エンジン」はどこまで現実的か

`SemanticSignalExtractor`（LLM を呼んで意味解析する）は、**Phase 1 では過剰投資**。

理由：
- LLM に発言の知識レベルを推定させると、追加の API コール or コンテキスト消費が発生する
- 語彙ルール（LexicalSignal）だけで、明確な発言の 60〜70% は拾える
- 残り 30〜40% は「ユーザーが訂正する」か「次の会話で上書きされる」で十分

**現実的なテスト方法：**

```
テスト対象：CLAUDE.md の検知ルールが実際に発火するか

テストシナリオ（手動）：
1. 「tmux ってなに？」と発言する
2. Claude が回答する
3. user_knowledge に (topic='tmux', level=0) が記録されているか確認
   → sqlite3 /Users/in/scripts/LLMLogger/knowledge.db \
      "SELECT * FROM user_knowledge WHERE topic='tmux';"

4. 次セッションで「tmux の話の続きを」と発言する
5. Claude が「先日 tmux を知らなかったと記録されています」と参照するか確認
```

自動テストは Phase 2 から。Phase 1 は「記録された/されなかった」の目視確認で十分。

### 誤判定率の現実的な見積もり

| シグナル種別 | 推定精度 | 対処 |
|------------|---------|------|
| 語彙ルール（明確な発言） | 70〜80% | Day 1 から運用 |
| 語彙ルール（曖昧な発言） | 40〜50% | 誤判定は許容。訂正で上書き |
| LLM 意味推定 | 80〜90% | Phase 2 から。コスト増大に注意 |

---

## 4. 矛盾への Pragmatist の立場

### brief.txt の矛盾：「完全自動 vs ユーザー関与」

Architect は「信頼度グラデーション（3 チャンネル）」という構造的解答を出した。これは設計として正しい。
しかし **Phase 1 でその仕組みを全部作る必要はない**。

Pragmatist の立場：

**「まず記録して、後で直す」**

- 誤判定は最初から起きる。許容する
- 誤判定が起きたとき、ユーザーが「まだわからん」と言えば上書きされる。それで十分
- confidence スコアの精緻な管理（0.65 閾値でチャンネル切替）は Phase 2 以降
- 「1行確認メモを返答末尾に添付する」（Channel B）は実は良いアイデアだが、実装せずに運用してみてから判断する

### 「完全自動」への現実的妥協点

要件 A（完全自動）と要件 B（ユーザー関与）の矛盾に対する答えは：

> **「デフォルト自動、訂正は自然言語で」**

- 記録は自動（CLAUDE.md ルール + LLMLogger）
- 確認プロンプトは原則出さない（オーバーヘッド増大を避ける）
- ユーザーが「違う」と言ったときだけ上書き
- これで要件 A を 80% 満たし、要件 B を最低限担保する

Architect の「Channel B（1行確認メモ）」は有用だが、**毎回表示するとノイズになる**。
Pragmatist 案：信頼度が 0.5 以下のときだけ（＝語彙ルールが曖昧だったとき）、1行メモを出す。実装コスト：CLAUDE.md に 2 行追記するだけ。

---

## 5. Pragmatist 判定：このプランで「教師」として機能するか？

**判定：機能する。ただし部分的に。**

### 機能する部分（Day 1〜Week 1）
- セッション横断での知識の記憶：動く
- 過剰説明の抑制（既知トピックのスキップ）：CLAUDE.md 参照が機能すれば動く
- 誤判定の修正：自然言語で「まだわからん」と言えば動く

### 機能しない部分（Week 1 時点）
- 説明の深さの自動調整：動かない。Claude が CLAUDE.md を参照して意識的に変える必要がある
- 能動的な学習提案：動かない
- 関連トピックの横断的な把握：動かない

### Pragmatist の結論

Architect 案の完全実装（3 テーブル + 3 チャンネル + SOLID モジュール分割）は、**最低でも 2〜3 週間の実装コスト**がかかる。その間、教師機能はゼロのまま。

対して、このプランの最小実装（1 テーブル + CLAUDE.md 数行）は **Day 1 に完了し、翌日から動く**。

> 「25% の完成度で今日から動くもの」 vs 「90% の完成度で 3 週間後に動くもの」
>
> 前者を選ぶ。残りの 65% は動かしながら足せばいい。

---

*コスト評価 by Pragmatist エージェント — 設計の理想は Architect が担う*
