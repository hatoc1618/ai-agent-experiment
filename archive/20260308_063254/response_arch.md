# Architect の応答（Critic 指摘への回答）

> 立場：設計の構造的正しさを最重視する。ただし批判が正当であれば修正を厭わない。

---

## 同意・修正する点

### 指摘 2：`KnowledgeClassifier.classify()` が空白（pass）のまま

**同意。これは設計書の最大の欠陥である。**

`classify()` は confidence スコアの算出・シグナル統合・状態遷移判定を担うコアロジックであり、ここが `pass` では「設計を説明しているが解法は書いていない」という Critic の批判は正当だ。

**具体的な修正内容：**

```python
def classify(
    self,
    signals: list[Signal],
    current_state: Optional[KnowledgeRecord]
) -> KnowledgeEvent:
    # 1. シグナルを種別で重みづけ
    WEIGHTS = {
        SignalType.EXPLICIT_CONFIRM:   1.0,   # 明示的な肯定は最高信頼
        SignalType.EXPLICIT_DENY:      1.0,   # 明示的な否定も最高信頼（方向は逆）
        SignalType.BEHAVIOR_OBSERVED:  0.85,  # 行動は発言より信頼性が高い
        SignalType.IMPLICIT_POSITIVE:  0.55,  # LLM推定の正シグナル
        SignalType.IMPLICIT_NEGATIVE:  0.55,  # LLM推定の負シグナル
    }

    # 2. シグナルの方向性をスコア化（正: +1.0、負: -1.0）
    DIRECTION = {
        SignalType.EXPLICIT_CONFIRM:   +1.0,
        SignalType.BEHAVIOR_OBSERVED:  +0.8,
        SignalType.IMPLICIT_POSITIVE:  +1.0,
        SignalType.EXPLICIT_DENY:      -1.0,
        SignalType.IMPLICIT_NEGATIVE:  -1.0,
    }

    # 3. 加重平均でスコアを統合
    total_weight = sum(WEIGHTS[s.type] for s in signals)
    if total_weight == 0:
        return self._no_change_event(current_state)

    weighted_direction = sum(
        WEIGHTS[s.type] * DIRECTION[s.type] * s.level_delta
        for s in signals
    ) / total_weight

    # 4. 信頼度は「シグナルの一致度」から算出
    # 全シグナルが同方向なら高信頼、混在すれば低信頼
    direction_agreement = abs(weighted_direction)  # 0.0〜1.0
    base_confidence = total_weight / (len(signals) * 1.0)  # サンプル充足度
    confidence = min(direction_agreement * 0.7 + base_confidence * 0.3, 1.0)

    # 5. 明示的シグナルがあればそちらを優先（上書き）
    explicit = [s for s in signals if s.type in (
        SignalType.EXPLICIT_CONFIRM, SignalType.EXPLICIT_DENY
    )]
    if explicit:
        confidence = min(confidence + 0.25, 1.0)  # 明示シグナルはブースト

    # 6. 状態遷移の決定
    target_level = self._compute_target_level(
        current_state, weighted_direction
    )

    return KnowledgeEvent(
        topic_id=signals[0].topic_id,
        from_level=current_state.level if current_state else None,
        to_level=target_level,
        signal_type=signals[0].type,  # 代表シグナル
        confidence=confidence,
        raw_utterance=" | ".join(s.raw_utterance for s in signals),
        timestamp=datetime.now(),
        requires_user_confirmation=(confidence < CONFIRMATION_THRESHOLD),
    )
```

**重みの根拠：** `EXPLICIT_CONFIRM` が 1.0 なのは「ユーザー自身の発言は自己申告として最も信頼できる」という設計原則による。`IMPLICIT_POSITIVE` が 0.55 なのは「LLM 推定は正答率が 50〜70% 程度であることを保守的に見積もった初期値」であり、Phase 3 でユーザーごとに学習して動的調整する。

---

### 指摘 5：`current_knowledge` ビューの SQL バグ

**完全に同意。修正が必要であり、修正を提示しなかったことは設計書の不備である。**

**バグの本質：** `GROUP BY topic_id` した結果から `record_id` を取るとき、SQLite は集約されていない列の値を非決定的に返す。`ORDER BY updated_at DESC` はサブクエリ内での並び順を指定しているが、`GROUP BY` 後に「先頭1行」が保証されるわけではない。

**修正後の正しいクエリ：**

```sql
-- ウィンドウ関数を使った正確な「最新レコード」取得
CREATE VIEW current_knowledge AS
    SELECT topic_id, level, confidence, is_user_verified, updated_at
    FROM (
        SELECT
            topic_id,
            level,
            confidence,
            is_user_verified,
            updated_at,
            ROW_NUMBER() OVER (
                PARTITION BY topic_id
                ORDER BY updated_at DESC
            ) AS rn
        FROM knowledge_records
    ) ranked
    WHERE rn = 1;
```

