# on-inspire

My working ideas and brain dumps live in `notes/` (gitignored, local only). Read them for context on intent and direction.

- Start with `notes/INDEX.md`. It lists every note by date with topic tags.
- Each note has YAML frontmatter (`title`, `date`, `time`, `topics`, `themes`, `related`, `status`).
- When saving a new note, name it `YYYY-MM-DD - Topic.md`, include that frontmatter, and add a row to the index.

## Knowledge base

Instagram Reel transcripts and the ideas, quotes, tools, and resources pulled from them live in `knowledge/` (gitignored, local only).

- Read `knowledge/README.md` for the pipeline (`inbox/` → `sources/reels/` → `atoms/` → `syntheses/`), the frontmatter schema, and the tag vocabulary.
- Use the templates in `knowledge/_templates/`. Add a row to `knowledge/INDEX.md` for each processed reel.
- When processing a transcript, split it into one atom per idea, link atoms and sources in both directions, and reuse existing tags before inventing new ones.
