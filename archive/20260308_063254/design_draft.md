# 教師的機能 設計案（Architect）

> 立場：拡張性・構造の清潔さ・理想的なシステム設計を最重視する。実装コストは二次的関心。

---

## 1. 全体アーキテクチャ

### 概念図

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code セッション                          │
│                                                                   │
│  ┌──────────────┐   Signal   ┌─────────────────────────────────┐ │
│  │  ユーザー発言  │ ─────────> │   KnowledgeInferenceEngine      │ │
│  └──────────────┘            │  (Signal Extractor + Classifier) │ │
│                              └────────────┬────────────────────┘ │
│                                           │ KnowledgeEvent        │
│                              ┌────────────▼────────────────────┐ │
│                              │   KnowledgeRepository (Port)     │ │
│                              └────────────┬────────────────────┘ │
│                                           │                       │
│              ┌────────────────────────────┼──────────────┐       │
│              ▼                            ▼              ▼       │
│   ┌──────────────────┐   ┌──────────────────┐  ┌──────────────┐ │
│   │  SQLite Adapter  │   │ LLMLogger Adapter│  │ CLAUDE.md    │ │
│   │  (永続・構造化)   │   │ (セッション横断  │  │ Adapter      │ │
│   │                  │   │  recall統合)     │  │ (高速参照)   │ │
│   └──────────────────┘   └──────────────────┘  └──────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │          TeachingStrategySelector                            ││
│  │   (知識レベル × コンテキスト → 説明スタイル選択)               ││
│  └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 責務の分離（ヘキサゴナルアーキテクチャ）

| レイヤー | コンポーネント | 責務 |
|---------|--------------|------|
| ドメイン層 | `KnowledgeTopic`, `KnowledgeState`, `KnowledgeEvent` | ビジネスルール・状態遷移ロジック |
| アプリケーション層 | `KnowledgeInferenceEngine`, `TeachingStrategySelector` | ユースケース実行 |
| ポート層 | `KnowledgeRepository` (interface) | 永続化の抽象 |
| インフラ層 | SQLite Adapter, LLMLogger Adapter, CLAUDE.md Adapter | 実際の I/O |

---

## 2. 知識状態データモデル

### 状態遷移機械（Formal State Machine）

```
        ┌───────────────────────────────────────────────────────┐
        │              KnowledgeStateMachine                    │
        │                                                       │
        │   UNKNOWN ──[heard_signal]──> HEARD                  │
        │   HEARD   ──[practice_signal]──> PRACTICING          │
        │   PRACTICING ──[mastery_signal]──> MASTERED          │
        │                                                       │
        │   MASTERED ──[confusion_signal]──> PRACTICING        │  ← 劣化可
        │   PRACTICING ──[confusion_signal]──> HEARD           │  ← 劣化可
        │   HEARD ──[confusion_signal]──> UNKNOWN              │  ← 劣化可
        │                                                       │
        │   任意 ──[explicit_override]──> 任意                  │  ← ユーザー訂正
        └───────────────────────────────────────────────────────┘
```

### コアデータモデル（Python dataclass）

```python
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional

class KnowledgeLevel(Enum):
    UNKNOWN    = 0   # 「それってなに」「知らなかった」
    HEARD      = 1   # 「聞いたことある」「説明してもらった」
    PRACTICING = 2   # 「使ってみた」「インストールした」「エラーが出た」
    MASTERED   = 3   # 「自分で設定した」「人に説明できる」「応用した」

class SignalType(Enum):
    IMPLICIT_POSITIVE  = "implicit_positive"   # LLM が推定した正方向シグナル
    IMPLICIT_NEGATIVE  = "implicit_negative"   # LLM が推定した負方向シグナル
    EXPLICIT_CONFIRM   = "explicit_confirm"    # ユーザーの明示的な肯定
    EXPLICIT_DENY      = "explicit_deny"       # ユーザーの明示的な否定・訂正
    BEHAVIOR_OBSERVED  = "behavior_observed"   # 実行・操作などの行動観察

@dataclass
class KnowledgeTopic:
    topic_id: str                    # 正規化済みトピックID（例: "tmux", "git.rebase"）
    canonical_name: str              # 表示名
    parent_topic: Optional[str]      # 階層構造（例: "tmux" の親は "terminal"）
    related_topics: list[str]        # 関連トピック群

@dataclass
class KnowledgeRecord:
    record_id: str
    topic_id: str
    level: KnowledgeLevel
    confidence: float                # 0.0〜1.0（LLM推定の確信度）
    source: SignalType               # このレコードを生成したシグナルの種別
    created_at: datetime
    updated_at: datetime
    session_id: str                  # どのセッションで更新されたか
    raw_utterance: str               # 根拠となった発言（説明可能性のため）
    is_user_verified: bool = False   # ユーザーが手動確認したか
    decay_rate: float = 0.0          # 時間による劣化係数

@dataclass
class KnowledgeEvent:
    """状態変化イベント（Eventドリブン設計）"""
    topic_id: str
    from_level: Optional[KnowledgeLevel]
    to_level: KnowledgeLevel
    signal_type: SignalType
    confidence: float
    raw_utterance: str
    timestamp: datetime
    requires_user_confirmation: bool = False  # 確信度が閾値未満のとき True
```

