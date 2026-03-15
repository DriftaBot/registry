# DriftaBot Specs

The central, always-up-to-date repository for public API specifications from major companies.

Specs are automatically fetched every 6 hours from their canonical public GitHub repositories by a [LangGraph](https://github.com/langchain-ai/langgraph)-powered crawler agent running in GitHub Actions. When breaking changes are detected, affected consumer repositories are automatically notified via GitHub issues.

## Spec Directory

```
companies/
└── providers/
    ├── stripe/openapi/         OpenAPI 3.0
    ├── twilio/openapi/         OpenAPI 3.0 (all service specs)
    ├── github/openapi/         OpenAPI 3.0/3.1
    ├── slack/openapi/          OpenAPI 2.0
    ├── sendgrid/openapi/       OpenAPI 3.0
    ├── digitalocean/openapi/   OpenAPI 3.0
    ├── netlify/openapi/        OpenAPI 2.0
    ├── pagerduty/openapi/      OpenAPI 3.0
    ├── shopify/graphql/        GraphQL SDL
    └── google/grpc/            gRPC / Protobuf
```

## File Naming

```
companies/providers/<company>/<spec_type>/<filename>.<spec_type>.<ext>
```

Examples:
- `companies/providers/stripe/openapi/stripe.openapi.json`
- `companies/providers/shopify/graphql/shopify_admin.graphql`
- `companies/providers/google/grpc/pubsub_v1/pubsub.proto`

## How It Works

### Crawler (every 6 hours)

1. [provider.companies.yaml](provider.companies.yaml) is the registry — it maps each company to the GitHub repo and file path(s) where their specs live.
2. A GitHub Actions [scheduled workflow](.github/workflows/crawl-specs.yml) runs every 6 hours.
3. At midnight UTC the workflow uses a LangGraph ReAct agent (Claude-powered). The other three runs use a fast deterministic crawler to save API costs.
4. The crawler fetches each spec, compares it with the stored version, and writes any updates.
5. Updated specs are committed and pushed back to this repo automatically.

### Consumer Notifier (on spec update)

1. After every commit that updates files under `companies/providers/`, the [notify-consumers workflow](.github/workflows/notify-consumers.yml) triggers automatically.
2. The [driftabot/engine](https://github.com/DriftaBot/engine) CLI compares old vs new specs to detect breaking changes.
3. GitHub Code Search finds public repositories that import the affected company's client libraries.
4. Repos registered in [consumer.companies.yaml](consumer.companies.yaml) are always notified (opt-in, no cap).
5. A GitHub issue is opened in each affected repo by the [@driftabot-agent](https://github.com/driftabot-agent) account.

## Adding a New API Provider

1. Find the company's public GitHub repo with their API spec.
2. Add an entry to [provider.companies.yaml](provider.companies.yaml):

```yaml
- name: acme
  display_name: Acme Corp
  specs:
    - type: openapi
      repo: acme/openapi
      path: spec/openapi.json
      output: companies/providers/acme/openapi/acme.openapi.json
  consumers:
    - query: "acme-sdk language:python"
    - query: "require(\"acme\") language:javascript"
```

3. Open a pull request — the next crawler run will pick it up automatically.

## Register Your Repo for Notifications

To receive breaking change notifications for any provider, open a PR adding your repo to [consumer.companies.yaml](consumer.companies.yaml):

```yaml
consumers:
  - repo: your-org/your-repo
    companies:
      - stripe
      - twilio
    contact: team@your-org.com   # optional
```

Registered repos are always notified — they bypass the dynamic search cap and are never false-positived out.

## Running Locally

```bash
# Install dependencies
pip install -e .

# Run the crawler (deterministic mode, no LLM cost)
GITHUB_TOKEN=ghp_xxx python -m crawler

# Run the crawler with the LangGraph agent
GITHUB_TOKEN=ghp_xxx ANTHROPIC_API_KEY=sk-ant-xxx python -m crawler

# Run the consumer notifier
GITHUB_TOKEN=ghp_xxx DRIFTABOT_TOKEN=ghp_yyy python -m notifier
```

## GitHub Policy Compliance

- All specs are fetched from **public** GitHub repositories only.
- The GitHub REST API is used (no HTML scraping), respecting GitHub's [Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies).
- Authenticated requests stay well within the 5,000 req/hr rate limit.
- This project is open source and non-commercial.

## Secrets Required

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions. Used to call the GitHub REST API and commit spec updates. |
| `ANTHROPIC_API_KEY` | Powers the LangGraph crawler agent (Claude). Only used once per day at midnight UTC. |
| `DRIFTABOT_TOKEN` | PAT for the [@driftabot-agent](https://github.com/driftabot-agent) GitHub account (`public_repo` scope). Used to create issues in consumer repos. |
