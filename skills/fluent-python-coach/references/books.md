# Books: index and extraction

Both PDFs live in `book/`: `fluent-python-2e.pdf` and `clean-code.pdf`. Every page number in `learning/book-index.md` is a **PDF page**: 1-based, counted from the first page of the file. The page number printed on the page is usually different (front matter shifts it), and `pdftotext -f/-l` takes PDF pages.

Run pypdf with `uv run --no-project --with pypdf python -`: `--no-project` keeps uv from syncing or relocking the agent's own environment. Write scratch output into a `mktemp -d` directory and delete it afterwards.

## Build the index

1. **Outline first.** Print each PDF's bookmarks with their PDF start pages:

   ```bash
   uv run --no-project --with pypdf python - book/fluent-python-2e.pdf <<'EOF'
   import sys
   from pypdf import PdfReader
   reader = PdfReader(sys.argv[1])
   print("pages", len(reader.pages))
   def walk(items, depth=0):
       for item in items:
           if isinstance(item, list):
               walk(item, depth + 1)
           else:
               print(depth, reader.get_destination_page_number(item) + 1, item.title)
   walk(reader.outline)
   EOF
   ```

   Find the depth at which the chapters sit (Fluent Python nests them under its five parts). A chapter ends on the page before the next entry at its depth or shallower; the last chapter ends where the next back-matter entry (appendix, index) starts. For Fluent Python, also record each chapter's sections: the entries one level below the chapter.
2. **Headings when there is no outline** (the walk prints nothing). Scan each page's opening lines for a chapter heading:

   ```bash
   uv run --no-project --with pypdf python - book/clean-code.pdf <<'EOF'
   import re, sys
   from pypdf import PdfReader
   for number, page in enumerate(PdfReader(sys.argv[1]).pages, start=1):
       head = "\n".join((page.extract_text() or "").splitlines()[:4])
       if match := re.search(r"chapter\s+(\d+)", head, re.IGNORECASE):
           print(number, match.group(1), head.replace("\n", " | "))
   EOF
   ```

   Keep the first hit per chapter number; running headers can repeat the word on later pages. Fluent Python's sections come from the same scan over a chapter's pages, looking for its section headings.
3. Write `learning/book-index.md` in the template from `templates.md`. Check it: 24 Fluent Python chapters and 17 Clean Code chapters, ranges ascending and not overlapping. If a range is uncertain, show the user the candidates and ask.

## Extract a chapter

Look up the range in `book-index.md`, then extract only those pages:

```bash
tmp=$(mktemp -d)
pdftotext -f 101 -l 140 -layout book/fluent-python-2e.pdf "$tmp/ch03.txt"   # if `command -v pdftotext` succeeds
```

Without `pdftotext`:

```bash
uv run --no-project --with pypdf python - book/fluent-python-2e.pdf 101 140 "$tmp/ch03.txt" <<'EOF'
import sys
from pypdf import PdfReader
path, first, last, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
pages = PdfReader(path).pages[first - 1:last]
with open(out, "w", encoding="utf-8") as f:
    f.write("\n\f".join(page.extract_text() or "" for page in pages))
EOF
```

Read the text file, in parts if it is long, and `rm -rf "$tmp"` when the spec or review is written. For Clean Code, extract only the chapters a review note cites.