### SQLite スキーマ

```sql
CREATE TABLE knowledge_topics (
    topic_id         TEXT PRIMARY KEY,
    canonical_name   TEXT NOT NULL,
    parent_topic     TEXT REFERENCES knowledge_topics(topic_id),
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_records (
    record_id        TEXT PRIMARY KEY,
    topic_id         TEXT NOT NULL REFERENCES knowledge_topics(topic_id),
    level            INTEGER NOT NULL CHECK (level BETWEEN 0 AND 3),
    confidence       REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
    source           TEXT NOT NULL,
    session_id       TEXT,
    raw_utterance    TEXT,
    is_user_verified INTEGER DEFAULT 0,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_events (
    event_id         TEXT PRIMARY KEY,
    record_id        TEXT REFERENCES knowledge_records(record_id),
    topic_id         TEXT NOT NULL,
    from_level       INTEGER,
    to_level         INTEGER NOT NULL,
    signal_type      TEXT NOT NULL,
    confidence       REAL NOT NULL,
    raw_utterance    TEXT,
    requires_confirm INTEGER DEFAULT 0,
    timestamp        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- セッション開始時に高速参照するためのビュー
CREATE VIEW current_knowledge AS
    SELECT topic_id, level, confidence, is_user_verified, updated_at
    FROM knowledge_records
    WHERE record_id IN (
        SELECT record_id FROM knowledge_records
        GROUP BY topic_id
        ORDER BY updated_at DESC
    );
```

### 3つのストレージの役割分担

| ストレージ | 役割 | 読み取りタイミング | 書き込みタイミング |
|-----------|------|-----------------|-----------------|
| **SQLite** | 真のレコード。全トピック・全履歴の永続保存。バッチ処理・分析の源泉 | 初回起動時・明示的クエリ | セッション終了時・重要イベント発生時 |
| **LLMLogger** | セッション横断の recall 統合。「前回このユーザーは〇〇について PRACTICING だった」を FTS5/Vector で高速検索 | セッション開始時の recall | report_outcome で更新 |
| **CLAUDE.md** | 最も頻出・高確信度のトピックを人間可読フォーマットで保持。Claude の System Prompt の一部として機能 | 毎ターン（System Prompt として） | SQLite の内容を定期的にエクスポート（上位 N トピック） |

---

## 3. 自動推定エンジン設計

### 3-1. シグナル抽出レイヤー（SignalExtractor）

```
ユーザー発言
    │
    ├── [LexicalSignalExtractor]   語彙レベルのパターンマッチ
    │     例: "なに？" "知らなかった" "初めて聞いた" → UNKNOWN方向
    │     例: "使ってみたけど" "やってみたら" → PRACTICING方向
    │     例: "自分でカスタマイズした" "設定書いた" → MASTERED方向
    │
    ├── [SemanticSignalExtractor]  LLM を用いた意味解析
    │     例: 質問の抽象度・精度・前提の有無を判定
    │     例: エラーの種類から「使おうとした」ことを推定
    │
    └── [BehaviorSignalExtractor]  行動ログからの推定（将来）
          例: bash で `brew install tmux` を実行 → PRACTICING確定
          例: 設定ファイルを編集 → PRACTICING〜MASTERED
```

### 3-2. 分類レイヤー（KnowledgeClassifier）

