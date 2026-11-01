# KnowledgeHub: MVP Specification

**Status:** Draft v1 (Phase 0)
**Owner:** Black23pearl
**Source:** Personal Knowledge & Learning System Project Plan, with the changes listed under "Decisions".

---

## 1. Purpose

KnowledgeHub is a web app for capturing study notes, organizing them, finding them quickly, and (later) tracking retention and asking questions grounded in your own notes.

**Core principle:** do not just store information. Help the user retrieve, connect, and retain it.

**Primary user:** one learner (me) studying topics like DBMS, DSA, and interview prep. Multi-user support exists in the data model from day one, but sharing and collaboration are out of scope.

## 2. Decisions (changes from the original plan)

| # | Decision | Reason |
|---|----------|--------|
| D1 | **Categories are dropped.** Organization uses tags and note-to-note links only. | Categories appeared in the feature list but were never modeled. Tags cover the need. |
| D2 | **Auth comes early.** Start with a single hardcoded user behind a FastAPI dependency, with `user_id` on every owned table. Real login is added before any AI feature. | Retrofitting ownership checks onto finished endpoints is error-prone. |
| D3 | **Tests start in Phase 2**, with CI (GitHub Actions) added shortly after. | Testing alongside features, not at the end. |
| D4 | **Vertical slice first.** The first milestone is "create a note in the UI, it is saved in Postgres, and it shows after refresh", before polishing the frontend. | Surfaces integration problems early and avoids rebuilding a fake-data UI. |
| D5 | **PostgreSQL runs in Docker Compose from the start.** The app itself is not containerized until later. | Avoids local Postgres install problems. |
| D6 | **Markdown export is an early feature.** | Cheap, gives backups, and lets me import real study material for testing. |
| D7 | **Archive is reversible; delete is permanent and asks for confirmation.** | Clear, testable behavior. |
| D8 | **Tag filter rule: AND by default.** Selecting multiple tags returns notes that have all of them. | A single defined rule that tests can check. |
| D9 | **Archived notes are hidden** from lists and search by default, with a "show archived" toggle. | Matches the test in the plan ("archived-note visibility follows the product rules"). |

## 3. MVP scope

### In the MVP

- Create, view, edit, archive, and delete notes
- Markdown editing with a rendered preview
- Tags (create, assign multiple per note, rename, delete) and tag-based filtering
- Notes list with pagination
- PostgreSQL persistence through a FastAPI backend
- Clear loading, empty, and error states
- Basic automated tests (backend first)
- Markdown export of all notes

### Not in the MVP (deferred, in rough order)

1. Full-text search (Phase 4)
2. Note links, backlinks, related notes (Phase 5)
3. Revision scheduling and review history (Phase 6)
4. AI question answering and embeddings (Phase 7)
5. Real authentication UI (before Phase 7, per D2)
6. Knowledge graph visualization, saved filters, keyboard shortcuts, dashboard charts
7. Deployment (Phase 8)

Out of scope entirely: collaboration/sharing, microservices, Redis, a separate search engine, mobile apps.

## 4. User stories (MVP)

1. As a learner, I can create a note with a title and Markdown body, so I can capture what I'm studying.
2. I can edit a note and see when it was last updated.
3. I can view a note rendered as formatted Markdown.
4. I can add several tags to a note, so I can group notes by topic.
5. I can filter the notes list by one or more tags.
6. I can archive a note to hide it without losing it, and restore it later.
7. I can permanently delete a note after confirming.
8. I can rename or delete a tag, and the notes using it stay consistent.
9. I can export all my notes as Markdown files, as a backup.

## 5. Screens

| Screen | Contents |
|--------|----------|
| **Notes list** (home for the MVP) | Sidebar with tags, note cards (title, snippet, tags, updated date), "New note" button, tag filter, "show archived" toggle, pagination |
| **Note editor** | Title field, Markdown textarea with live preview, tag picker, Save and Cancel |
| **Note detail** | Rendered Markdown, tags, created/updated timestamps, Edit, Archive, Delete |
| **Tag management** | List of tags with note counts, rename, delete |
| **Empty and error states** | No notes yet, no results for this filter, API unreachable |

