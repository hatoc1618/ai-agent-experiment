# /discussion Slash Command - Multi-Expert Debate Framework

議論・協議機能を呼び出すスラッシュコマンド

Fast implementation guide for invoking 3-expert discussions about any agenda.

---

## 🚀 Quick Start

```bash
# Make executable
chmod +x /Users/in/ai-agent-experiment/tools/discussion_command.py

# Create symlink for easy access
ln -s /Users/in/ai-agent-experiment/tools/discussion_command.py /usr/local/bin/discussion

# Test installation
discussion discuss "テスト議題"
```

---

## 📖 Basic Usage

```bash
# Start a collaborative discussion
discussion discuss "200+ファイルのPythonリファクタリング戦略"

# Start a debate (adversarial challenge)
discussion discuss "テスト自動生成 vs テスト不要" --mode debate

# Start Socratic inquiry (question-driven)
discussion discuss "Obsidian × Claude Code統合の最適設計" --mode socratic

# Get JSON format for integration
discussion discuss "アジェンダ" --json
```

---

## 🎭 3 Expert Roles

### 1. **ARCHITECT** (建築家)
- **視点**: 理想的、包括的、品質重視
- **焦点**: システム設計、長期戦略、ベストプラクティス
- **特徴**: 理論的、詳細、前向き思考

### 2. **PRAGMATIST** (実用主義者)
- **視点**: 現実的、実装可能、コスト重視
- **焦点**: リソース制約、段階化、ROI優先
- **特徴**: 直接的、結果志向、地に足がついた

### 3. **CRITIC** (批評家)
- **視点**: 懐疑的、リスク重視、仮定挑戦
- **焦点**: 隠れたリスク、矛盾、盲点検出
- **特徴**: 質問的、徹底的、証拠ベース

---

## 🔄 3 Discussion Modes

### 1. **DISCUSSION** (協力的)
各専門家が互いの視点を尊重しながら、異なるレンズから分析
- 相互補完的なインサイト
- 統合的な理解
- 複数視点の総合
```bash
discussion discuss "アジェンダ"
```

### 2. **DEBATE** (対抗的)
専門家が互いの仮定に異議を唱え、立場を擁護
- 厳密な検証
- 矛盾と陥穽の発見
- アイデアの強度テスト
```bash
discussion discuss "アジェンダ" --mode debate
```

### 3. **SOCRATIC** (質問駆動)
戦略的な質問を通じて理解を深化
- 潜在的な仮定の露出
- 思考力の発展
- 段階的な問い

```bash
discussion discuss "アジェンダ" --mode socratic
```

---

## 📋 Usage Examples

### Example 1: Design Decision Debate

```bash
discussion discuss "マイクロサービス vs モノリシック設計を200+ファイルに適用" --mode debate
```

**出力:**
- ARCHITECT: 理想的なマイクロサービス設計
- PRAGMATIST: 実装可能なハイブリッドアプローチ
- CRITIC: 隠れた依存関係と相互作用リスク

### Example 2: Risk Assessment

```bash
discussion discuss "AI生成テストの信頼性と保守性コスト" --mode debate
```

**出力:**
- ARCHITECT: 理想的なテスト戦略
- PRAGMATIST: 現実的なテスト範囲の限定
- CRITIC: テスト脆弱性と長期保守リスク

### Example 3: Technology Choice Socratic

```bash
discussion discuss "Obsidian統合のアーキテクチャ選択" --mode socratic
```

**出力:**
```
ARCHITECT's Questions:
- What are the non-functional requirements?
- How do we ensure architectural consistency?
- What patterns will minimize technical debt?

PRAGMATIST's Questions:
- What's the MVP scope?
- What's the resource constraint?
- How do we measure ROI?

CRITIC's Questions:
- What assumptions underlie this approach?
- What could go wrong at scale?
- How would we validate success?
```

### Example 4: Pragmatic Planning

```bash
discussion discuss "200+ファイルのリファクタリング実行計画" --mode discussion
```

**出力:**
```
【ARCHITECT Analysis】
理想的な4段階アプローチ...

【PRAGMATIST Response】
現実的な優先度限定戦略...

【CRITIC Challenge】
隠れたリスク検出と矛盾指摘...

【Synthesis】
統合アプローチと推奨実行戦略
```

---

## 💻 Advanced Usage

### Get Specific Expert Prompt

