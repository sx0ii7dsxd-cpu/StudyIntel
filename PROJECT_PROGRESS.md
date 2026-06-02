# StudyIntel Handoff

## Read This First
If the user says:
- "go through PROJECT_PROGRESS.md"
- "continue StudyIntel work"
- "resume the production-ready work"

then use this file as the source of truth for what has already been done, what must not be broken, and what should be done next.

Do not restart planning from zero unless the codebase has changed significantly.

## Project
- Flask + SQLite study management platform
- Student login/register
- Teacher login/register
- Study timer
- Leaderboards
- Class chat
- Private messaging
- Study materials upload
- Gemini AI integration
- Analytics dashboard

## Main Goal
Make the project production-ready and GitHub-ready over time in small, safe steps without breaking the current project.

## How To Work On This Project
- Analyze the codebase before making changes
- Explain the issue before making large changes
- Make small incremental edits, not big rewrites
- Preserve existing behavior unless the task is specifically to change it
- Test each step after editing
- Prefer safe, reversible improvements
- Do not "clean everything up" in one go

## Original Priority Order

### Phase 1 - Security and stability
1. Replace hardcoded secrets with environment variables
2. Implement password hashing
3. Prevent duplicate usernames
4. Add secure file uploads
5. Fix authorization issues for materials
6. Create `requirements.txt`
7. Create/improve `.gitignore`
8. Disable debug mode in production

### Phase 2 - Bug fixes
1. Review all routes
2. Check session security
3. Check database consistency
4. Fix timer edge cases
5. Improve error handling

### Phase 3 - New features
1. Study streak system
2. AI study planner
3. Flashcard generator
4. Better analytics
5. Student achievements
6. Improved leaderboard

## Audit Findings Already Identified
- `SECRET_KEY` and `TEACHER_SECRET` were hardcoded in `app.py`
- Passwords were stored and checked in plaintext
- Duplicate usernames were allowed
- File uploads are currently unsafe
- Material edit/delete authorization is incomplete
- Debug mode was hardcoded on
- `.gitignore` is incomplete
- `student_materials.html` route/template mismatch exists
- Database schema is weak and missing stronger constraints
- Session hardening still needs a later pass
- `google.generativeai` is deprecated and should be migrated later

## Completed So Far

### Done 1. Environment-based secrets and runtime config
Completed:
- `app.secret_key` now reads from `SECRET_KEY`
- `TEACHER_SECRET` now reads from environment
- `FLASK_DEBUG` now controls debug mode
- App now raises a clear startup error if required secrets are missing
- Local `.env` was updated so current local behavior still works

Files changed:
- `app.py`
- `.env`

### Done 2. Password hashing with upgrade path
Completed:
- New student registrations store hashed passwords
- New teacher registrations store hashed passwords
- Student login verifies hashed passwords
- Teacher login verifies hashed passwords
- If an older account still has a plaintext password, successful login upgrades it immediately to a hash

Important helper names:
- `is_hashed_password`
- `login_password_matches`

Files changed:
- `app.py`

### Done 3. Duplicate username prevention
Completed:
- Student registration blocks an already used username
- Teacher registration blocks an already used username
- Username uniqueness is currently enforced at app level, not DB constraint level
- Usernames are blocked globally across student and teacher accounts

Files changed:
- `app.py`

### Done 4. Better registration error UX
Completed:
- Duplicate username no longer sends users to a blank plain-text page
- Student register shows inline error text on the same page
- Teacher register shows inline error text on the same page
- Previously entered form values stay filled after the error
- Invalid class code and invalid teacher secret code also return to the same form page

Files changed:
- `app.py`
- `templates/register.html`
- `templates/teacher_register.html`
- `static/style.css`

### Done 5. Secure file uploads
Completed:
- Uploads now use `secure_filename()`
- Allowed file types are restricted to `pdf`, `docx`, `pptx`, and `txt`
- Unsupported file types are rejected
- Uploaded filenames are sanitized and made unique
- Teacher dashboard now shows inline upload success/error messages

