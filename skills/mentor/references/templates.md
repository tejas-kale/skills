# State file formats

Create a file the first time it is needed. In `log.md`, `ledger.md`, `gate.md` and `rule-requests.md` the newest entry goes last. Text in `<angle brackets>` is a placeholder to replace.

## `charter.md`

```markdown
# Charter

Intake: <date>. Timezone: <IANA zone>. Rules review (week 6): <intake + 42 days>.

## Slots

| Slot | Occupant | Since | Goal |
|---|---|---|---|
| Work focus | <what> | <date> | <the goal, in the user's words> |
| Deep personal project | <what> | <date> | <goal> |
| Learning track | <what> | <date> | <goal> |

## Floors

| Floor | Number | Goal |
|---|---|---|
| Sleep | in bed by <HH:MM>, up at <HH:MM> | <goal> |
| Exercise | <n> sessions a week | <goal> |
| Unaided thinking | <n> sessions of <m> minutes a week | <goal> |

## Bet

- **Bet:** <the direction being tested>
- **Deliverable:** <small and concrete>
- **Started:** <date>. **Review date:** <date>.
- **Goal:** <what the bet is meant to find out>

## Rituals

- **Daily lines:** <HH:MM>, on paper. The three lines: <what the user chose to write>.
- **Weekly review:** <weekday> <HH:MM>, 20 minutes.
```

## `log.md`

Targets come from the charter. A row without a target in the charter gets `-`.

```markdown
## Week <Monday> to <Sunday> (review <date>, <HH:MM> to <HH:MM>)

| Measure | Source | Target | Actual |
|---|---|---|---|
| Nights in bed by bedtime | self-report | 7 | <n> |
| Exercise sessions | self-report | <floor> | <n> |
| Unaided thinking sessions | self-report | <floor> | <n> |
| Daily lines written | self-report | 7 | <n> |
| Learning-track sessions | self-report | <target or -> | <n> |
| Days with prompts past bedtime | script | 0 | <n> |
| Projects touched | script | <target or -> | <n> |
| Max parallel sessions | script | <target or -> | <n> |

- **Last week's commitment:** <kept, missed or overridden>. <one line>
- **Paper notes:** <three lines at most>
- **Problem:** `<tag from the index>`, <proposed by the mentor, or chosen by the user over the mentor's `<tag>`>
- **Advice:** <practice name> (<book, chapter>)
- **Commitment for the week:** <wording>. **Goal:** <the goal behind it>.
- **Parked:** <n> items
```

## `ledger.md`

`Kind` is `override` or `spike`. For an override, `About` names the commitment exactly as the charter or the log words it, so that overrides on one commitment can be counted.

```markdown
| Date | Kind | About | Note |
|---|---|---|---|
| <date> | override | <commitment> | User's reason: <one line>. Mentor's position: <one line>. |
| <date> | spike | <topic> | <HH:MM> to <HH:MM> |
```

## `gate.md`

`Outcome` is `waiting`, `switched <date>` or `withdrawn <date>`.

```markdown
## <date>: <slot>: <old occupant> -> <new occupant>

- **Why the old one stalled:** <the user's words>
- **Its next concrete step would have been:** <one step>
- **What the new one replaces:** <the trade>
- **Earliest switch:** <memo date + 7 days>
- **Outcome:** <outcome>
```

## `parked.md`

```markdown
- <date>: <idea or topic, one line>
```

## `rule-requests.md`

`Kind` is `rule` (waits for week 6) or `broken` (fix now).

```markdown
| Date | Request | Kind | Outcome |
|---|---|---|---|
| <date> | <the change the user wants in how the mentor works> | rule | <waiting, or the week-6 decision> |
| <date> | <what the mentor did against its skill, or what in the skill failed> | broken | <the edit needed in the skill> |
```