```bash
# Get ARCHITECT's detailed analysis for a specific agenda
discussion expert architect --agenda "アジェンダ" --mode discussion

# Get PRAGMATIST's realistic plan
discussion expert pragmatist --agenda "アジェンダ" --mode discussion

# Get CRITIC's risk analysis
discussion expert critic --agenda "アジェンダ" --mode debate
```

### JSON Output for Integration

```bash
discussion discuss "アジェンダ" --json

# Output:
# {
#   "agenda": "アジェンダ",
#   "mode": "discussion",
#   "experts": ["architect", "pragmatist", "critic"],
#   "instructions": {
#     "step_1": "Get ARCHITECT's opening analysis",
#     "step_2": "Get PRAGMATIST's analysis and response",
#     ...
#   }
# }
```

### Piping to Claude Code

```bash
# Get discussion prompt and pipe to Claude
discussion discuss "テーマ" | pbcopy

# Then paste into Claude Code chat for full analysis
```

### Batch Mode (複数アジェンダ)

```bash
cat agendas.txt | while read agenda; do
  echo "=== $agenda ==="
  discussion discuss "$agenda" --mode debate
  echo ""
done
```

---

## 🎯 Typical Workflow

### 1️⃣ **Issue Identification Phase**
```bash
# 議題を特定
discussion discuss "テスト自動生成の失敗率30-40%をどう扱うか" --mode socratic
```

### 2️⃣ **Analysis Phase**
```bash
# 各専門家の視点を集める
discussion discuss "議題" --mode discussion
```

### 3️⃣ **Challenge Phase**
```bash
# 批判的検証で矛盾を露出
discussion discuss "議題" --mode debate
```

### 4️⃣ **Synthesis Phase**
```bash
# 統合的なアプローチを導出
discussion discuss "議題" --mode discussion
```

---

## 🔗 Integration Examples

### Claude Code Hook Integration

```json
{
  "hooks": {
    "decision_needed": {
      "trigger": "ambiguous_requirement",
      "action": "exec discussion discuss '${REQUIREMENT_TEXT}' --mode debate"
    }
  }
}
```

### Shell Alias for Quick Access

```bash
# Add to ~/.zshrc or ~/.bashrc
alias /discuss='discussion discuss'
alias /debate='discussion discuss --mode debate'
alias /ask='discussion discuss --mode socratic'

# Usage:
/discuss "アジェンダ"
/debate "対立する意見"
/ask "戦略的な質問"
```

### Obsidian Integration

Store discussion results in Obsidian:

```bash
# Capture discussion output
discussion discuss "テーマ" > ~/Obsidian/Discussions/$(date +%Y%m%d_%H%M%S).md

# With frontmatter
cat > ~/Obsidian/Discussions/$(date +%Y%m%d).md << EOF
---
type: discussion
mode: debate
date: $(date)
agenda: "アジェンダ"
---

$(discussion discuss "アジェンダ" --mode debate)
EOF
```

---

## 📊 Comparison: Discussion Modes

| Aspect | Discussion | Debate | Socratic |
|--------|-----------|--------|----------|
| **Goal** | Comprehensive analysis | Stress-test ideas | Deep understanding |
| **Tone** | Collaborative | Adversarial | Inquisitive |
| **Output** | Integrated insights | Challenged positions | Strategic questions |
| **Best for** | Complex decisions | Risky plans | Learning/development |
| **Time** | Medium | Long | Variable |

---

## 🧠 Expert Comparison Matrix

|  | Architect | Pragmatist | Critic |
|---|-----------|-----------|--------|
| **Strength** | Comprehensive vision | Realistic roadmap | Risk detection |
| **Weakness** | Optimistic estimates | May skip quality | Can be blocking |
| **Best questions** | "What's ideal?" | "What's feasible?" | "What could fail?" |
| **Validates** | System design | Implementation plan | Risk mitigation |

---

## 🐛 Troubleshooting

### Command not found

```bash
# Check if script is executable
ls -la /Users/in/ai-agent-experiment/tools/discussion_command.py

# Make executable
chmod +x /Users/in/ai-agent-experiment/tools/discussion_command.py

# Verify symlink
ln -s /Users/in/ai-agent-experiment/tools/discussion_command.py /usr/local/bin/discussion
```

### Python not found

