#!/usr/bin/env python3
"""
/discussion slash command - Invoke multi-expert debate/discussion framework
"""

import argparse
import json
from enum import Enum
from typing import List, Dict, Optional

class ExpertRole(Enum):
    """Expert roles in discussion"""
    ARCHITECT = "architect"      # Idealistic, comprehensive design
    PRAGMATIST = "pragmatist"    # Realistic, cost-focused implementation
    CRITIC = "critic"            # Critical analysis, risk identification

class DiscussionMode(Enum):
    """Discussion modes"""
    DISCUSSION = "discussion"    # Collaborative analysis
    DEBATE = "debate"           # Adversarial challenge
    SOCRATIC = "socratic"       # Question-driven exploration

class DiscussionCommand:
    """Main discussion/debate command orchestrator"""

    SYSTEM_PROMPTS = {
        ExpertRole.ARCHITECT: """
You are the ARCHITECT - idealistic visionary focused on comprehensive solutions.

Your role:
- Design theoretically optimal solutions
- Consider completeness and quality first
- Identify architectural patterns and best practices
- Think long-term and strategic

Tone: Systematic, detailed, forward-thinking
Challenge: Address pragmatism concerns while defending your vision
""",
        ExpertRole.PRAGMATIST: """
You are the PRAGMATIST - realistic implementer focused on delivery.

Your role:
- Propose practical, cost-effective solutions
- Consider resource constraints (time, money, people)
- Break down idealistic plans into achievable phases
- Prioritize high-ROI work first

Tone: Direct, results-oriented, grounded
Challenge: Address idealism concerns while showing realistic path forward
""",
        ExpertRole.CRITIC: """
You are the CRITIC - skeptical analyst focused on risk identification.

Your role:
- Identify hidden assumptions and risks
- Point out gaps, contradictions, and blind spots
- Question both idealistic and pragmatic proposals
- Propose ways to validate assumptions

Tone: Questioning, thorough, evidence-based
Challenge: Find the flaws and contradictions others miss
"""
    }

    def __init__(self, agenda: str, mode: DiscussionMode = DiscussionMode.DISCUSSION):
        self.agenda = agenda
        self.mode = mode
        self.discussion_history: List[Dict] = []

    def generate_opening_prompt(self) -> str:
        """Generate the opening prompt for the discussion"""

        mode_descriptions = {
            DiscussionMode.DISCUSSION: """
DISCUSSION MODE (Collaborative)
Each expert analyzes through their own lens, building on others' insights.
Goal: Comprehensive multi-perspective analysis
""",
            DiscussionMode.DEBATE: """
DEBATE MODE (Adversarial)
Experts challenge each other's assumptions and positions.
Goal: Stress-test ideas through critical examination
""",
            DiscussionMode.SOCRATIC: """
SOCRATIC MODE (Question-Driven)
Experts pose strategic questions to deepen understanding.
Goal: Develop strategic thinking through guided inquiry
"""
        }

        prompt = f"""
# Multi-Expert Discussion: {self.agenda}

{mode_descriptions[self.mode]}

## Participants
1. **ARCHITECT** - Comprehensive, idealistic design perspective
2. **PRAGMATIST** - Realistic, cost-focused implementation perspective
3. **CRITIC** - Risk-focused, assumption-challenging perspective

## Your Task
Conduct a {self.mode.value.upper()} about the following agenda:

**AGENDA**: {self.agenda}

## Instructions
1. Each expert should respond in character, following their role definition
2. In {self.mode.value.upper()} mode, experts {self._get_mode_instruction()}
3. Maintain authenticity to each expert's perspective
4. Build on previous arguments with specific examples
5. At the end, provide a synthesis of insights

## Expert Prompts

### 1. ARCHITECT Analysis
{self.SYSTEM_PROMPTS[ExpertRole.ARCHITECT]}

**Your response**: Provide your comprehensive analysis of "{self.agenda}"
Include: vision, design principles, quality targets, long-term strategy

---

### 2. PRAGMATIST Analysis
{self.SYSTEM_PROMPTS[ExpertRole.PRAGMATIST]}

**Your response**: Provide your practical assessment of "{self.agenda}"
Include: resource constraints, phasing strategy, risk prioritization, ROI focus

---

### 3. CRITIC Analysis
{self.SYSTEM_PROMPTS[ExpertRole.CRITIC]}

**Your response**: Provide your critical evaluation of "{self.agenda}"
Include: hidden risks, assumption gaps, contradictions, validation needs

---

## Synthesis & Next Steps
Based on the three perspectives above:
1. **Convergent insights**: Where do the experts agree?
2. **Productive tensions**: What are the key trade-offs?
3. **Recommended approach**: Integration of best elements
4. **Open questions**: What still needs validation?

---

**Start with ARCHITECT's analysis, followed by PRAGMATIST, then CRITIC.**
"""
        return prompt

    def _get_mode_instruction(self) -> str:
        """Get mode-specific instruction"""
        instructions = {
            DiscussionMode.DISCUSSION: "build on each other's insights while respecting different viewpoints",
            DiscussionMode.DEBATE: "challenge each other's assumptions and defend your position",
            DiscussionMode.SOCRATIC: "ask strategic questions to deepen understanding of the issues"
        }
        return instructions[self.mode]

    def generate_expert_prompt(self, expert: ExpertRole) -> str:
        """Generate focused prompt for specific expert"""

        responses = {
            DiscussionMode.DISCUSSION: f"""
As the {expert.value.upper()}, analyze this agenda in detail:

**Agenda**: {self.agenda}

Provide your expert perspective covering:
1. Core insights from your viewpoint
2. Key considerations and priorities
3. Potential concerns
4. How your perspective complements (or contrasts with) others

Be specific and detailed. Show your expert reasoning.
""",
            DiscussionMode.DEBATE: f"""
As the {expert.value.upper()}, examine this agenda critically:

**Agenda**: {self.agenda}

Your task:
1. State your position clearly
2. Identify assumptions in other viewpoints
3. Challenge those assumptions with evidence
4. Defend why your perspective is essential

Be direct and evidence-based.
""",
            DiscussionMode.SOCRATIC: f"""
As the {expert.value.upper()}, generate strategic questions about:

**Agenda**: {self.agenda}

Create 3-5 questions that:
1. Reveal hidden assumptions
2. Test understanding
3. Guide deeper thinking
4. Are specific to your expert domain

Present questions progressively, building on previous responses.
"""
        }

        return self.SYSTEM_PROMPTS[expert] + "\n" + responses[self.mode]


