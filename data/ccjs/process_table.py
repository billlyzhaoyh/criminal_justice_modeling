import pandas as pd
import os
from datetime import datetime

def sort_columns_chronologically(df):
    """
    Sort columns chronologically, keeping 'metric_name' as the first column.
    """
    # Get all columns except metric_id
    date_columns = [col for col in df.columns if col != 'metric_name']
    
    # Convert date strings to datetime objects for sorting
    def parse_date(date_str):
        # Handle quarterly format (e.g., "Apr - Jun 2015")
        if ' - ' in date_str:
            month, year = date_str.split(' - ')[1].split()
            # Convert month name to number
            month_to_num = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            return datetime(int(year), month_to_num[month], 1)
        return None
    
    # Sort columns based on dates
    sorted_columns = ['metric_name'] + sorted(date_columns, key=parse_date)
    
    # Reorder columns in the dataframe
    return df[sorted_columns]

def process_ccjs_data():
    """
    Process the CCJS data by:
    1. Filtering for All crime and National level data
    2. Removing unnecessary columns
    3. Splitting into quarterly and annual data
    4. Transforming both into wide format
    5. Sorting columns chronologically
    """
    try:
        # Get the most recent file in the raw directory
        raw_dir = "./data/ccjs/raw"
        files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        if not files:
            raise FileNotFoundError("No CSV files found in the raw directory")
        
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
        input_path = os.path.join(raw_dir, latest_file)
        
        # Read the CSV file
        df = pd.read_csv(input_path)
        
        # Apply filters
        filtered_df = df[
            (df['offence_type'] == 'All crime') & 
            (df['geographic_area_name'] == 'National')
        ]
        
        # Remove unnecessary columns
        columns_to_keep = ['stage', 'metric_name', 'date_granularity', 'time_period', 'value']
        filtered_df = filtered_df[columns_to_keep]
        
        # Split into quarterly and annual data
        quarterly_df = filtered_df[filtered_df['date_granularity'] == 'Quarterly'].copy()
        annual_df = filtered_df[filtered_df['date_granularity'] == 'Rolling annual'].copy()
        
        # Process quarterly data
        quarterly_wide = quarterly_df.pivot(
            index='metric_name',
            columns='time_period',
            values='value'
        ).reset_index()
        
        # Process annual data
        annual_wide = annual_df.pivot(
            index='metric_name',
            columns='time_period',
            values='value'
        ).reset_index()

        # Sort columns chronologically
        quarterly_wide = sort_columns_chronologically(quarterly_wide)
        annual_wide = sort_columns_chronologically(annual_wide)
        
        # Display information about the transformed data
        print(f"\nQuarterly Data Overview:")
        print(f"Shape: {quarterly_wide.shape}")
        print("\nColumns:")
        for col in quarterly_wide.columns:
            print(f"- {col}")
            
        print("\nAnnual Data Overview:")
        print(f"Shape: {annual_wide.shape}")
        print("\nColumns:")
        for col in annual_wide.columns:
            print(f"- {col}")
        
        # Save the transformed data
        output_dir = "./data/ccjs/processed"
        os.makedirs(output_dir, exist_ok=True)
        
        current_date = datetime.now().strftime("%B-%Y")
        
        # Save quarterly data
        quarterly_output = os.path.join(output_dir, f"ccjs_quarterly_{current_date}.csv")
        quarterly_wide.to_csv(quarterly_output, index=False)
        print(f"\nQuarterly data saved to: {quarterly_output}")
        
        # Save annual data
        annual_output = os.path.join(output_dir, f"ccjs_annual_{current_date}.csv")
        annual_wide.to_csv(annual_output, index=False)
        print(f"Annual data saved to: {annual_output}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_ccjs_data()
