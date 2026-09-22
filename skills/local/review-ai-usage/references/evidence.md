# Evidence rules

## Meaningful work

Include a conversation when the agent materially changed an artefact, decision,
or understanding. Skip greetings, quick lookups, and disposable wording edits.
List skipped sessions compactly so the user can challenge the filter.

## Division of work

Record separately:

- **Agent did:** actions visible in assistant messages and tool events.
- **User did:** actions explicitly stated or visible in user messages.
- **Requires confirmation:** likely human work that is not visible in evidence.

An inference never becomes an observed action.

## Interventions

Record an intervention when the user rejects an output, changes the approach,
restores a missed constraint, identifies an error, changes scope, or supplies
judgement the agent could not provide. Give its timestamp and a concise
paraphrase. Use a short excerpt only when its wording matters.

Ordinary continuation prompts are not interventions.

## Lessons

A candidate lesson states a repeatable change in behaviour supported by a
specific incident. Confirm it only with the user. Record its evidence count and
supporting cases. Mark recurrence after three supporting incidents.

## Confidential work

Excluded workspaces contribute no content. For included confidential work,
record the workflow shape and observable outcome. Omit names, source text,
internal URLs, secrets, and raw excerpts.
