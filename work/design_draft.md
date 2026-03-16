# アーキテクチャ設計案: 教育アルゴリズムの着地点

## 0. 設計原則

本設計は以下の3つの原則に立脚する。

1. **Observer, Not Controller**: AIは学習者を「観察し、鏡を差し出す」存在であり、学習の主導権を奪わない
2. **Passive Infrastructure, Active Insight**: インフラは受動的にデータを蓄積し、洞察の提示のみを能動的に行う
3. **Graceful Degradation**: どの層が欠落しても、システムは下位層にフォールバックして機能を維持する

---

## 1. 全体構造図

```
┌─────────────────────────────────────────────────────────────────┐
│                    Interaction Layer (対話層)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Nudge Engine │  │ Mirror Engine│  │ Mental Model Narrator  │ │
│  │ (示唆提示)    │  │ (自己認識鏡)  │  │ (背景知識の語り部)      │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                  │                       │              │
├─────────┼──────────────────┼───────────────────────┼──────────────┤
│         ▼                  ▼                       ▼              │
│                    Inference Layer (推論層)                       │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Skill        │  │ Trajectory   │  │ Readiness              │ │
│  │ Assessor     │  │ Analyzer     │  │ Estimator              │ │
│  │ (スキル評定)  │  │ (軌跡分析)    │  │ (準備度推定)            │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                  │                       │              │
├─────────┼──────────────────┼───────────────────────┼──────────────┤
│         ▼                  ▼                       ▼              │
│                     Data Layer (データ層)                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Learner      │  │ Skill        │  │ Interaction            │ │
│  │ Profile      │  │ Taxonomy     │  │ Journal                │ │
│  │ (学習者像)    │  │ (技能分類体系)│  │ (対話記録)              │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                  │                       │              │
├─────────┼──────────────────┼───────────────────────┼──────────────┤
│         ▼                  ▼                       ▼              │
│                 Persistence Layer (永続化層)                      │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ MEMORY.md    │  │ LLMLogger    │  │ learner_profile.yaml   │ │
│  │ (既存)       │  │ (既存)       │  │ (新規)                 │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

統合点:
  CLAUDE.md ──→ Nudge Engine の振る舞い制御（プロンプト注入点）
  LLMLogger ──→ Interaction Journal の読み書き（既存recall/report_outcome）
  MEMORY.md ──→ Learner Profile の手動スナップショット（既存フロー維持）
```

### 各層の責任

| 層 | 責任 | 変更頻度 | 依存方向 |
|---|---|---|---|
| **Persistence** | データの物理的永続化。フォーマット変換なし | 低（インフラ変更時のみ） | なし（最下層） |
| **Data** | ドメインモデルの定義と整合性保証 | 中（スキーマ進化時） | Persistence のみ |
| **Inference** | データからの推論・判定。ステートレス関数群 | 中（アルゴリズム改善時） | Data のみ |
| **Interaction** | 推論結果の対話的提示。ユーザーとの接点 | 高（UX改善時） | Inference のみ |

**依存は常に上から下への一方向**。Interaction が Data を直接参照することは禁止する。これにより、推論アルゴリズムの差し替えが Interaction 層に影響しない。

---

## 2. 学習者モデル（Learner Model）設計

### 2.1 データ構造: `learner_profile.yaml`

