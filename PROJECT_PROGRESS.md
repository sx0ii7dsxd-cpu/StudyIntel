# StudyIntel Progress

## How To Use This File
If the user says:
- "go through PROJECT_PROGRESS.md"
- "continue StudyIntel work"
- "resume the production-ready work"

then use this file as the main handoff and continue from the next unfinished item.

## Phase Plan

### Phase 1 - Security and Stability
1. Replace hardcoded secrets with environment variables
2. Implement password hashing
3. Prevent duplicate usernames
4. Add secure file uploads
5. Fix authorization issues for materials
6. Create `requirements.txt`
7. Improve `.gitignore`
8. Disable debug mode in production

### Phase 2 - Bug Fixes
1. Review all routes
2. Check session security
3. Check database consistency
4. Fix timer edge cases
5. Improve error handling

### Phase 3 - New Features
1. Study streak system
2. AI study planner
3. Flashcard generator
4. Better analytics
5. Student achievements
6. Improved leaderboard

## Progress So Far

### Completed
1. Moved `SECRET_KEY` and `TEACHER_SECRET` to environment-based config.
2. Added password hashing for student and teacher accounts.
3. Added backward-compatible password upgrade for older plaintext users on login.
4. Blocked duplicate usernames in student and teacher registration.
5. Improved registration UX so errors show inline on the same page.
6. Added secure file upload rules:
   - `secure_filename()`
   - only `pdf`, `docx`, `pptx`, `txt`
   - unique sanitized filenames
7. Fixed material authorization at the route level.
8. Added `teacher_id` ownership support for materials.
9. Added auto-migration for older databases missing `teacher_id`.
10. Created `requirements.txt`.
11. Improved `.gitignore` for `.env`, `users.db`, `uploads/`, `venv/`, `.DS_Store`.
12. Fixed `/materials` route to use the real `student_material.html` template.
13. Centralized debug-mode parsing with a helper.
14. Confirmed production stays safe when `FLASK_DEBUG` is not enabled.
15. Removed `users.db`, `uploads/`, and `.DS_Store` from Git tracking while keeping local files on disk.
16. Pushed the main hardening commit to GitHub:
    - `eaabdff` `Harden auth and material uploads`

### Phase 1 Status
- Phase 1 is functionally complete.
- There is still repo cleanup to commit if needed:
  - tracked-file removal for `users.db`, `uploads/`, `.DS_Store`
  - optional ignore decision for `graphify-out/obsidian/.obsidian/`

## Important Notes
- Keep changes small and safe.
- Do not rewrite the whole auth flow.
- Do not remove the backward-compatible password upgrade logic yet.
- Do not break student or teacher login.
- Keep the improved register-page UX unless intentionally improving it further.

## Testing Already Done
- `python3 -m py_compile app.py`
- `./venv/bin/python -m py_compile app.py`
- Verified new password storage is hashed
- Tested duplicate username flow
- Tested inline register errors
- Tested secure upload allow/block behavior
- Tested sanitized upload filenames
- Tested material authorization for same-class vs cross-class access
- Tested `teacher_id` migration behavior
- Verified `/materials` now points to the existing template
- Verified debug helper behavior
- Verified `users.db`, `uploads/`, and `.DS_Store` are no longer tracked by `git ls-files`

## Current Repo State
- Main app/code hardening work is done.
- `PROJECT_PROGRESS.md` and `requirements.txt` are part of the work.
- `users.db`, `uploads/`, and `.DS_Store` are removed from Git tracking but may still appear as deletions until committed.
- `graphify-out/obsidian/.obsidian/` is local untracked output.

## Next Step
Start Phase 2.

Recommended first move:
1. Review all routes
2. Identify the highest-risk bugs
3. Fix them one by one with tests after each change

## Known Future Items
- Database still has no unique DB constraint on username
- Database still lacks stronger constraints / foreign keys
- Session cookie hardening still needs a later pass
- `google.generativeai` is deprecated and should later move to `google.genai`
