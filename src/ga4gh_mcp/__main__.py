"""Entry point: ga4gh-mcp [generate-key | (run server)]"""

from __future__ import annotations

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "generate-key":
        from ga4gh_mcp.auth.api_key import ApiKeyValidator

        raw_key, key_hash = ApiKeyValidator.generate_key()

        user = "new-user"
        desc = ""
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--user" and i + 1 < len(args):
                user = args[i + 1]
                i += 2
            elif args[i] == "--description" and i + 1 < len(args):
                desc = args[i + 1]
                i += 2
            else:
                i += 1

        print(f"API Key (save this — shown only once): {raw_key}")
        print(f"Key Hash: {key_hash}")
        print()
        print("Add to config/api-keys.yaml:")
        print(f'  - user_id: "{user}"')
        print(f'    key_hash: "{key_hash}"')
        if desc:
            print(f'    description: "{desc}"')
        return

    from ga4gh_mcp.server import main as server_main
    server_main()


if __name__ == "__main__":
    main()
