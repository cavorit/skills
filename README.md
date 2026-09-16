<h1>
<p align="center">
  /datacards-pair
</h1>
<p align="center">
  DataCards projects as environments for agents
</p>
</p>

`datacards-pair` connects a coding agent to a running
[DataCards](https://datacards.app) project: it runs Python in the same marimo
kernels the user works in, inspects live notebook state, commits durable
notebook changes through marimo's code mode, and places cards on decks. It is
a fork of [marimo-pair](https://github.com/marimo-team/marimo-pair) extended
with the DataCards features (publish/consume graph, decks, cards, templates,
screenshots).

## Prerequisites

- A running DataCards project. In the cloud, open the project's
  "Pair with agent" dialog: it shows the project URL
  (`https://<host>/<team>/<project>/`) and a project token
  (`dc_sk_proj_...`); pass the token via the `MARIMO_TOKEN` env var.
  A local [marimo](https://marimo.io) notebook works too (`--no-token` for
  auto-discovery)
- `bash`, `curl`, and `jq` available on `PATH` (on Windows, run from
  Git Bash, or from WSL with those tools installed in the distro — the
  scripts also find notebooks running on the Windows host)

## Install

### Agent Skills (any tool)

Works with any agent that supports the [Agent Skills](https://agentskills.io)
open standard:

```bash
npx skills add cavorit/skills

# or upgrade an existing install
npx skills upgrade cavorit/skills
```

If you don't have `npx` installed but have `uv`:

```bash
uvx deno -A npm:skills add cavorit/skills
```

### Claude Code (plugin)

Add the marketplace and install the plugin:

```
/plugin marketplace add cavorit/skills
/plugin install datacards-skills@datacards-pair
```

To opt in to auto-updates (recommended), so you always get the latest version:

```
/plugin → Marketplaces → datacards-pair → Enable auto-update
```

## FAQ

### I keep getting prompted to allow Bash commands

The skill declares its own `allowed-tools`, but Claude Code may still prompt
you to approve each Bash call. To avoid repeated prompts, copy the absolute
paths to the scripts from the installed skill and add them to your
`.claude/settings.json` (project-level) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(bash /path/to/skills/datacards-pair/scripts/discover-servers.sh *)",
      "Bash(bash /path/to/skills/datacards-pair/scripts/execute-code.sh *)"
    ]
  }
}
```

### The agent connects to a remote URL. Is that expected?

Yes. The primary use case is a DataCards project running in the cloud, so
`execute-code.sh` sends the code to the project URL you give it, authenticated
with the project token. Only share a project token with an agent you trust to
run code in that project; tokens expire and are scoped to one project.
