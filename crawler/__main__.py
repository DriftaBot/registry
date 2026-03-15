"""
Entrypoint: python -m crawler

- With ANTHROPIC_API_KEY set: runs the full LangGraph ReAct agent (Claude-powered,
  can discover new specs beyond what's in companies.yaml).
- Without ANTHROPIC_API_KEY: runs a deterministic loop over companies.yaml
  with no LLM dependency and zero API cost.
"""
import os
import sys


def main() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY detected — running LangGraph agent.")
        from crawler.agent import build_agent

        agent = build_agent()
        final_state = agent.invoke({
            "messages": [(
                "user",
                "Please crawl all companies defined in companies.yaml and update any specs "
                "that have changed. Print a summary at the end showing how many specs were "
                "updated, unchanged, and errored.",
            )]
        })
        for msg in reversed(final_state["messages"]):
            if hasattr(msg, "content") and msg.type == "ai" and msg.content:
                print("\n" + "=" * 60)
                print(msg.content)
                print("=" * 60)
                break
    else:
        print("No ANTHROPIC_API_KEY — running deterministic crawler.")
        from crawler.runner import run
        run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCrawler interrupted.")
        sys.exit(1)
