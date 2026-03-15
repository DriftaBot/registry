.PHONY: notify notify-agent

## notify: run the deterministic consumer notifier (no LLM, no API cost)
##
## Usage:
##   make notify
##
notify:
	GITHUB_TOKEN=$${GITHUB_TOKEN} DRIFTABOT_TOKEN=$${DRIFTABOT_TOKEN} python -m notifier

## notify-agent: run the LangGraph agent notifier (requires ANTHROPIC_API_KEY)
##
## Usage:
##   make notify-agent
##
notify-agent:
	GITHUB_TOKEN=$${GITHUB_TOKEN} DRIFTABOT_TOKEN=$${DRIFTABOT_TOKEN} ANTHROPIC_API_KEY=$${ANTHROPIC_API_KEY} python -m notifier
