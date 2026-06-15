import os
import pandas as pd
import gspread
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def get_all_google_sheets_data():
    """Connects to Google Sheets using the service account and extracts data from all tabs."""
    if not SERVICE_ACCOUNT_FILE or not GOOGLE_SHEET_ID:
        raise ValueError(
            "CRITICAL: Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_SHEET_ID in your .env file."
        )

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Could not find the JSON file at path: {SERVICE_ACCOUNT_FILE}"
        )

    print("Authenticating with Google Cloud via Service Account...")
    # Authenticate and open the spreadsheet
    client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    
    # Fetch all available worksheet tabs dynamically
    worksheets = spreadsheet.worksheets()
    print(f"Connected successfully. Found {len(worksheets)} sheet tabs in the workbook.\n")
    
    all_tabs_data = {}

    for ws in worksheets:
        tab_name = ws.title
        print(f"Pulling data from tab: '{tab_name}'...")
        
        # Extract rows from the current tab
        values = ws.get_all_values()
        
        if not values:
            print(f"⚠️ Tab '{tab_name}' is empty. Skipping.")
            continue
            
        # The first row contains the header names
        header = values[0]
        rows = values[1:]
        
        # Build DataFrame
        df = pd.DataFrame(rows, columns=header)
        df.dropna(how="all", inplace=True) # Clear completely blank rows
        
        all_tabs_data[tab_name] = df

    return all_tabs_data

def main():
    # Pandas display configurations for the terminal
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)

    try:
        # Scrape all tabs from the Google Sheet
        scraped_data = get_all_google_sheets_data()
        
        print("\n--- Scraping Summary ---")
        for tab_name, df in scraped_data.items():
            print(f"\n=========================================")
            print(f" TAB: {tab_name} ({len(df)} rows found)")
            print(f"=========================================")
            
            if not df.empty:
                print(df.to_string(index=False))
            else:
                print("[No Data]")
                
            # OPTIONAL: Un-comment the lines below if you want to save each tab to a local CSV file automatically
            # csv_filename = f"{tab_name.replace(' ', '_')}_scraped.csv"
            # df.to_csv(csv_filename, index=False)
            # print(f"💾 Saved to {csv_filename}")

    except Exception as exc:
        print(f"\nAn error occurred during execution: {exc}")

if __name__ == "__main__":
    main()