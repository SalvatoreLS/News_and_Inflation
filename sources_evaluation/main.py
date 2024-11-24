import os
from dotenv import load_dotenv

from tabulate import tabulate

from source_evaluator import SourceEvaluator


load_dotenv()


def main():

    pdf_path = os.getenv("PDF_PATH")
    api_key = os.getenv("GROQ_API_KEY")

    evaluator = SourceEvaluator(
            pdf_path=pdf_path,
            links=None,
            api_key_=api_key)

    result = evaluator.evaluate(
            scrape=True,
            scrapegraph=True,
            category=False,
            second_category=False)
    
    print(tabulate(result, headers='keys', tablefmt='psql'))

    result.to_csv("result.csv", index=False)

if __name__ == "__main__":
    main()