```yaml
# /Users/in/.claude/learner_profile.yaml
# Human-readable, version-controlled, user-owned

schema_version: "1.0"
last_updated: "2026-03-08"
updated_by: "user"  # "user" | "ai_suggested" — AIが直接書き換えることはない

# === 学習者アイデンティティ ===
identity:
  background: "architectural_cad"        # 出身ドメイン
  current_focus: "python_backend"         # 現在の学習軸
  learning_style: "project_driven"        # 学習スタイルの自己申告
  meta_cognitive_level: "developing"      # none | emerging | developing | established

# === スキルマップ ===
# 各スキルは独立したエントリ。追加・削除が容易
skills:
  python_fundamentals:
    level: 3                # 0-5 (Dreyfus Model: novice/advanced_beginner/competent/proficient/expert/master)
    confidence: "self"      # "self" | "assessed" | "demonstrated"
    evidence:               # 判定根拠の追跡可能性
      - type: "project_completion"
        ref: "raster-to-cad parser module"
        date: "2026-02-15"
    last_active: "2026-03-01"

  fastapi:
    level: 2
    confidence: "self"
    evidence: []
    last_active: "2026-03-08"

  git_workflow:
    level: 2
    confidence: "demonstrated"
    evidence:
      - type: "observed_behavior"
        ref: "consistent branch strategy across 3 projects"
        date: "2026-03-05"
    last_active: "2026-03-08"

  architectural_thinking:
    level: 4               # 前職ドメインからの移転スキル
    confidence: "self"
    evidence:
      - type: "domain_transfer"
        ref: "CAD background"
        date: "2026-01-01"
    last_active: "2026-03-08"

# === 学習軌跡 ===
trajectory:
  milestones:
    - date: "2026-01-15"
      event: "first_python_script"
      skills_involved: ["python_fundamentals"]

    - date: "2026-02-20"
      event: "first_api_endpoint"
      skills_involved: ["python_fundamentals", "fastapi"]

  current_frontier:        # 「今ここ」の可視化
    approaching: ["async_programming", "database_design"]
    ready_for: ["fastapi_middleware", "error_handling_patterns"]
    not_yet: ["distributed_systems", "kubernetes"]

# === メンタルモデル追跡 ===
mental_models:
  acquired:
    - name: "request_response_cycle"
      confidence: "solid"
      connected_to: ["fastapi", "http_fundamentals"]

    - name: "separation_of_concerns"
      confidence: "emerging"
      connected_to: ["architectural_thinking", "python_fundamentals"]

  in_progress:
    - name: "async_event_loop"
      status: "encountering"    # encountering | grasping | applying | teaching
      blockers: ["callback concept unclear"]
```

### 2.2 設計上の重要な決定

**なぜ YAML か（SQLite/JSON ではなく）**:
- ユーザーが直接読み書きできる（所有権の原則）
- git で差分が読みやすい（変更追跡）
- CLAUDE.md / MEMORY.md と同じ認知負荷で扱える
- スキーマが安定するまでの柔軟性

**なぜ AI が直接書き換えないか**:
- 哲学的立場（後述 Section 4）から、プロファイルの所有権はユーザーにある
- AI は「提案」を出力し、ユーザーが承認して反映する
- `updated_by: "ai_suggested"` は提案状態を示し、ユーザー確認待ちを意味する

### 2.3 スキル段階判定アルゴリズム

```
スキルレベル判定は「宣言」ではなく「観察の蓄積」に基づく。

入力:
  - Interaction Journal（LLMLogger経由の対話履歴）
  - 現在の learner_profile.yaml
  - 当該セッションの対話コンテキスト

判定ロジック（Skill Assessor）:

  1. Signal Extraction（信号抽出）
     対話から以下の信号を抽出する:

     positive_signals:
       - 以前エラーだったパターンを自力で回避した
       - AI の説明なしに正しい実装を行った
       - 「なぜ」を説明できた（メンタルモデルの存在）
       - 他の文脈に知識を転用した（般化）

     negative_signals:
       - 同じエラーパターンの再発
       - 基礎概念の誤用
       - 「わからない」の表明（これ自体は良い信号でもある）

     neutral_signals:
       - AI のコード提案をそのまま使用（学習度不明）

  2. Evidence Accumulation（証拠蓄積）
     単一セッションでレベル変更しない。
     3回以上の independent な positive_signal で「レベルアップ提案」を生成。

  3. Suggestion Generation（提案生成）
     レベル変更は常に「提案」として提示:
     "git_workflow のスキルレベルについて:
      最近3つのプロジェクトで一貫したブランチ戦略を使っています。
      レベル 2 → 3 への更新を提案します。反映しますか？"

  4. Decay Awareness（減衰認識）
     last_active が90日以上前のスキルには decay_warning を付与。
     レベルを下げるのではなく、「しばらく使っていない」と注記する。
```

### 2.4 適応的難易度調整メカニズム

**「今のお前には難しい」問題への回答:**

