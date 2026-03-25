# notes.md
## Key Architecture Decisions

### Hybrid AI Model Approach
Date: 24 March 2026

The system will follow a hybrid AI model:

DEFAULT MODE (Free/Local):
- Runs on free or local models
- Core functionality works offline or low-cost
- No dependency on paid APIs

UPGRADE MODE (Paid APIs):
- Optional integration with OpenAI, Claude etc.
- Activated after system validation
- Acts as performance booster not dependency

RULES:
- System must work 100% in free mode first
- Paid APIs only enhance, never replace core functions
- Switching between modes must not break workflow
- User chooses when to upgrade

STATUS: Decided ✅