```bash
# Check Python installation
python3 --version

# Update shebang if needed
head -1 /Users/in/ai-agent-experiment/tools/discussion_command.py
```

### Invalid mode

```bash
# Valid modes only:
discussion discuss "theme" --mode discussion  # ✅
discussion discuss "theme" --mode debate      # ✅
discussion discuss "theme" --mode socratic    # ✅
discussion discuss "theme" --mode unknown     # ❌
```

---

## 📚 Real-World Examples

### From Final Report (Actual Case Study)

```bash
# Original debate topic
discussion discuss "200+ファイルのPythonリファクタリング: テスト自動生成 vs テスト不要" --mode debate

# This would have generated:
# - ARCHITECT's 4-phase ideal design
# - PRAGMATIST's 2-phase cost-reduced plan
# - CRITIC's hidden risks and contradictions
#
# Result: Modified hybrid approach recommended
```

### Decision Examples

```bash
# For Obsidian integration architecture
discussion discuss "Obsidian統合: ログ直接注入 vs ディスティラー vs LLMLogger" --mode debate

# For test strategy decisions
discussion discuss "AIテスト生成: 自動化vs手動レビュー vs 両方" --mode discussion

# For team learning
discussion discuss "クリーンアーキテクチャの200+ファイルへの適用" --mode socratic
```

---

## 🎓 Learning Path

1. **Begin with DISCUSSION** - Understand all perspectives
2. **Move to DEBATE** - Challenge assumptions
3. **Advance to SOCRATIC** - Ask strategic questions
4. **Integrate learnings** - Apply insights to decisions

---

## 📝 Output Format

### Discussion Mode Output
```
【ARCHITECT's Perspective】
[Ideal, comprehensive analysis]

【PRAGMATIST's Perspective】
[Realistic, cost-focused plan]

【CRITIC's Perspective】
[Risk analysis and challenges]

【Synthesis】
- Convergent insights
- Productive tensions
- Recommended approach
- Open questions
```

### Debate Mode Output
```
【ARCHITECT's Position】
[Defended argument]

【PRAGMATIST Challenges】
[Pragmatic concerns]

【ARCHITECT Responds】
[Defense and counter-arguments]

【CRITIC's Assessment】
[Deeper contradictions]

【Synthesis】
[Resolution or acknowledged trade-off]
```

### Socratic Mode Output
```
【ARCHITECT's Strategic Questions】
1. [Question]
2. [Question]
3. [Question]

【PRAGMATIST's Strategic Questions】
1. [Question]
2. [Question]

【CRITIC's Strategic Questions】
1. [Question]
2. [Question]

【Learning Path】
[How these questions guide understanding]
```

---

## 🔧 Configuration

### Custom Model Preferences

Add to `~/.discussion_config`:
```bash
export DEFAULT_MODE="debate"
export EXPERT_STYLE="formal"
export OUTPUT_FORMAT="markdown"
```

### Obsidian Vault Integration

```bash
export DISCUSSION_VAULT_PATH="~/Obsidian/Strategic Decisions"
export AUTO_SAVE_DISCUSSIONS=true
```

---

## 📞 Tips & Tricks

### Get Focused Analysis Fast
```bash
# Specific expert perspective
discussion expert pragmatist --agenda "テーマ"
```

### Validate Decisions
```bash
# Run through all 3 modes for comprehensive validation
for mode in discussion debate socratic; do
  discussion discuss "決定内容" --mode $mode
done
```

### Create Decision Record
```bash
# Save discussion to Obsidian for audit trail
mkdir -p ~/Obsidian/Decisions
discussion discuss "決定内容" --mode debate > \
  ~/Obsidian/Decisions/$(date +%Y%m%d)_decision.md
```

---

## 📖 References

- **Final Report**: `/Users/in/ai-agent-experiment/output/final_report.md`
- **Agent Prompts**: `/Users/in/ai-agent-experiment/agents/`
- **Design Docs**: `/Users/in/ai-agent-experiment/work/`

---

## ✅ Checklist for Effective Discussions

- [ ] Clear, specific agenda
- [ ] 15-30 minute timeframe expected
- [ ] Choose mode appropriate to decision
- [ ] Document key insights
- [ ] Save in Obsidian for future reference
- [ ] Act on synthesis recommendations

---

**Version**: 1.0.0
**Created**: 2026-03-06
**Status**: Production Ready