Later screens: search results, dashboard, review queue, AI assistant.

## 6. Data model (MVP tables)

| Table | Fields | Notes |
|-------|--------|-------|
| `users` | id, email, password_hash (nullable until real auth), created_at | One seeded user at first |
| `notes` | id, user_id, title, content, created_at, updated_at, archived_at | `archived_at IS NULL` means active |
| `tags` | id, user_id, name, color | Unique on `(user_id, name)` |
| `note_tags` | note_id, tag_id | Primary key `(note_id, tag_id)`, cascade on delete |

Planned for later phases (not created yet):

| Table | Phase | Purpose |
|-------|-------|---------|
| `note_links` | 5 | source_note_id, target_note_id, relationship_type. Unique on `(source, target, type)`, with a check that source is not equal to target, cascade on delete |
| `review_state` | 6 | One row per note: due_at, interval_days, ease. Makes "due today" cheap |
| `review_events` | 6 | History: note_id, reviewed_at, recall_rating. All timestamps in UTC |
| `note_chunks` | 4/7 | Heading-based passages of a note, used for search snippets, retrieval, and citations |

## 7. API (MVP)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/notes` | Create a note |
| GET | `/api/notes` | List notes (filters: `tags`, `archived`; pagination: `limit`, `offset`) |
| GET | `/api/notes/{id}` | Get one note |
| PATCH | `/api/notes/{id}` | Update title, content, tags |
| POST | `/api/notes/{id}/archive` | Archive |
| POST | `/api/notes/{id}/restore` | Restore |
| DELETE | `/api/notes/{id}` | Permanent delete |
| GET | `/api/tags` | List tags with note counts |
| PATCH | `/api/tags/{id}` | Rename or recolor |
| DELETE | `/api/tags/{id}` | Delete a tag (removes it from notes, never deletes notes) |
| GET | `/api/export` | Download all notes as Markdown |

**Conventions:** JSON in and out, correct status codes (201 on create, 404 when missing, 422 on validation errors), and one consistent error shape: `{"error": {"code": "...", "message": "..."}}`.

## 8. Acceptance criteria (definition of done for the MVP)

- [ ] Notes survive a page refresh and a server restart.
- [ ] Updating one note never changes another.
- [ ] Multi-tag filtering returns only notes that have all selected tags.
- [ ] Deleting a tag leaves its notes intact and removes only the association.
- [ ] Archived notes are hidden by default and reappear with the toggle.
- [ ] Empty title is rejected with a clear message; very long content is handled.
- [ ] Every screen has loading, empty, and error states.
- [ ] Backend tests pass in CI on every push.
- [ ] README explains how to set up and run the project from scratch.
- [ ] No secrets in the repo (`.env` is ignored, `.env.example` is committed).

## 9. Revised build order

| Step | Work | Outcome |
|------|------|---------|
| 0 | This spec, screen sketches, repo structure | Done when spec is approved |
| 1 | Docker Compose + Postgres, FastAPI skeleton, Alembic, `POST/GET /api/notes`, a minimal React page that calls them | End-to-end slice works |
| 2 | Full notes CRUD, validation, errors, pytest, hardcoded-user dependency | Persistent, tested notes API |
| 3 | Frontend foundation: layout, list, editor, detail, states | Usable notes UI on the real API |
| 4 | Tags: many-to-many, filtering, pagination, tag management | MVP organization features |
| 5 | Archive/restore, Markdown export, CI | **MVP complete** |
| 6+ | Search, links, revision, real auth, AI, deployment | Per original plan |

## 10. Open questions

- Which Markdown renderer to use in React (`react-markdown` is the likely default)?
- Should tag colors be free-form hex or chosen from a fixed palette?
- Page size for the notes list (start with 20)?
- Real auth approach later: session cookies or JWT?

## 11. Rules we are following

- MVP first, one major feature at a time, finish and test before moving on.
- No premature infrastructure.
- Build the non-AI version of everything before the AI version.
- Don't merge code I can't explain.
- Keep the repo demonstrable: README, screenshots, architecture notes, meaningful commits.
