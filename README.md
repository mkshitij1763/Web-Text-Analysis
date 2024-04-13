**Text Analysis on URLs from Spreadsheet**

This Python script extracts text from URLs listed in an Excel spreadsheet, performs sentiment analysis, and calculates readability metrics. 

**Problem Statement**

The objective is to process a set of URLs provided in an Excel file ("input.xlsx"). For each URL:

1. **Extract Text:**  Fetch the webpage content and extract the article body, excluding headers, footers, and extraneous content.
2. **Clean Text:**  Remove stop words, punctuation, and other non-alphanumeric characters from the extracted text.
3. **Sentiment Analysis:**  Analyze the cleaned text to determine positive and negative sentiment scores. Additionally, calculate polarity (positive vs negative lean) and subjectivity (opinion vs fact) scores.
4. **Readability Analysis:**  Evaluate the readability of the text using various metrics like average sentence length, percentage of complex words, Fog Index, and more.

**Solution**

This script addresses the problem statement by following these steps:

1. **Data Loading and Preprocessing:**
   - Reads URLs and their IDs from "input.xlsx" using pandas.
   - Defines a function `load_stopwords` to load stop words from external text files.

2. **URL Loop and Text Processing:**
   - Iterates through each URL in the DataFrame.
   - Fetches the webpage content using `requests` and parses it with BeautifulSoup.
   - Extracts the text content using `.get_text()`.
   - Applies the `clean_text` function to remove stop words, punctuation, and non-alphanumeric characters.

3. **Text Analysis:**
   - Performs sentiment analysis using the `sentimental_analysis` function:
     - Calculates positive and negative scores based on predefined positive and negative word lists.
     - Determines polarity and subjectivity scores.
   - Performs readability analysis using the `readability_analysis` function:
     - Calculates various readability metrics like average sentence length, percentage of complex words, Fog Index, and more.

4. **Output Generation:**
   - Stores the analysis results (URL ID, URL, sentiment scores, readability metrics) in a list `output_data`.
   - Creates a Pandas DataFrame `output_df` from `output_data`.
   - Saves the DataFrame to a new Excel file "output.xlsx".

**Dependencies**

This script requires the following Python libraries:

- pandas
- requests
- beautifulsoup4
- nltk
- re

**Instructions**

1. Install the required libraries using `pip install pandas requests beautifulsoup4 nltk`.
2. Place the script (e.g., `text_analysis.py`) and the following files in the same directory:
   - Input Excel file: "input.xlsx"
   - Stop word lists (replace with your own if desired):
      - StopWords_Auditor.txt
      - StopWords_Currencies.txt
      - ... (other stop word list files)
   - Positive and negative word lists:
      - positive-words.txt
      - negative-words.txt
3. Run the script from the command line: `python text_analysis.py`

This will generate an output Excel file "output.xlsx" containing the processed data with sentiment scores and readability metrics for each URL.