```python
class KnowledgeClassifier:
    """
    SOLID準拠：単一責務（分類のみ）・オープン拡張可
    """

    def classify(
        self,
        signals: list[Signal],
        current_state: Optional[KnowledgeRecord]
    ) -> KnowledgeEvent:
        """
        複数シグナルを統合して状態変化イベントを生成する。

        設計原則：
        - 正方向の確信が高いシグナルが複数あれば昇格
        - 負方向（混乱・否定）シグナルは即時劣化を検討
        - 確信度が CONFIRMATION_THRESHOLD 未満なら requires_user_confirmation=True
        - 明示的シグナル（EXPLICIT_*）は暗黙的シグナルより優先度が高い
        """
        pass

CONFIRMATION_THRESHOLD = 0.65  # これ未満なら確認フラグを立てる
```

### 3-3. フィードバックループ（誤判定修正）

設計の核心：「完全自動」と「ユーザー関与」を **2つの並行チャンネル** として設計し、排他的にしない。

```
┌──────────────────────────────────────────────────────┐
│                 フィードバックループ設計                  │
│                                                        │
│  Channel A（サイレント自動更新）                         │
│  ─────────────────────────────                        │
│  confidence >= 0.65 のイベント                          │
│  → ユーザーへの通知なしに SQLite を更新                  │
│  → CLAUDE.md に反映                                    │
│                                                        │
│  Channel B（確認付き更新）                               │
│  ─────────────────────────────                        │
│  confidence < 0.65 のイベント                           │
│  → 次の返答末尾に 1行の確認メモを添付                    │
│    「※ tmux の理解度を "practicing" と記録しました。     │
│       違う場合は「tmux まだわからん」と言ってください」    │
│  → ユーザーが否定 → explicit_deny イベント発火 → 即補正  │
│                                                        │
│  Channel C（能動的確認 — 重要イベント時のみ）             │
│  ─────────────────────────────                        │
│  UNKNOWN → MASTERED のような大きな飛躍を検出した場合      │
│  → 「本当に理解していますか？」を明示的に質問              │
└──────────────────────────────────────────────────────┘
```

### 3-4. SOLID 原則に基づくモジュール分割

| 原則 | 適用 |
|------|------|
| **S** Single Responsibility | `SignalExtractor` は抽出のみ。`KnowledgeClassifier` は分類のみ。`KnowledgeRepository` は永続化のみ |
| **O** Open/Closed | 新しいシグナル抽出器（BehaviorSignalExtractor等）を既存コード変更なしに追加可能 |
| **L** Liskov | `SQLiteAdapter` / `LLMLoggerAdapter` / `InMemoryAdapter` は全て `KnowledgeRepository` として置換可能 |
| **I** Interface Segregation | 読み取り用 `KnowledgeReader` と書き込み用 `KnowledgeWriter` を分離 |
| **D** Dependency Inversion | `KnowledgeInferenceEngine` は具体的な SQLite ではなく `KnowledgeRepository` ポートに依存 |

---

## 4. 段階的実装計画

### Phase 1：知識記録基盤（インフラ構築）

**目標：** トピック × 知識レベルをセッション横断で記録できる状態

**マイルストーン：**
1. SQLite に `knowledge_records` テーブル追加
2. `LexicalSignalExtractor`（ルールベース）実装
   - 「なに？」「初めて」「知らなかった」→ UNKNOWN
   - 「使ってみた」「やってみたら」→ PRACTICING
3. セッション終了時に LLMLogger へ `report_outcome` で記録
4. CLAUDE.md に「現在の知識サマリー」セクション追加（手動更新）

**教師として機能する度合い：20%**
- まだ説明スタイルは変わらない
- ただし「前回 tmux を聞いていた」という記録が残る

---

### Phase 2：知識参照と説明スタイル調整

**目標：** セッション開始時に知識レベルを読み込み、説明の深さを自動調整

**マイルストーン：**
1. セッション開始時に `KnowledgeRepository.get_by_topic()` で知識を読み込む
2. `TeachingStrategySelector` 実装
   ```
   UNKNOWN    → 比喩・例え話優先。前提ゼロから
   HEARD      → 具体例で補強。前回の説明への言及
   PRACTICING → つまずきポイントの先回り説明
   MASTERED   → 対等な議論モード。深い技術詳細
   ```
3. CLAUDE.md のシステムプロンプトに知識サマリーを自動注入
4. Channel B（確認付き更新）を実装 → 1行確認メモをレスポンス末尾に添付
5. `SemanticSignalExtractor`（LLM推定）を `LexicalSignalExtractor` と組み合わせる

