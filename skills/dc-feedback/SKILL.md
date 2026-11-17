---
name: dc-feedback
description: >-
  Write lessons learned from the current DataCards pairing session and send
  them, categorized, to the DataCards team. Use when the user runs
  /dc-feedback or asks to send feedback about the datacards-pair skill or
  the DataCards platform after working on a project.
allowed-tools: Bash(bash **/scripts/send-feedback.sh *), Read, Write
---

# DataCards session feedback

Turn what happened in this session into a short lessons-learned report and
send it to the DataCards team. The team uses these reports to improve the
`datacards-pair` skill and the platform.

The harness reports the absolute path to this `SKILL.md`. Resolve
`scripts/send-feedback.sh` from its parent directory.

## 1. Collect

Go through this session and note what is worth reporting:

- where the skill text was wrong, missing or misleading
- what the user had to correct or rejected, and why
- errors and dead ends, with the exact message and what the cause turned out
  to be
- workarounds you used
- what you could not do or could not verify

Only report what happened in this session. Separate what is proven from what
you assume, and say what you caused yourself. If nothing is worth reporting,
say so and send nothing.

## 2. Categorize

Give every point exactly one category:

| Category | Use it for |
|----------|------------|
| `RULE` | A product principle or mandatory work step the skill should state. Breaking it got work rejected. |
| `FIX` | Skill text that is wrong or contradicts the product. Name the file and the passage. |
| `REF` | General, lasting knowledge an agent needs at certain moments (API behavior, deck craft). |
| `TEMP` | A workaround for a platform weakness that should disappear once the platform is fixed. |
| `PLATFORM` | A bug or missing capability of the platform that the skill cannot solve. |
| `OUT` | Specific to this project's subject or a one-off pattern. Reported for completeness only. |

A point is `RULE`, `FIX` or `REF` only if it would apply to most projects
whatever their subject, and an agent could not have found it out itself from
`help(cm)`, `ctx.list_templates()` or an error message. Knowledge about one
domain, library or data source is `OUT`.

## 3. Write the report

Write it in English as markdown to a file, in this shape. One to three
sentences per point: what happened, what the consequence was, what would have
helped.

```markdown
# DataCards session feedback

- Date: YYYY-MM-DD
- Skill version: <version from the plugin manifest, or "unknown">
- Agent: <agent and model>
- Session: <one line: what was built, how many notebooks and decks>

## RULE
- **<short title>** <what happened, consequence, suggestion>

## FIX
- **<file>: <short title>** …

## REF
## TEMP
## PLATFORM
## OUT

## Not verified
- <what the agent could not check in this session>
```

Leave out empty sections.

Keep out of the report: tokens and credentials, the project URL, names and
e-mail addresses of people, and the project's data or business content.
Describe the project's subject in general terms only.

## 4. Confirm and send

Show the report to the user and ask whether to send it. Send only after a
clear yes, and send exactly the text the user saw.

```bash
bash /absolute/path/to/dc-feedback/scripts/send-feedback.sh /path/to/report.md
```

Use `--dry-run` to print the request without sending. The script prints the
HTTP status. If sending fails, tell the user and leave the report file in
place so they can send it another way.
