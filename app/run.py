"""CLI entry point for CSV Data-Analyst Agent."""
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="CSV Data-Analyst Agent")
    parser.add_argument("question", type=str, help="Natural language question")
    parser.add_argument("csv_path", type=str, help="Path to CSV file")
    return parser.parse_args()

def main():
    args = parse_args()
    from app.oracle import answer_question

    try:
        result = answer_question(args.question, args.csv_path)
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()