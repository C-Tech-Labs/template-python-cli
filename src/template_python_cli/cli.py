import argparse


def main():
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Template Python CLI")
    parser.add_argument('--name', type=str, help='Your name', default='world')
    args = parser.parse_args()
    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
