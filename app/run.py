"""CLI entry point for CSV Data-Analyst Agent."""
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="CSV Data-Analyst Agent")
    parser.add_argument("question", type=str, help="Natural language question")
    parser.add_argument("csv_path", type=str, help="Path to CSV file")
    return parser.parse_args()

def main():
    args = parse_args()
    from app.agent import main as agent_main

    try:
        result = agent_main(args.question, args.csv_path)
        # Handle file outputs (e.g., charts)
        if isinstance(result, dict) and 'files' in result:
            for path in result['files']:
                if isinstance(path, str) and path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    print(f"![chart]({path})")
                else:
                    print(path)
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()