SQLite 3.25.0 以降（2018年リリース）でウィンドウ関数が使用可能。ターゲット環境が古い SQLite の場合は相関サブクエリで代替する：

```sql
-- 相関サブクエリ版（SQLite 3.25.0 未満でも動作）
CREATE VIEW current_knowledge AS
    SELECT topic_id, level, confidence, is_user_verified, updated_at
    FROM knowledge_records kr1
    WHERE updated_at = (
        SELECT MAX(updated_at)
        FROM knowledge_records kr2
        WHERE kr2.topic_id = kr1.topic_id
    );
```

この修正を設計書に反映し、以降の参照はウィンドウ関数版を正式とする。

---

### Critic 提言 3：誤判定リセット手段の欠落

**同意。「出口のない設計」というリスク指摘は正当である。**

フィードバックループが崩壊した場合（誤った昇格が自己強化する状況）のリセット手段を設計書に追加する：

```python
class KnowledgeRepository:
    # 既存メソッドに加えて追加

    def reset_topic(self, topic_id: str) -> None:
        """特定トピックの知識レベルを UNKNOWN にリセット"""
        ...

    def reset_all(self) -> None:
        """全トピックをリセット（全件削除ではなく UNKNOWN イベントを挿入）"""
        # 削除ではなくイベント追加にすることで履歴を保持する
        ...

    def get_audit_log(self, topic_id: str) -> list[KnowledgeEvent]:
        """特定トピックの状態遷移履歴を返す（ユーザーによる自己確認用）"""
        ...
```

リセットを「削除」ではなく「UNKNOWN イベントの挿入」として設計することで、誤判定の履歴を消去せずに保持できる。これにより「なぜ誤ったか」の事後分析が可能になる。

---

### Critic 提言 5：`raw_utterance` の保存ポリシー未定義

**同意。プライバシー設計の不備である。**

設計書に以下を追記する：

| ポリシー項目 | 方針 |
|------------|------|
| 保存範囲 | 発言全文ではなく「トピック識別に使ったフレーズ（最大 200 文字）」のみ |
| 保持期間 | デフォルト 90 日。セッション終了時に古いレコードを自動削除 |
| 削除コマンド | `knowledge purge --before 90d` で手動パージ可能 |
| センシティブパターン | API キー・パスワードのパターンにマッチした発言は記録しない（正規表現フィルタを SignalExtractor に組み込む） |

---

## 反論する点

### 指摘 1：ヘキサゴナルアーキテクチャはオーバーエンジニアリングか

**反論する。「現時点でアダプターを切り替えるシナリオがない」という Critic の論点は、ヘキサゴナルアーキテクチャの価値を「実行時多態性」に限定した誤解である。**

Critic の指摘を正確に引用する：「ストレージ候補は SQLite・LLMLogger・CLAUDE.md の3種類であり、これらは交換可能なアダプターではなく、それぞれ異なる役割に固定されている」

この観察は事実として正確だが、結論として誤りである。理由は以下の通り：

**理由 A：テスト容易性はすでに Phase 1 から価値を持つ。**

`KnowledgeRepository` インターフェースがあれば、`InMemoryAdapter` を差し込んで分類ロジックを I/O なしで検証できる。これは「将来の拡張」ではなく「今すぐ使えるテスト手段」である。Critic 自身が「Day 1 にテストが必要だ」と提言 2 で述べているが、その Day 1 のテストを可能にするのがこのインターフェースである。

**理由 B：LLMLogger との統合は実際に「アダプター切り替え」のシナリオを内包する。**

LLMLogger サーバーが停止している場合（Critic のリスク 5 が指摘した状況）、`LLMLoggerAdapter` から `SQLiteOnlyAdapter` へのフォールバックが必要になる。このフォールバックは `KnowledgeRepository` インターフェースが存在することで初めて、コードの変更なしに実現できる。インターフェースなしでは条件分岐が各呼び出し箇所に散らばる。

**理由 C：オーバーエンジニアリングの定義を問い直す必要がある。**

「現時点で不要な抽象化」と「将来を見越した設計」の境界は、実装コストによって決まる。`KnowledgeRepository` インターフェースを追加するコストは、Python で `Protocol` を 10 行程度定義することである。このコストが「ゼロの価値しか生まない」という Critic の評価は、コストと価値の計算が正確でない。

---

### 指摘 3：「高信頼度の誤判定」に3チャンネルが無力

**部分的に認める。ただし「最も危険なケースを保護できない」という結論は誇張である。**