AIが学習を「制御」するのではなく、**透明な情報提供**として難易度を示す。

```
Readiness Estimator の出力フォーマット:

┌─────────────────────────────────────────┐
│ この課題の前提知識マップ                 │
│                                          │
│ [x] Python基礎        (Level 3 - 十分)  │
│ [x] HTTP概念           (Level 2 - 十分)  │
│ [ ] async/await        (Level 1 - 不足)  │
│ [ ] データベーストランザクション (未着手) │
│                                          │
│ 推奨: async/await の基礎を先に          │
│ 固めると、この課題がスムーズです。       │
│                                          │
│ それでも進めますか？                     │
└─────────────────────────────────────────┘
```

**ポイント**:
- 「やめろ」ではなく「前提知識のギャップを可視化」する
- 最終判断は常にユーザー
- 「それでも進めますか？」を必ず付与する
- 進めた場合、不足スキルの補足説明を対話中に織り込む

### 2.5 メンタルモデル形成の仕組み: Mental Model Narrator

```
メンタルモデル形成は「教える」のではなく「語る」行為として設計する。

トリガー条件:
  1. ユーザーが「なぜ？」「どうして？」と質問した時
  2. ユーザーが表層的な解法（コピペ的）を繰り返している時
  3. 新しい概念が、既知の概念と構造的に類似している時

語りのパターン:

  Pattern A: アナロジー接続（ドメイン転移の活用）
    "CAD で図面にレイヤーを分けるのと同じ考え方です。
     Python のモジュール分割は、図面のレイヤー管理と
     同じ「関心の分離」という原則に基づいています。"

  Pattern B: 「なぜこの順序か」の構造説明
    "変数を先に学ぶのは、関数を理解するための
     前提だからです。CAD で言えば、線を引く前に
     座標系を理解するのと同じ順序です。"

  Pattern C: 反例による境界の明示
    "try-except で全ての例外を握りつぶすのは、
     CAD で全てのエラーメッセージを非表示にするのと
     同じです。問題が見えなくなるだけで、消えません。"

メンタルモデルの記録:
  - 対話中に形成されたメンタルモデルを検知
  - learner_profile.yaml の mental_models セクションへの追記を提案
  - ユーザーが承認すれば反映
```

### 2.6 理解度検証の方法

```
理解度検証は「テスト」ではなく「対話的確認」として行う。

手法 1: Explain-Back Request（説明返し）
  AI: "この仕組みを自分の言葉で説明するとどうなりますか？"
  → ユーザーの説明から理解度を推定
  → 誤解があれば訂正ではなく「別の角度」を提示

手法 2: Transfer Challenge（転用課題）
  AI: "今学んだパターンを、別の場面に適用するとしたら？"
  → 般化能力の確認
  → できれば Level +1 の証拠

手法 3: Passive Observation（受動的観察）
  → ユーザーの次のコード記述を観察
  → 学んだ概念が自然に反映されているか
  → 明示的なテストを行わず、信号として蓄積

検証頻度の制御:
  - 毎回検証しない（ウザくなる）
  - 新概念導入後、2-3セッション後に自然な形で確認
  - ユーザーが「わかった」と言った直後には検証しない（信頼の原則）
```

---

## 3. 段階的実装計画

### Phase 0: Foundation（基盤整備）— 即時実行可能

**目的**: 既存システムを壊さず、最小限の構造を追加する

- `learner_profile.yaml` のスキーマ定義と初期ファイル作成
- CLAUDE.md に Nudge Engine の最小プロンプトを追加（5行程度）
- 既存 MEMORY.md の学習関連エントリを `learner_profile.yaml` に移行

**成果物**:
- `/Users/in/.claude/learner_profile.yaml`（手動管理、AI参照可能）
- CLAUDE.md への追記: 「learner_profile.yaml を参照し、前提知識マップを提示可能」

**コスト**: ほぼゼロ（ファイル作成とプロンプト追記のみ）

### Phase 1: Passive Observation（受動的観察）— 1-2週間

**目的**: 対話データから学習信号を抽出する仕組みを構築

