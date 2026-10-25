# Books: index and extraction

Both PDFs live in `book/`: `total-typescript.pdf` and `clean-code.pdf`. Every page number in `learning/book-index.md` is a **PDF page**: 1-based, counted from the first page of the file. The page number printed on the page is usually different (front matter shifts it), and `pdftotext -f/-l` takes PDF pages.

*Exploring JavaScript* is not a PDF here: it is looked up on the web ([`js-diagnostic.md`](js-diagnostic.md)).

## Tools

Outlines need pypdf; page text uses `pdftotext` when `command -v pdftotext` succeeds, else pypdf. Write scratch output into `tmp=$(mktemp -d)` and `rm -rf "$tmp"` afterwards. Pick the Python that has pypdf, in the same command as the script that uses it (shell variables do not carry over):

```bash
if command -v uv >/dev/null; then
  PY="uv run --no-project --with pypdf python"   # --no-project leaves any project environment alone
else
  python3 -m venv "$tmp/venv" && "$tmp/venv/bin/pip" install -q pypdf && PY="$tmp/venv/bin/python"
fi
```

## Build the index

1. **Outline first.** Print each PDF's bookmarks with their PDF start pages:

   ```bash
   $PY - book/total-typescript.pdf <<'EOF'
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

   Find the depth at which the chapters sit (Total TypeScript may nest them under its six parts). A chapter ends on the page before the next entry at its depth or shallower; the last chapter ends where the next back-matter entry (afterword, index) starts. For Total TypeScript, also record each chapter's sections: the entries one level below the chapter.
2. **Headings when there is no outline** (the walk prints nothing). Scan each page's opening lines for a chapter heading:

   ```bash
   $PY - book/clean-code.pdf <<'EOF'
   import re, sys
   from pypdf import PdfReader
   for number, page in enumerate(PdfReader(sys.argv[1]).pages, start=1):
       head = "\n".join((page.extract_text() or "").splitlines()[:4])
       if match := re.search(r"chapter\s+(\d+)", head, re.IGNORECASE):
           print(number, match.group(1), head.replace("\n", " | "))
   EOF
   ```

   Keep the first hit per chapter number; running headers can repeat the word on later pages. When a book's headings carry no "Chapter" word, match the chapter titles from `plan-backlog.md` (Total TypeScript) or the rubric's Clean Code table instead. Total TypeScript's sections come from the same scan over a chapter's pages, looking for its section headings.
3. Write `learning/book-index.md` in the template from `templates.md`. Check it: 16 Total TypeScript chapters and 17 Clean Code chapters, ranges ascending and not overlapping. If a range is uncertain, show the user the candidates and ask.

## Extract a chapter

Look up the range in `book-index.md`, then extract only those pages:

```bash
pdftotext -f 101 -l 140 -layout book/total-typescript.pdf "$tmp/ch05.txt"   # if `command -v pdftotext` succeeds
```

Without `pdftotext`:

```bash
$PY - book/total-typescript.pdf 101 140 "$tmp/ch05.txt" <<'EOF'
import sys
from pypdf import PdfReader
path, first, last, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
pages = PdfReader(path).pages[first - 1:last]
with open(out, "w", encoding="utf-8") as f:
    f.write("\n\f".join(page.extract_text() or "" for page in pages))
EOF
```

Read the text file, in parts if it is long, and `rm -rf "$tmp"` when the spec or review is written. For Clean Code, extract only the chapters a review note cites.