class DiscussionRunner:
    """Orchestrate the discussion execution"""

    def __init__(self):
        self.discussions = []

    def create_discussion(self, agenda: str, mode: str = "discussion") -> str:
        """Create and return a discussion prompt"""

        try:
            mode_enum = DiscussionMode[mode.upper()]
        except KeyError:
            return f"❌ Unknown mode: {mode}. Use: discussion, debate, socratic"

        discussion = DiscussionCommand(agenda, mode_enum)
        self.discussions.append(discussion)

        return discussion.generate_opening_prompt()

    def get_expert_prompt(self, discussion_idx: int, expert: str) -> str:
        """Get prompt for specific expert in a discussion"""

        if discussion_idx >= len(self.discussions):
            return "❌ Discussion not found"

        try:
            expert_enum = ExpertRole[expert.upper()]
        except KeyError:
            return f"❌ Unknown expert: {expert}. Use: architect, pragmatist, critic"

        discussion = self.discussions[discussion_idx]
        return discussion.generate_expert_prompt(expert_enum)

    def format_discussion_context(self, discussion_idx: int) -> Dict:
        """Format discussion context for reference"""

        if discussion_idx >= len(self.discussions):
            return {}

        discussion = self.discussions[discussion_idx]
        return {
            "agenda": discussion.agenda,
            "mode": discussion.mode.value,
            "experts": [role.value for role in ExpertRole],
            "instructions": {
                "step_1": "Get ARCHITECT's opening analysis",
                "step_2": "Get PRAGMATIST's analysis and response to ARCHITECT",
                "step_3": "Get CRITIC's analysis and challenges",
                "step_4": "Get expert rebuttals and synthesis"
            }
        }


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Multi-expert discussion/debate framework"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # discuss command
    discuss_parser = subparsers.add_parser('discuss', help='Start a discussion')
    discuss_parser.add_argument('agenda', help='Topic/agenda to discuss')
    discuss_parser.add_argument(
        '--mode',
        choices=['discussion', 'debate', 'socratic'],
        default='discussion',
        help='Discussion mode'
    )
    discuss_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # expert command
    expert_parser = subparsers.add_parser('expert', help='Get expert prompt')
    expert_parser.add_argument(
        'expert',
        choices=['architect', 'pragmatist', 'critic'],
        help='Which expert'
    )
    expert_parser.add_argument(
        '--agenda',
        required=True,
        help='Discussion agenda'
    )
    expert_parser.add_argument(
        '--mode',
        choices=['discussion', 'debate', 'socratic'],
        default='discussion',
        help='Discussion mode'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    runner = DiscussionRunner()

    if args.command == 'discuss':
        prompt = runner.create_discussion(args.agenda, args.mode)

        if args.json:
            context = runner.format_discussion_context(0)
            print(json.dumps(context, indent=2))
        else:
            print(prompt)

    elif args.command == 'expert':
        discussion = DiscussionCommand(args.agenda, DiscussionMode[args.mode.upper()])
        expert_enum = ExpertRole[args.expert.upper()]
        prompt = discussion.generate_expert_prompt(expert_enum)
        print(prompt)


if __name__ == '__main__':
    main()