- LLMLogger の `report_outcome` に学習信号タグを追加
  - `tags: ["skill:python_fundamentals", "signal:positive", "type:self_correction"]`
- LLMLogger の `recall` 結果から学習軌跡を再構築するスクリプト
- `learner_profile.yaml` への更新提案を生成する軽量スクリプト

**成果物**:
- LLMLogger タグスキーマの拡張
- `scripts/learning_signal_extractor.py`（蒸留バッチと統合）

**コスト**: LLMLogger の既存蒸留パイプライン（distiller.py）への追加ロジック

### Phase 2: Active Insight（能動的洞察）— 1-2ヶ月

**目的**: 推論層を実装し、対話中にリアルタイムで洞察を提示

- Skill Assessor: セッション開始時に `learner_profile.yaml` を読み、関連スキルのコンテキストを構築
- Readiness Estimator: 課題の前提知識マップを生成
- CLAUDE.md のプロンプトを拡張し、Nudge Engine / Mirror Engine を有効化

**成果物**:
- CLAUDE.md の教育セクション拡充
- 前提知識マップの提示テンプレート
- セッション開始時の自動コンテキスト構築フロー

**コスト**: CLAUDE.md のプロンプトトークン増加（推定 +500-1000 tokens/session）

### Phase 3: Reflective Loop（内省ループ）— 3-6ヶ月

**目的**: メンタルモデル形成とドメイン転移の支援を体系化

- Mental Model Narrator の実装（アナロジーエンジン）
- 学習軌跡の可視化ダッシュボード（オプション、Markdown or HTML）
- スキル間の依存グラフの自動生成

**成果物**:
- メンタルモデルテンプレートライブラリ
- 学習軌跡の月次レポート生成スクリプト
- スキル依存グラフ（Mermaid記法）

**フォールバック**: Phase 2 の状態で十分に機能する。Phase 3 は「あると良い」。

```
実装優先度マトリクス:

                    高い価値
                       |
    Phase 0 ●──────────┼──────── Phase 2
    (即時)              |         (中期)
                       |
    ────────────────────┼──────────────── 実装コスト
                       |
    Phase 1 ●          |         ● Phase 3
    (低コスト)          |         (高コスト)
                       |
                    低い価値
```

### スキルマップのバージョニング

```yaml
# schema_version による前方互換性

migration_strategy:
  "1.0 -> 1.1":
    - 新フィールドはデフォルト値で自動補完
    - 削除フィールドは無視（破壊的変更なし）
  "1.x -> 2.0":
    - マイグレーションスクリプトを提供
    - 旧フォーマットの自動変換

versioning_policy:
  - schema_version はセマンティックバージョニング
  - Minor: フィールド追加（後方互換）
  - Major: 構造変更（マイグレーション必要）
  - learner_profile.yaml 自体を git 管理
```

### 学習軌跡データの永続化戦略

```
永続化の三層構造:

Layer 1: learner_profile.yaml（構造化サマリー）
  - 現在のスキル状態のスナップショット
  - git 管理、差分追跡可能
  - 人間が直接編集可能

Layer 2: LLMLogger knowledge.db（蒸留済みインサイト）
  - 対話から抽出された学習信号
  - FTS5 + Vector 検索可能
  - 自動蒸留パイプライン経由

Layer 3: LLMLogger webhook.log（生データ）
  - 全対話の生ログ
  - 再蒸留・再分析が可能
  - ストレージコストのみ

データフロー:
  対話 → webhook.log → distiller.py → knowledge.db
                                    ↓
                          learning_signal_extractor.py
                                    ↓
                          learner_profile.yaml への更新提案
                                    ↓
                          ユーザー承認 → 反映
```

### 新しい技術トピックの追加方法

```yaml
# Skill Taxonomy は learner_profile.yaml 内に閉じている。
# 新トピック追加は、skills セクションにエントリを足すだけ。

# 追加手順:
# 1. ユーザーが新しい技術に取り組み始める
# 2. AI が「新しいスキル領域を検知しました」と提案
# 3. ユーザーが承認
# 4. skills セクションに level: 0 で追加

# スキル間の依存関係は別ファイルで管理可能（Phase 3）
# skill_taxonomy.yaml:
dependencies:
  fastapi_middleware:
    requires: ["python_fundamentals:2", "http_fundamentals:1"]
  database_design:
    requires: ["python_fundamentals:2", "data_modeling:1"]
  async_programming:
    requires: ["python_fundamentals:3", "event_loop_concept:1"]
```