Files changed:
- `app.py`
- `templates/teacher_dashboard.html`
- `static/style.css`

### Done 6. Material authorization improvements
Completed:
- Route-level authorization now blocks cross-class edit/delete access
- `materials` now support explicit `teacher_id` ownership
- Existing databases are auto-migrated to add `teacher_id`
- Older materials with no `teacher_id` still fall back safely to class-based checks
- New uploads now store the uploading teacher's `teacher_id`

Files changed:
- `app.py`
- `create_db.py`

### Done 7. Requirements file
Completed:
- Added a minimal pinned `requirements.txt` based on real app dependencies in the virtualenv

Files changed:
- `requirements.txt`

### Done 8. `.gitignore` improvements
Completed:
- Added ignore rules for `.env`
- Added ignore rules for `users.db`
- Added ignore rules for `uploads/`
- Added ignore rules for `venv/`
- Added ignore rule for `.DS_Store`

Important note:
- Files already tracked by Git do not become untracked automatically just because they are now in `.gitignore`
- If needed later, tracked local/generated files can be removed from Git history/index carefully in a separate step

Files changed:
- `.gitignore`

## Testing Already Performed
- `python3 -m py_compile app.py`
- `./venv/bin/python -m py_compile app.py`
- Checked database record directly and confirmed new password storage uses hashed values like `scrypt:...`
- Tested duplicate username flow with Flask test client and temporary SQLite database
- Verified duplicate username now renders inline on the same registration page
- Tested secure upload allow/block behavior with Flask test client and temporary SQLite database
- Verified sanitized unique filenames are saved for uploads
- Verified route-level material authorization blocks cross-class edits/deletes
- Verified `teacher_id` migration and ownership behavior for old and new materials

## Database State
- `users.db` was deleted and recreated fresh from `create_db.py`
- Current database is a fresh database using the same schema from the script

## Current Repo Status
- `.gitignore`, `app.py`, `create_db.py`, `static/style.css`, `templates/register.html`, `templates/teacher_dashboard.html`, and `templates/teacher_register.html` have local changes from the production-readiness work
- `requirements.txt` and `PROJECT_PROGRESS.md` are new files
- `users.db` still shows as tracked in Git because it was already tracked before the `.gitignore` update
- `uploads/` still has tracked-file churn for the same reason and may need a careful untrack step later
- `graphify-out/obsidian/.obsidian/` is also showing as untracked local output

## Important Current Behavior To Preserve
- Do not break student login
- Do not break teacher login
- Do not remove the backward-compatible password upgrade logic yet
- Do not replace the whole auth flow with a rewrite
- Keep visual behavior of the improved register pages unless intentionally improving it
- Keep changes incremental

## Next Step To Do
The next recommended task is:

### Next: production safety pass and cleanup
Good next small options:
- verify debug stays off outside local development
- decide whether to untrack already tracked local/generated files like `users.db` and `uploads/`
- fix the `student_materials.html` vs `student_material.html` mismatch

## After That
Do these in order unless the user changes priorities:

1. Disable production debug usage fully
The code already moved to env-based debug config, but keep verifying production-safe behavior.

2. Decide whether to untrack already tracked local/generated files
Examples:
- `users.db`
- `uploads/`
- `.DS_Store`

## Known Follow-up Bugs / Risks
- Route renders `student_materials.html` but template file present is `student_material.html`
- Database has no unique constraint on username yet
- Database tables still lack stronger constraints and foreign keys
- Session cookie hardening still needs a later pass
- Gemini package deprecation needs future migration

## Instruction For Future Sessions
When resuming:
1. Read this file first
2. Confirm current repo state briefly
3. Continue from "Next Step To Do" unless the user asks for a different priority
4. Keep edits small and test after each step
