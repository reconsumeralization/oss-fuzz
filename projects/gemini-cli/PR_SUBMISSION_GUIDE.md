# PR Submission Guide - OSS-Fuzz Foundation

## Pre-Submission Checklist

### ✅ Code Quality
- [ ] All files follow OSS-Fuzz conventions
- [ ] No hardcoded paths or sensitive data
- [ ] Proper error handling in build scripts
- [ ] Clear, descriptive commit messages

### ✅ DCO Compliance
- [ ] All commits include `Signed-off-by: Your Name <email>`
- [ ] Use `git commit -s` for automatic sign-off
- [ ] Verify with `git log --grep="Signed-off-by"`

### ✅ Testing
- [ ] Local build verification
- [ ] OSS-Fuzz trial build passes
- [ ] Fuzz targets compile successfully
- [ ] Basic seed corpora work

### ✅ Documentation
- [ ] README.md explains the PR clearly
- [ ] PR_STRATEGY.md outlines phased approach
- [ ] Code comments explain complex logic
- [ ] Contact information provided

## PR Title Format
```
feat(oss-fuzz): Add foundation setup for Gemini CLI fuzzing (Phase 1)
```

## PR Description Template
```markdown
## Overview
This PR establishes the foundation for OSS-Fuzz integration with Gemini CLI.

## Changes
- Add basic Go fuzzing configuration (3 targets)
- Include minimal Dockerfile and build script
- Add comprehensive .gitignore
- Provide clear documentation

## Testing
- [x] OSS-Fuzz trial build passes
- [x] 3 fuzz targets compile successfully
- [x] Basic seed corpora work correctly

## Phase Strategy
This is Phase 1 of 4-phase integration. See PR_STRATEGY.md for details.

## Contact
reconsumeralization@gmail.com
```

## DCO Fix Commands
If DCO issues arise:
```bash
# Fix all commits in branch
git rebase HEAD~N --signoff

# Force push (use with caution)
git push --force-with-lease origin branch-name
```

## Maintainer-Friendly Features
- **Small Scope**: Only 3 fuzz targets
- **Clear Documentation**: Every file explained
- **Independent**: No dependencies on future phases
- **Low Risk**: Minimal configuration changes
- **Tested**: Basic functionality verified

## Future Phases
- **Phase 2**: Core functionality (5 additional targets)
- **Phase 3**: Security-critical (4 high-priority targets)
- **Phase 4**: Comprehensive coverage (5 remaining targets)
