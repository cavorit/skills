---
name: dc-feedback
description: >-
  Write up the lessons learned from the current DataCards pairing session,
  with enough context to act on them, and send the report to the DataCards
  team. Use when the user runs /dc-feedback or asks to send feedback about
  the datacards-pair skill or the DataCards platform after working on a
  project.
allowed-tools: Bash(bash **/scripts/send-feedback.sh *), Read, Write
---

# DataCards session feedback

Write a report about this session and send it to the DataCards team. The team
uses these reports to improve the `datacards-pair` skill and the platform.

The reader was not in the session and cannot ask you anything. They know
DataCards well, but not this project, not what the user asked for and not
what you tried. A point like "screenshots were unreliable" is useless to
them. A point is useful when they could reproduce the situation from it and
see what to change. Do not sort or rate the points; the team does that.

The harness reports the absolute path to this `SKILL.md`. Resolve
`scripts/send-feedback.sh` from its parent directory.

## 1. Go through the session

Go through the whole session from the start, not only the last part. If
earlier parts were summarized, use the summary and say in the report that
the early part comes from a summary.

Look for these moments:

- **The user corrected or rejected something.** What had you built or
  proposed, what did the user say, and what did they want instead?
- **You were wrong about DataCards.** What did you assume, where did the
  assumption come from (a passage in the skill, marimo knowledge, a guess),
  and what turned out to be true?
- **Something failed or hung.** The call, the exact message, what you tried,
  and what the cause was.
- **Something took much longer than it should have.** Where did the time go?
- **You worked around something.** What did not work as expected, and what
  did you do instead?
- **You could not do something** the task needed, or had to ask the user to
  do it by hand.
- **The skill helped.** A rule or passage that prevented a mistake is worth
  one line, so it is not removed later.

Report only what happened in this session. If nothing is worth reporting,
tell the user and send nothing.

## 2. Write the report

Write it in English as markdown to a file, in this shape:

```markdown
# DataCards session feedback

## Session

- Date: YYYY-MM-DD
- Skill version: <version from the plugin manifest, or "unknown">
- Agent: <agent and model>
- Task: <what the user asked for, in two or three sentences>
- Result: <what exists now: notebooks, decks, cards; finished, partly
  finished or abandoned>
- Size: <rough duration or number of turns, and how often the user had to
  correct the direction>

## What happened

<Five to ten sentences that tell the session in order: the starting state
of the project, the main steps, where it went off track and how it got
back. This is the frame the lessons below are read in.>

## Lessons

### <short title that states the point>

- **Situation:** what you were trying to do at that moment, and the state
  of the project.
- **What happened:** what you did and what came back. Quote the call and
  the error message exactly. For a correction, give the user's words.
- **Cause:** what it turned out to be. Mark it as *confirmed* (say how you
  confirmed it) or *assumed*.
- **Cost:** what it cost: turns, rework, a rejected result, a restart.
- **Resolution:** what you did in the end, or "unresolved".
- **Would have helped:** the sentence in the skill, the error text or the
  platform behavior that would have prevented it. If a passage of the
  skill led you there, name the file and quote the passage.

### <next lesson>
…

## What worked well

- <rule, passage or platform feature that helped, and where>

## Not verified

- <what you could not check in this session, and why>

## Remarks from the user

<only if the user adds something in step 3, in their words>
```

Rules for the content:

- Order the lessons by what they cost, the most expensive first.
- Write one lesson per cause. If the same cause showed up three times, write
  it once and say it happened three times.
- Every bullet must hold something specific to this session. Leave a bullet
  out if you have nothing concrete for it.
- Include a short code snippet or the relevant lines of an output where the
  reader needs them to reproduce the point. Keep it to what is needed.
- Say what you caused yourself. A mistake of yours that the skill could not
  have prevented is still worth reporting, marked as such.
- Leave out sections that would be empty.

Keep out of the report: tokens and credentials, the project URL, host names,
names and e-mail addresses of people, and the project's data or business
content. Describe the subject of the project in general terms ("a dashboard
for sensor time series"), and replace such details in quoted messages and
code with placeholders.

## 3. Confirm and send

Show the report to the user. Ask two things: whether they want to add or
change anything, and whether to send it. Put what they add under "Remarks
from the user" and show the report again if it changed. Send only after a
clear yes, and send exactly the text the user saw.

```bash
bash /absolute/path/to/dc-feedback/scripts/send-feedback.sh /path/to/report.md
```

Use `--dry-run` to print the request without sending. The script prints the
HTTP status. If sending fails, tell the user and leave the report file in
place so they can send it another way.
