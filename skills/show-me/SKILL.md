---
name: show-me
description: Explain the current topic with concise ASCII diagrams, code-shape sketches, and diffs printed in the console. Use when the user asks to see, show, sketch or diagram how something works or what a change looks like, or when a structure or flow is clearer drawn than described.
---

Help the user understand the current topic of conversation visually. Skip the preamble and keep prose brief. Pick the smallest view that makes the key point clear.

The output is read in a terminal or an Emacs terminal buffer. Print everything as text in fenced code blocks. Use plain ASCII only (no box-drawing characters, no emoji), keep lines under 80 columns, and never write files, open a browser, or produce HTML or Mermaid. Use the language and naming of the code under discussion; the examples below are only shapes.

- Show logic or an algorithm as pseudocode:

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

- Show runtime control flow as a call tree:

```text
submit_form
  create_session
    persist_prompt
    launch_agent
  navigate_to_session
```

- Show UI or object structure as an indented tree, with the state and module boundaries that matter, and file paths where they help:

```text
SessionPage (routes/session)
  state: events
  SessionToolbar
    RunSkillButton (shared/ui)
  SessionTimeline
```

- Show file responsibility or a broad refactor as a shallow file tree:

```text
src/
|-- commands/     # parses user actions
|-- sessions/     # owns session state
`-- transport/    # sends API requests
```

- Show component interaction, control flow, or data flow as an ASCII sequence diagram, one column per participant and one arrow per message:

```text
User            UI              Daemon
 |  choose cmd   |                |
 |-------------->|                |
 |               | expanded prompt|
 |               |--------------->|
 |               |  stream result |
 |               |<- - - - - - - -|
```

- Show relationships between a few parts as a box-and-arrow diagram, left to right or top to bottom. Use `-->` for calls or data, `- ->` for optional or async links:

```text
+--------+     +--------+     +-------+
| parser | --> | planner| --> | runner|
+--------+     +--------+     +-------+
                   |
                   v
               +-------+
               | cache |
               +-------+
```

- Show state changes as a table or a transition list:

```text
state      event         next
idle       submit        running
running    done          idle
running    cancel        idle
```

- Use `diff` when the point is what changes and the surrounding shape already exists. Match the diff shape to the topic.

For a structure change:

```diff
 SessionPage
   state: events
   SessionToolbar
+    RunSkillButton
   SessionTimeline
+    SkillResultCard
```

For a file-layout change:

```diff
 src/
 |-- commands/
+|   `-- show_me      # expands the slash command
 |-- sessions/
-`-- transport.py
+`-- transport/
+    |-- client.py
+    `-- stream.py
```

For a call-tree or call-stack change:

```diff
 submit_form
   create_session
     persist_prompt
+    expand_skill_mention
     launch_agent
-  navigate_to_session
+  navigate_to_session
+    subscribe_to_events
```

For a state or control-flow change:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

- Show the whole block when most of it is new, when omitted context would hide ownership or order, or when the user needs a copyable target shape. Use the project's own language and fence tag:

```python
def expand_skill(command: str) -> str:
    skill_name = command[1:]
    return f"use the {skill_name} skill"
```

- When a topic is too dense for one diagram, split it into two or three small ones, each with one line of text saying what it shows. Do not make an HTML page or any file for this.

### guidance

Place each visual next to the short text it supports. Keep only the calls, files, fields, states, and boundaries needed to answer the user's current question or the options to resolve the current discussion point.

You may use one of these, you may use several, it is unlikely you will use all of them. Use your judgement and don't overwhelm the user.