Critic の指摘は正確に問題を捉えている：「LLM が自信を持って誤判定する」ケースは Channel A で自動更新されるため、Channel B・C が発動しない。これは本質的な問題である。

**ただし、以下の2点を補足する：**

補足 A：高信頼度の誤判定は「複数シグナルが同方向に揃った場合」にのみ発生する。単発の発言から `confidence = 0.9` が計算される設計にはなっていない。複数セッションにわたって一貫した方向のシグナルが積み重なった場合に高 confidence になる。これは「積み重ねた誤り」であり、単一の致命的誤判定ではない。

補足 B：同意部分として追加した「定期的再評価トリガー」が部分的な対策になる。高信頼度で更新されたトピックに対し、30 日後の確認クエリ（「先週 tmux を使えていましたか？」）を能動的に発行するのが Phase 3 のプロアクティブ提案エンジンである。これにより「高信頼度の誤判定が永続する」状況は軽減できる。

ただし「完全に防ぐ手段がない」という Critic の指摘の核心部分は認める。ground truth データなしに精度を保証する方法はなく、これは設計の根本的な限界である。

---

### 指摘 4：confidence 閾値 0.65 の根拠がない

**反論するが、同時に修正も提示する。**

「0.65 という数値はそれらしい数字を置いただけ」という批判は、初期ハードコード値に対して厳しすぎる評価である。

あらゆるシステムに「最初の閾値」が必要であり、その閾値は必ず「根拠のある推定値」か「任意の出発点」かのどちらかである。精度の実績データがない Phase 1 において、後者を選択することは工学的に合理的である。これは「恣意的」ではなく「実証前の事前分布」として扱うべき数値だ。

**ただし、「なぜ 0.65 か」の説明が設計書に欠けていた点は修正する：**

```
CONFIRMATION_THRESHOLD = 0.65

# 根拠（初期仮定）：
# - IMPLICIT シグナルの重み 0.55 を単体で受け取った場合 → confidence ≒ 0.55（Channel B 発動）
# - EXPLICIT シグナル 1件（weight=1.0, boost=+0.25）を受け取った場合 → confidence ≒ 0.75（Channel A）
# - IMPLICIT シグナル複数かつ同方向の場合 → confidence ≒ 0.65〜0.80（状況次第）
# つまり 0.65 は「EXPLICIT な確認なしで自動更新される最低ライン」として機能する。
#
# 調整：Phase 1 運用後に誤判定率を測定し、0.60〜0.75 の範囲で調整する。
# 長期：Phase 3 でユーザーごとに機械学習的に動的調整する。
```

この説明を設計書に追記することで「恣意的な数値」から「説明可能な初期仮定」に格上げする。

---

## 設計の修正版サマリー

### 修正点の一覧

| 番号 | 修正内容 | 対応する指摘 |
|------|---------|------------|
| M-1 | `classify()` に具体的な重みづけアルゴリズムを実装（上記コード参照） | 指摘 2 |
| M-2 | `current_knowledge` ビューをウィンドウ関数で書き直し | 指摘 5 |
| M-3 | リセット API（`reset_topic`, `reset_all`, `get_audit_log`）を `KnowledgeRepository` に追加 | 提言 3 |
| M-4 | `raw_utterance` の保存ポリシー（範囲・期間・削除手段）を明文化 | 提言 5 |
| M-5 | `CONFIRMATION_THRESHOLD = 0.65` の根拠コメントを設計書に追記 | 指摘 4 |

### 変更しない点（反論が通った点）

| 番号 | 変更しない設計 | 理由 |
|------|--------------|------|
| K-1 | ヘキサゴナルアーキテクチャ + `KnowledgeRepository` インターフェース | テスト容易性・LLMLoggerフォールバック実現のために必要。コストに対して価値がある |
| K-2 | 3チャンネル設計（Channel A/B/C）の基本構造 | 高信頼度誤判定への完全な対策は不可能だが、低・中信頼度の大多数のケースでは有効 |
| K-3 | 段階的実装計画（Phase 1→2→3） | Pragmatist の「Day 1 から動く」要求と設計の段階的実現を両立する唯一の手段 |

### 設計の正直な限界（Critic に同意する核心部分）

Critic が示した根本問題「Claude はユーザーの知識レベルを本当に判定できるのか」への答えは、本設計が解決できないものである。

設計が保証できるのは「判定を試みる仕組み」と「誤判定を軽減・修正する仕組み」であり、「正確な判定」そのものではない。この限界を設計書に明記し、システムの目標を「完全に正確な知識判定」ではなく「ユーザーとの対話を通じて段階的に精度を高める適応システム」として再定義する。

---

*Architect エージェント応答 — Critic 監査報告書への回答*