**教師として機能する度合い：65%**
- 説明の深さが知識レベルに合わせて変わる
- 既知の概念は「ご存知の通り〜」でスキップ
- 誤判定の 35% はユーザーの訂正で修正される

---

### Phase 3：能動的な教育エンジン

**目標：** 学習タイミングを能動的に提案・管理する

**マイルストーン：**
1. **時間減衰モデル**
   - `decay_rate` を用いて「最後の参照から N日経った知識」を検出
   - 「先週 tmux を学んでましたが、使えてますか？」を自然な会話の中で挿入
2. **関連トピックグラフ**
   - `KnowledgeTopic.related_topics` を活用
   - tmux が MASTERED になったら、Vim + tmux の統合を提案
3. **プロアクティブ提案エンジン**
   - ユーザーが似たタスクをしているときに未習得の関連ツールを提示
   - 「このコマンドを毎回打ってますが、Makefile でまとめてみませんか？」
4. **Channel C（能動的確認）の完全実装**
   - 大きな状態遷移（HEARD → MASTERED等）に対して明示的確認

**教師として機能する度合い：90%**
- 学習の設計をエージェントが自律的に行う
- ユーザーは「教えてくれ」と言わなくても学習が進む
- 残り 10% は LLM の意味理解の限界によるもの

---

## 5. 識別された矛盾・設計上の対処

### 矛盾の本質的構造

brief.txt が提示する矛盾は、表面的には「自動化の精度」と「ユーザー負担」のトレードオフだが、より深く見ると **「システムの信頼性はどこが保証するか」** という認識論的な問いである。

```
要件A（完全自動） ←───── 矛盾 ─────→ 要件B（ユーザー関与）
  LLM が判定                              ユーザーが判定
  誤判定リスクあり                         手間・摩擦が増える
```

この矛盾は「解消できない本質的トレードオフ」ではなく、**「信頼度という連続変数」** で設計することで解決できる。

### Architect としての設計的解決：信頼度グラデーション

二択（自動 or 手動）ではなく、**信頼度スコアを軸にした 3チャンネル設計** がこの矛盾の構造的解答である。

```
confidence スコア：0.0 ─────────────────────────── 1.0

0.0 〜 0.40  ：判定を保留。ユーザーへの質問を優先（Channel C）
0.40〜 0.65  ：暫定更新 + 1行確認メモ（Channel B）
0.65〜 1.00  ：サイレント自動更新（Channel A）
```

この設計により：
- **要件 A を満たす：** 高信頼度のケース（発言が明確）は完全自動。ユーザーは何も意識しない
- **要件 B を満たす：** 低信頼度のケースは軽量な確認（1行メモ）で補正機会を提供
- **オーバーヘッドを最小化：** 確認はポップアップ・中断ではなく、応答末尾の 1行に限定

### 残留する設計上の判断

| 問題 | Architect の立場 |
|------|----------------|
| 確信度閾値（0.65 等）はハードコードか？ | 初期はハードコードで可。Phase 3 では個人差を学習して動的調整する拡張ポイントを残す |
| 知識の「劣化」（忘却）をモデル化すべきか？ | 設計上は必須。`decay_rate` をデータモデルに含める。初期値ゼロで無効化し、Phase 3 で有効化 |
| トピックの粒度はどう決めるか？ | 「tmux」「git」単位（粗）から「git.rebase」「tmux.prefix」単位（細）まで階層化。`parent_topic` で表現 |
| CLAUDE.md への自動書き込みは安全か？ | 書き込みは定期バッチ処理（セッション終了時）に限定。ターン中の書き換えは禁止 |

### この矛盾が示すより大きな設計原則

「完全自動 vs ユーザー関与」という二項対立は、**AIシステムにおける自律性とヒューマン・イン・ザ・ループの普遍的なトレードオフ** である。本設計では「信頼度による段階的関与」というパターンで解決したが、これは医療診断支援・自動運転の介入判断など他ドメインでも有効な一般的解法である。

理想的なシステムは「自動か手動か」を固定するのではなく、**信頼度に応じてスペクトラム上で動的に位置を変える** ものである。

---

*設計案 by Architect エージェント — 実装コストは Pragmatist エージェントが評価する*
