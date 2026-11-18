# Adding a source

How a new book, article, talk or podcast transcript becomes part of the mentor's knowledge. The mentor advises from distillations only, never from the raw text, so a source counts once its distillation is in `references/` and the index points into it.

## Where each part lives

- **Raw source** (PDF, saved article, transcript): kept in the user's private files, never in this folder. This folder is in a public repo.
- **Distillation**: `references/<slug>.md`, at most about 10 KB. `<slug>` is the title in lower case with hyphens.
- **Pointers**: `references/index.md`.

## Steps

1. **Read the whole source.** Work from the text the user gives you, attached in this conversation. If only part of it is readable (a scanned PDF, a cut-off transcript), say which part and distil only that.
2. **Pick a key.** Two capital letters not yet in the index's key table.
3. **Write the distillation** in the format below.
4. **Update the index.** Add the key's row to the key table. For each problem in the index, add the practices that bear on it: under **Also**, or under **First** when one is stronger than a practice already there, keeping **First** at five. Where the new source takes a side in an entry of "Where the books disagree", add it to that side. Where it contradicts the others on a question not yet listed, add a new entry with its **Turns on** line.
5. **Hand over.**
   - In Claude Code: write both files under `skills/mentor/references/` in the skills repo and tell the user to commit and push them, then press **Sync now** in the Claude project.
   - In a Claude project: give the user the new file and the whole updated `index.md`, as files, and tell them to add both to `skills/mentor/references/` in the skills repo, push, and press **Sync now**.

**Done when:** the distillation follows the format, every practice in it is reachable from the index or deliberately left out, and the user has the next action for getting both files into the repo.

## Format

Same sections for every kind of source, so that Advise reads them all alike.

```markdown
# <Title> (<Author or host>, <year>)

Kind: <book | article | talk | podcast>. Source: <publisher, site or show; the URL for anything online>.

## Core argument

<One paragraph: the claim, the evidence offered for it, the remedy.>

## Sections

- <Chapter, heading or segment>, <p. N | hh:mm:ss | ¶ N>

## Practices

### 1. <Name of the practice, as an action>

- **Cite:** <section>, <p. N–M | hh:mm:ss | ¶ N>
- **Do:** <The action, with the source's numbers. A number the source gives as one person's example is written as an example.>
- **Why:** <The source's reason, one line.>
- **Limits:** <Only where the source names who or when it does not suit.>

## Positions

- **Saying no and narrowing versus exploring:** <stance, with cites>
- **Quitting versus finishing what was started:**
- **How tightly to schedule and plan time:**
- **Ambition, goals and how much to take on:**
- **Passion or interest as a guide to choosing work:**
- **Rest, leisure and limits on work:**
- **How to choose which skills or projects to pursue:**

## Terms

- **<Term>:** <definition> (<cite>)
```

## Rules for the content

- **Locators.** Books: chapter, with part or rule, and the PDF page. Articles: heading and paragraph number. Audio and video: segment and timestamp. Advise cites the section to the user; the fine locator lets the user check it.
- **Practices only from the source.** A practice is something the source tells the reader to do. Leave out anecdotes, studies and claims that come with no action.
- **Sizes.** A book: 8 to 12 practices. An article or episode: 1 to 5. A source with no practice gets no file: tell the user so.
- **Positions.** Leave a line out where the source says nothing on it. Do not infer a stance.
- **Plain words.** No quotation longer than a short phrase. The distillation restates; it does not reproduce.
