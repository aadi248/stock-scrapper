import pandas as pd
import os

# --- Configuration ---
STATIC_FILE = 'static_symbols.csv'
SYMBOL_COLUMN_NAME = 'Symbol' # This must match the header in your CSV file exactly

def get_static_company_symbols():
    """
    Loads the list of company symbols from a static local CSV file.
    This function will never attempt to connect to the internet.
    """
    
    # 1. Check if the local file exists
    if not os.path.exists(STATIC_FILE):
        print(f"Error: Static symbol file not found at: {STATIC_FILE}")
        print("Please ensure you have saved the cleaned symbol list as 'static_symbols.csv' in this directory.")
        return []

    # 2. Load the data using pandas
    try:
        # We assume the file is a standard CSV
        df = pd.read_csv(STATIC_FILE)
        
        # 3. Extract the symbols column
        if SYMBOL_COLUMN_NAME not in df.columns:
            print(f"Error: The CSV file does not contain a column named '{SYMBOL_COLUMN_NAME}'.")
            print("Please check your file and rename the symbol column.")
            return []
            
        companies = df[SYMBOL_COLUMN_NAME].tolist()
        
        print(f"-> Successfully loaded {len(companies)} symbols from the static file.")
        return companies
        
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return []

# --- Execution Example ---
if __name__ == '__main__':
    symbol_list = get_static_company_symbols()
    
    if symbol_list:
        print("\nFirst 5 symbols in the list:")
        print(symbol_list[:5])
    else:
        print("\nSymbol list is empty.")