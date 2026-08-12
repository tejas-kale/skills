---
name: doom-literate-config
description: Change a Doom Emacs configuration — literate config.org setups, package declarations, keybindings, fonts, UI, and tool integrations.
---

# Doom Literate Config

In a literate setup `config.org` is the source and everything else is **tangled** — generated on export and overwritten. Every edit belongs in the source; an edit to a tangled file is lost at the next tangle.

## 1. Establish what tangles where

Read `init.el`, `config.org`, `config.el`, and `packages.el`.

- `:config literate` in `init.el` makes `config.org` the source.
- Ordinary `emacs-lisp` blocks tangle to `config.el`.
- Blocks marked `:tangle packages.el` tangle there; `package!` declarations need that marker.

Done when you can name the source file and the tangle destination of every block you intend to touch.

## 2. Account for the current configuration

Before the first edit, inventory every active setting in `config.el` and every `package!` declaration in `packages.el`, and confirm each one has a home in `config.org`.

Carry package-file comments into a `config.org` block tangled to `packages.el`, so they survive regeneration.

Done when every active setting, declaration, and comment in the tangled files is accounted for in the source — each one either preserved there or deliberately dropped.

## 3. Make the smallest Doom-native change

Reach for the Doom macro over raw Emacs Lisp:

| Task | Use |
|---|---|
| Declare an external package | `package!` (in the `packages.el` block) |
| Configure a package | `use-package!` |
| Bind keys | `map!` |
| Set the default font | `doom-font` |
| Set new-frame geometry | `default-frame-alist` |

Give each tool its own `config.org` section and code block, with its prerequisites in a block above its configuration.

Done when every changed line traces to a preference the user stated.
