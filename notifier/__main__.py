"""
Entrypoint: python -m notifier

- With ANTHROPIC_API_KEY set: runs the LangGraph ReAct agent.
- Without ANTHROPIC_API_KEY: runs the deterministic notifier runner.
"""
import os
import sys


def main() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY detected — running LangGraph notifier agent.")
        from notifier.agent import build_agent

        agent = build_agent()
        final_state = agent.invoke({
            "messages": [(
                "user",
                "Detect breaking API changes from the latest spec crawl and notify "
                "affected consumer repositories by creating GitHub issues. "
                "Print a summary at the end.",
            )]
        })
        for msg in reversed(final_state["messages"]):
            if hasattr(msg, "content") and msg.type == "ai" and msg.content:
                print("\n" + "=" * 60)
                print(msg.content)
                print("=" * 60)
                break
    else:
        print("No ANTHROPIC_API_KEY — running deterministic notifier.")
        from notifier.runner import run
        run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nNotifier interrupted.")
        sys.exit(1)
