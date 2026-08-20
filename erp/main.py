"""Repository-level helper for the VERP workspace."""


def main() -> None:
    """Print the available local service entrypoints."""

    print("VERP workspace")
    print("Start CRM API with: uv run python CRM/main.py")
    print("Or with uvicorn: uv run uvicorn CRM.main:app --reload")
    print("Central identity endpoints are mounted at: /api/v1/identity/users")
    print("Central identity permission endpoints are mounted at: /api/v1/identity/permissions")


if __name__ == "__main__":
    main()