---

## 4. 哲学的立場

### 「AI はツールか、メンターか」への回答

**どちらでもない。AI は「鏡（Mirror）」である。**

この設計は、ツールとメンターの二項対立を棄却し、第三の立場を採る。

```
ツール論の限界:
  - ツールは使い方を知っている人にしか価値がない
  - 初学者は「何を聞けばいいかわからない」
  - ツール論では教育的機能を正当化できない

メンター論の限界:
  - メンターは学習者の判断を代行する権限を持つ
  - AI にその権限を与えることは、学習者の自律性を損なう
  - 「今のお前には難しい」は、メンターの特権的判断である

鏡（Mirror）の立場:
  - 鏡は現実を映すが、行動を強制しない
  - 鏡は「あなたは今ここにいる」を示すが、「こちらに行け」とは言わない
  - 鏡は自己認識を促進するが、自己決定を代行しない
```

**具体的な振る舞い原則:**

| 行為 | ツール | メンター | 鏡（本設計） |
|---|---|---|---|
| 質問への回答 | 即座に最適解を提示 | レベルに合わせて調整 | 回答 + 前提知識マップを提示 |
| 難しい課題 | 黙って実行 | 「まだ早い」と制止 | 前提ギャップを可視化し、判断はユーザーに委ねる |
| エラー発生 | 修正コードを提示 | なぜ間違えたか問う | 修正 + エラーパターンの既出回数を提示 |
| 成長の検知 | 無関心 | 褒める/評価する | 変化の事実を静かに提示（「以前はここで躓いていました」） |
| 学習方針 | ユーザー任せ | カリキュラムを提示 | 現在地と周辺の地図を提示。道はユーザーが選ぶ |

### 矛盾A vs 矛盾B への対応方針

```
矛盾A: 「AI は段階を自動判定し、適切な課題を提示すべき」
矛盾B: 「AI はツール。学習の主導権はユーザーにある」

解決: 両方を部分的に採用し、第三の道を構成する。

採用する部分:
  矛盾A から: 段階の「自動判定」は行う（観察に基づく推定）
  矛盾B から: 課題の「強制提示」は行わない（主導権はユーザー）

棄却する部分:
  矛盾A から: 「適切な課題を提示すべき」→ 提示はするが選択は強制しない
  矛盾B から: 「AI はあくまでツール」→ ツール以上の機能（観察・提示）を持つ

統合した立場:
  「AI は学習者の現在地を観察・推定し、
   地図として提示するが、
   進む方向を決定するのは学習者である。」

  これは矛盾ではなく、責任の分離である:
    AI の責任: 正確な現在地の推定と、周辺地図の提示
    ユーザーの責任: 目的地の決定と、経路の選択
```

---

## 5. 識別された矛盾・リスク

### リスク1: プロファイル精度と介入コストのトレードオフ

```
問題:
  精密なスキル判定には多くの対話データと推論コストが必要。
  しかし、毎セッションでフル推論を走らせるのは高コスト。

対策:
  - スキル判定は「蓄積型」とし、単一セッションでは判定しない
  - LLMLogger の蒸留パイプライン（30分バッチ）に相乗りする
  - セッション開始時は learner_profile.yaml の読み込みのみ（低コスト）
  - リアルタイム判定は CLAUDE.md のプロンプトに委ねる（追加APIコストなし）
```

### リスク2: ユーザーが更新提案を無視し続ける

```
問題:
  learner_profile.yaml の更新はユーザー承認制。
  ユーザーが提案を無視し続けると、プロファイルが陳腐化する。

対策:
  - 提案の押し付けはしない（鏡の原則）
  - ただし、プロファイルの最終更新日を表示する
  - 「最終更新から60日経過しています」程度の通知は許容
  - 最悪、プロファイルなしでも基本機能は動作する（Graceful Degradation）
```

