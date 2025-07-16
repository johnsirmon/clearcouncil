# ClearCouncil Development Prompt Template

## Context
**Project:** ClearCouncil - Local government transparency tool
**Current State:** Production system with PDF processing, web interface, voting analysis
**Environment:** VS Code Insiders + Claude Code, Python 3.12, .venv active

## Objective
**Primary Goal:** [Describe specific goal here]
**Why:** [Brief explanation of motivation]

## Constraints & Requirements
**Must Have:**
- [ ] Maintain 100% backward compatibility
- [ ] Use existing virtual environment (.venv)
- [ ] Follow existing code patterns
- [ ] Pass existing integration tests

**Nice to Have:**
- [ ] [Optional features]

**Must NOT:**
- [ ] Break existing CLI commands
- [ ] Install packages globally
- [ ] Modify existing database schema without migration
- [ ] Change existing API contracts

## Environment Safety
**Virtual Environment:** /home/johnsirmon/projects/clearcouncil/.venv
**Current Status:** [Run ./check_env.sh to verify]
**Package Manager:** pip with requirements.txt

## Success Criteria
I'll know this worked when:
- ✅ All existing tests pass: `python quick_test.sh`
- ✅ CLI help works: `python clearcouncil.py --help`
- ✅ Web interface loads: `python clearcouncil_web.py serve`
- ✅ [Specific new functionality works]

## Questions for Learning
- What patterns should I follow from existing codebase?
- Are there better practices I should adopt?
- How does this integrate with existing architecture?

---
**Ready to proceed with the above context and constraints.**
