# openclaw-driftabot

[OpenClaw](https://docs.openclaw.ai/) agent tool plugin for [DriftaBot Registry](https://driftabot.github.io/registry/) — query API spec drift and breaking change reports via natural language.

## What it does

DriftaBot Registry crawls API specs daily from 59+ providers (Stripe, GitHub, Twilio, Slack, Shopify, and more) and generates markdown drift reports when breaking changes are detected. This plugin exposes three structured tools so any OpenClaw agent can query the registry in real time.

| Tool | Description |
|------|-------------|
| `driftabot_list_providers` | List all tracked providers with spec types and GitHub repos |
| `driftabot_get_drift` | Get the latest breaking-change report for a provider |
| `driftabot_get_spec_info` | Get spec type, GitHub repo, and file path for a provider |

All tools fetch from `raw.githubusercontent.com/DriftaBot/registry/main` — no API key required.

## Install

```bash
cd ~/.openclaw/workspace/plugins
git clone https://github.com/DriftaBot/registry.git _driftabot
cp -r _driftabot/openclaw/plugins/driftabot-tool ./driftabot-tool
rm -rf _driftabot
cd driftabot-tool && npm install && npm run build
```

Or install via npm:

```bash
npm install -g openclaw-driftabot
```

## Configure

In your OpenClaw agent config, allowlist the tools:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "allow": ["driftabot_list_providers", "driftabot_get_drift", "driftabot_get_spec_info"]
        }
      }
    ]
  }
}
```

## Example queries

```
"What API providers are tracked in DriftaBot?"
"Did Stripe's API break anything recently?"
"Show me the latest drift report for GitHub's REST API"
"What spec type does Shopify use?"
"Which providers have openapi specs?"
```

## Links

- [DriftaBot Registry](https://github.com/DriftaBot/registry)
- [Documentation](https://driftabot.github.io/registry/)
- [OpenClaw Docs](https://docs.openclaw.ai/)