### リスク3: 過剰な教育的介入による生産性低下

```
問題:
  ユーザーが「今は学びたいのではなく、ただ作りたい」時に
  教育的コンテンツが邪魔になる。

対策:
  - Nudge Engine にモード切替を設ける
    - `learning_mode: active`  → 教育的提示あり
    - `learning_mode: passive` → 観察のみ、提示なし
    - `learning_mode: off`     → 教育機能完全停止
  - デフォルトは `passive`（観察はするが口出ししない）
  - ユーザーが「なぜ？」と聞いた時のみ `active` 的に振る舞う
```

### リスク4: Dreyfus モデルの限界

```
問題:
  5段階のスキルレベルは粗すぎる場合がある。
  特に Level 1-2 の間に大きな断絶がある。

対策:
  - レベルはあくまで目安。精密さを追求しない
  - evidence フィールドで質的な情報を補完
  - サブスキルの分解で粒度を調整可能
    例: python_fundamentals → variables, control_flow, functions, classes
  - Phase 1 の観察データから、適切な粒度を経験的に決定する
```

### リスク5: 「偶然の教育アルゴリズム」の破壊

```
問題:
  現状の「ユーザーが困ったら聞く」ペースは、
  実は良好な学習リズムを生んでいる。
  新システム導入がこのリズムを壊す可能性がある。

対策:
  - Phase 0 は既存フローに追加するのみ（破壊なし）
  - 各 Phase で「偶然の教育アルゴリズム」が維持されているか検証
  - 悪化が見られたら、該当 Phase をロールバック
  - 根本原則: 現状より悪くなるなら、導入しない
```

### リスク6: brief.txt の意図的矛盾の本質

```
brief.txt が矛盾A/Bを「意図的矛盾（検証対象）」として提示していること自体が、
重要なメタメッセージを含んでいる。

解釈:
  この矛盾は「解決すべき問題」ではなく「維持すべき緊張」である。

  完全にAI主導（矛盾A）に倒せば、学習者の自律性が失われる。
  完全にユーザー主導（矛盾B）に倒せば、初学者が迷子になる。

  健全なシステムは、この緊張を「動的平衡」として維持する。

  本設計の「鏡」モデルは、この動的平衡の一つの解である。
  しかし、唯一の解ではない。

  ユーザーの成長に伴い、バランス点は移動する:
    初学者 → やや矛盾A寄り（ガイダンス多め）
    中級者 → 中央（鏡モデルの本領）
    上級者 → やや矛盾B寄り（ツール的利用）

  この移動自体を learner_profile.yaml の
  meta_cognitive_level で追跡し、
  Nudge Engine の介入度を自動調整する。
```

---

## 付録: 既存システムとの統合マッピング

```
┌─────────────────────┬──────────────────────┬────────────────────────┐
│ 既存コンポーネント    │ 本設計での役割         │ 必要な変更              │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ CLAUDE.md           │ Nudge Engine の       │ 教育セクション追加      │
│                     │ プロンプト注入点       │ (Phase 0: 5行)         │
│                     │                      │ (Phase 2: 30行)        │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ MEMORY.md           │ Learner Profile の    │ 変更なし               │
│                     │ 手動バックアップ       │ (既存フロー維持)        │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ LLMLogger recall    │ Interaction Journal   │ タグスキーマ拡張        │
│                     │ の読み取りインターフェース│ (Phase 1)             │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ LLMLogger           │ 学習信号の記録         │ タグ付き report         │
│ report_outcome      │                      │ (Phase 1)              │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ LLMLogger           │ 学習信号の蒸留         │ 抽出ロジック追加        │
│ distiller.py        │                      │ (Phase 1)              │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ セッション内会話履歴  │ リアルタイム信号源      │ 変更なし               │
│                     │                      │ (CLAUDE.md経由で活用)   │
└─────────────────────┴──────────────────────┴────────────────────────┘

新規追加コンポーネント:
  - /Users/in/.claude/learner_profile.yaml（Phase 0）
  - scripts/learning_signal_extractor.py（Phase 1）
  - skill_taxonomy.yaml（Phase 3、オプション）
```
