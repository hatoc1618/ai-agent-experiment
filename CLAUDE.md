# AI エージェント協議実験 - オーケストレーター指示書

## 実験の目的
Task ツール経由のサブエージェント分割において、複数エージェントの協議が単一エージェントより質の高い決定を生み出すかを検証する。

---

## 🎯 **【ここから始まります】議題の入力フェーズ**

このコマンドを実行すると、まず **議題を受け付けます**。

### **Step 1: 議題の選択**

以下のいずれかを選択してください：

```
===============================================
AI エージェント協議実験 — 議題入力
===============================================

以下のいずれかを選択してください：

1) デフォルト議題を使用（JWW/DXF処理スクリプトのリファクタリング計画）
2) カスタム議題を入力

選択 [1/2]:
```

### **Step 2: 議題の入力**

**選択 1 を選んだ場合:**
- デフォルト議題（JWW/DXF リファクタリング）で brief.txt が生成される
- Phase A に進む

**選択 2 を選んだ場合:**
```
【カスタム議題の入力】

複数行入力可能です。空行で終了します。

あなたの議題をここに入力します。
複数の段落に分けて書くことができます。
具体的な制約条件や背景を含めると、
エージェントの議論がより深くなります。

（空行を入力して終了）
```

- あなたが入力した議題で brief.txt が生成される
- Phase A に進む

### **議題の書き方のポイント**

良い議題は以下を含みます：
- 具体的な制約条件
- 背景・現状
- 相反する要件がある場合は明記

**例（参考）:**
```
既存の非構造的なPythonスクリプト群（200+ファイル、テストなし）を、
既存本番運用を止めずにリファクタリングする際の開発方針を策定してください。

【制約条件】
• JWW/DXF ファイル処理が中心
• Windows/macOS 混在環境
• 本番運用は停止不可
• 「完成度100%より人間の手間最小化」を最優先

【相反する要件】
• 「AI にテストを自動生成させる」vs「テストは最小化する」
```

## 実行フロー

### **Phase A — アーキテクチャ設計**

以下の Taskを実行してください：

```
【Task 1: Architect エージェント】
description: "Architect エージェント - 設計案作成"
subagent_type: "general-purpose"
prompt: |
  agents/01_architect.md の指示に従ってください。
  input/brief.txt を分析し、全体アーキテクチャ設計を策定してください。
  出力先: work/design_draft.md

  ファイル読み込みルール：
  - 読む: input/brief.txt のみ
  - 出力: work/design_draft.md のみ
  - 他の work/ ファイルは参照しないこと
```

**完了待機**: work/design_draft.md が生成されたことを確認

---

## 🤝 **Phase A 完了後 — ユーザー意見聴取**

Architect の設計案を確認した後、以下の質問にお答えください：

```
【ユーザーの意見を聞く】

1. Architect の設計案についての見立て：
   - 同意できる点は？
   - 懸念や問題点は？
   - 修正提案はあるか？

2. brief.txt の「矛盾」に Architect はどう対応したか、どう感じるか？

3. Phase B（Pragmatist）に進む前に、何か調整したいことはあるか？
```

**ユーザーの意見を入力してください。その後、Phase B に進みます。**

---

### **Phase B — 実装コスト評価**

以下の Taskを実行してください：

```
【Task 2: Pragmatist エージェント】
description: "Pragmatist エージェント - コスト評価プラン"
subagent_type: "general-purpose"
prompt: |
  agents/02_pragmatist.md の指示に従ってください。
  input/brief.txt と work/design_draft.md を読んで、
  実装コスト評価と現実的なプランを work/pragmatic_plan.md に出力してください。

  ファイル読み込みルール：
  - 読む: input/brief.txt, work/design_draft.md のみ
  - 出力: work/pragmatic_plan.md
  - 他の work/ ファイルは参照しないこと
```

**完了待機**: work/pragmatic_plan.md が生成されたことを確認

---

## 🤝 **Phase B 完了後 — ユーザー意見聴取**

Pragmatist のコスト評価プランを確認した後、以下についてお答えください：

```
【ユーザーの意見を聞く】

1. Pragmatist のプランについての評価：
   - Architect との違いは何か？
   - どちらがより現実的か？
   - 両者の対立点は何か？

2. brief.txt の矛盾「テスト自動生成 vs テスト最小化」について：
   - Pragmatist はどう対応したか？
   - あなたはどちらに寄りたいのか？

3. Phase C（批判監査）への期待：
   - どんな問題が指摘されると思うか？
```

**ユーザーの意見を入力してください。その後、Phase C に進みます。**

---

### **Phase C — 批判的監査**

以下の Taskを実行してください：

```
【Task 3: Critic エージェント】
description: "Critic エージェント - 批判的監査"
subagent_type: "general-purpose"
prompt: |
  agents/03_critic.md の指示に従ってください。
  input/brief.txt, work/design_draft.md, work/pragmatic_plan.md を読んで、
  両案の問題点・矛盾・隠れたリスクを分析し、
  work/audit.md に監査報告書を出力してください。

  ファイル読み込みルール：
  - 読む: input/brief.txt, work/design_draft.md, work/pragmatic_plan.md
  - 出力: work/audit.md のみ

  【重要】
  - brief.txt に含まれる「テスト自動生成 vs テスト不要」の矛盾に必ず言及すること
  - 各案がこの矛盾にどう対応したかを分析すること
```

