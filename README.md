# DriftaBot Specs

The central, always-up-to-date repository for public API specifications from major companies.

Specs are automatically fetched every 6 hours from their canonical public GitHub repositories by a [LangGraph](https://github.com/langchain-ai/langgraph)-powered crawler agent running in GitHub Actions.

## Spec Directory

```
companies/
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
companies/<company>/<spec_type>/<filename>.<spec_type>.<ext>
```

Examples:
- `companies/stripe/openapi/stripe.openapi.json`
- `companies/shopify/graphql/shopify_admin.graphql`
- `companies/google/grpc/pubsub_v1/pubsub.proto`

## How It Works

1. [companies.yaml](companies.yaml) is the registry — it maps each company to the GitHub repo and file path(s) where their specs live.
2. A GitHub Actions [scheduled workflow](.github/workflows/crawl-specs.yml) runs every 6 hours.
3. The workflow runs `python -m crawler`, which invokes a LangGraph ReAct agent powered by Claude.
4. The agent fetches each spec, compares it with the stored version, and writes any updates.
5. Updated specs are committed and pushed back to this repo automatically.

## Adding a New Company

1. Find the company's public GitHub repo with their API spec.
2. Add an entry to [companies.yaml](companies.yaml):

```yaml
- name: acme
  display_name: Acme Corp
  specs:
    - type: openapi
      repo: acme/openapi
      path: spec/openapi.json
      output: companies/acme/openapi/acme.openapi.json
```

3. Open a pull request — the next crawler run will pick it up automatically.

## Running Locally

```bash
# Install dependencies
pip install -e .

# Set required env vars
export GITHUB_TOKEN=ghp_your_token_here
export ANTHROPIC_API_KEY=sk-ant-your_key_here

# Run the crawler
python -m crawler
```

## GitHub Policy Compliance

- All specs are fetched from **public** GitHub repositories only.
- The GitHub REST API is used (no HTML scraping), respecting GitHub's [Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies).
- Authenticated requests stay well within the 5,000 req/hr rate limit.
- This project is open source and non-commercial.

## Secrets Required

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions. Used to call the GitHub REST API. |
| `ANTHROPIC_API_KEY` | Required to run the Claude-powered LangGraph agent. Add this in repo Settings → Secrets. |