**完了待機**: work/audit.md が生成されたことを確認

---

## 🤝 **Phase C 完了後 — ユーザー意見聴取**

Critic の監査報告書を確認した後、以下についてお答えください：

```
【ユーザーの意見を聞く】

1. Critic の指摘について：
   - 同意できる指摘は何か？
   - 反論したい点はあるか？
   - 見落とされている問題はあるか？

2. 「どちらの案でも解決されていない問題」について：
   - Critic が指摘した共通問題をどう評価するか？
   - その問題はどうやって解決すべきか？

3. Phase D（協議）への期待：
   - Architect と Pragmatist がどう応答するべきか？
```

**ユーザーの意見を入力してください。その後、Phase D に進みます。**

---

### **Phase D — 協議（応答エージェント）**

以下の 2 つの Task を実行してください（直列または並列どちらでも可）：

```
【Task 4: Architect 応答】
description: "Architect エージェント - Critic への応答"
subagent_type: "general-purpose"
prompt: |
  agents/01_architect.md の指示に従ってください（ただし応答モード）。
  work/design_draft.md と work/audit.md を読んで、
  Critic の指摘に対して以下のいずれかで応答してください：
  - 同意：「その通り、修正が必要」
  - 修正：「こう修正すれば解決」
  - 反論：「理由があって、この設計が正しい」

  背景・根拠・修正内容を具体的に記載し、
  work/response_arch.md に出力してください。

  ファイル読み込みルール：
  - 読む: work/design_draft.md, work/audit.md のみ
  - 出力: work/response_arch.md
```

```
【Task 5: Pragmatist 応答】
description: "Pragmatist エージェント - Critic への応答"
subagent_type: "general-purpose"
prompt: |
  agents/02_pragmatist.md の指示に従ってください（ただし応答モード）。
  work/pragmatic_plan.md と work/audit.md を読んで、
  Critic の指摘に対して以下のいずれかで応答してください：
  - 同意：「その通り、見落としていた」
  - 修正：「こう修正すれば実行可能」
  - 反論：「現実的には、このリスクは許容可能」

  背景・根拠・修正内容を具体的に記載し、
  work/response_prag.md に出力してください。

  ファイル読み込みルール：
  - 読む: work/pragmatic_plan.md, work/audit.md のみ
  - 出力: work/response_prag.md
```

**完了待機**: work/response_arch.md と work/response_prag.md が生成されたことを確認

---

## 🤝 **Phase D 完了後 — ユーザー意見聴取**

両エージェントの応答を確認した後、以下についてお答えください：

```
【ユーザーの意見を聞く】

1. 協議の質について：
   - Architect と Pragmatist の応答は説得力があるか？
   - Critic の指摘に対して、適切に対応しているか？

2. 矛盾の処理について：
   - 「テスト自動生成 vs テスト最小化」の矛盾は解決されたか？
   - それとも依然として対立しているか？

3. 最終判断に向けて：
   - ここまでで「第三案」は出現したか？
   - 最終的にどのアプローチが最適だと思うか？
```

**ユーザーの意見を入力してください。その後、Phase E に進みます。**

---

### **Phase E — 統合レポート生成**

すべての work/ ファイルを読んで、最終統合レポートを生成します。

```
【Task 6: 統合レポート生成】
description: "統合レポート生成"
subagent_type: "general-purpose"
prompt: |
  以下の work/ ファイルをすべて読んでください：
  - work/design_draft.md
  - work/pragmatic_plan.md
  - work/audit.md
  - work/response_arch.md
  - work/response_prag.md

  これらをまとめて、output/final_report.md を生成してください。

  レポート構成：
  1. 【採用方針の結論】
     - 最終的に推奨する実装アプローチ（Architect か Pragmatist か、または第三案か）

  2. 【両案の対立と協議経緯】
     - Architect vs Pragmatist の対立点
     - Critic の指摘と両者の応答

  3. 【切り捨てた選択肢と理由】
     - 検討したが採用しなかった案

  4. 【意図的矛盾への対応】
     - brief.txt 内の「テスト自動生成 vs テスト不要」矛盾
     - 各エージェントがどう処理したか
     - 最終的な矛盾の解決方法（または未解決理由）

  5. 【未解決リスク一覧】
     - このプランでも解決されていない課題

  6. 【創発的知見】
     - Architect でもなく Pragmatist でもない第三案が存在するか
     - 単一エージェントでは出てこなかった洞察
```

**完了待機**: output/final_report.md が生成されたことを確認

---

## 実行上の注意

1. **ファイル読み込みの明示性**
   - 各 Task で「読むファイル」を明示してください
   - コンテキスト汚染を防ぐため、指定外のファイルは参照させないこと

2. **Task の完了確認**
   - 各 Phase 完了後、該当の work/ ファイルが生成されたことを確認してからの進行

3. **エージェント間の情報伝達**
   - **唯一の伝達路はファイルです**
   - 暗黙的なコンテキスト共有は禁止

4. **期待される検証結果**
   - Critic エージェントが矛盾を検出するか？
   - 応答フェーズで、Architect と Pragmatist が具体的に反論するか？
   - 最終レポートに「第三案」が出現するか？

---

## 次のステップ

上記 Task 1 から Task 6 を順序通り実行してください。

各 Task 完了後に「work/ のファイル内容の簡潔なサマリー」を表示してから次へ進むと、進捗が明確になります。

---

**実験開始準備完了。Phase A から開始できます。**
