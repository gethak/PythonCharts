import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # For better date formatting
import os # For checking if file exists

def load_and_preprocess_data(filepath, date_column='Date', value_column_in_csv=None,
                             output_value_column_name=None, resample_freq=None,
                             date_format=None, multiply_value=None):
    """
    Loads data from a CSV file, processes the date column,
    optionally multiplies values, resamples, and renames the value column.

    Args:
        filepath (str): Path to the CSV file.
        date_column (str): Name of the column containing date information.
        value_column_in_csv (str): Name of the column containing the primary data/values in the input CSV.
        output_value_column_name (str): Desired name for the value column in the output DataFrame.
        resample_freq (str or None): Pandas resampling frequency string (e.g., 'ME' for month end).
                                     If None, no resampling is performed.
        date_format (str or None): The strftime format to parse the date (e.g., '%m/%d/%Y').
                                   If None, pandas will attempt to infer the format.
        multiply_value (float or None): A factor to multiply the value column by (e.g., for percentage conversion).

    Returns:
        pd.DataFrame or None: A processed DataFrame with a DatetimeIndex and a single value column,
                              or None if an error occurs.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return None

    try:
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        print(f"Error: File is empty at '{filepath}'")
        return None
    except Exception as e:
        print(f"Error reading CSV '{filepath}': {e}")
        return None

    if date_column not in df.columns:
        print(f"Error: Date column '{date_column}' not found in '{filepath}'")
        return None

    try:
        df[date_column] = pd.to_datetime(df[date_column], format=date_format)
    except ValueError as e:
        print(f"Error converting date column in '{filepath}': {e}")
        return None

    df.set_index(date_column, inplace=True)

    # Determine the column to work with for values
    if value_column_in_csv:
        if value_column_in_csv not in df.columns:
            print(f"Error: Value column '{value_column_in_csv}' not found in '{filepath}'")
            return None
        current_values_series = df[value_column_in_csv]
    else:
        # If not specified, assume it's the first (and ideally only) data column
        if len(df.columns) == 1:
            current_values_series = df.iloc[:, 0]
        else:
            print(f"Error: 'value_column_in_csv' must be specified for '{filepath}' "
                  "if it has multiple data columns or if the target column is not the only one.")
            return None
    
    # Ensure the series is numeric, coercing errors to NaN
    current_values_series = pd.to_numeric(current_values_series, errors='coerce')


    # Apply multiplication if specified
    if multiply_value is not None:
        current_values_series = current_values_series * multiply_value

    # Resample if specified
    if resample_freq:
        current_values_series = current_values_series.resample(resample_freq).mean()

    # Determine final output column name
    final_col_name = output_value_column_name if output_value_column_name else current_values_series.name
    if not final_col_name:
        final_col_name = "Value"

    return current_values_series.to_frame(name=final_col_name)

# --- Configuration ---
CPI_FILE = 'sa_cpi_monthly_yoy.csv'
USD_ZAR_FILE = 'USD_ZAR Historical Data.csv'
EUR_ZAR_FILE = 'EUR_ZAR Historical Data.csv'
PPI_FILE = 'sa_ppi_data.csv'
BRENT_OIL_FILE = 'brent_crude_oil_prices.csv'

START_DATE = '2015-01-01'
END_DATE = '2025-03-31' # Ensure this aligns with your data availability

# --- Load and Prepare Data ---
cpi_df = load_and_preprocess_data(
    filepath=CPI_FILE,
    value_column_in_csv='CPI_YOY_Change',
    output_value_column_name='CPI_YOY_Change',
    resample_freq=None,
    multiply_value=100
)

usd_zar_monthly = load_and_preprocess_data(
    filepath=USD_ZAR_FILE,
    value_column_in_csv='Price',
    output_value_column_name='USD_ZAR',
    date_format='%m/%d/%Y',
    resample_freq='ME'
)

eur_zar_monthly = load_and_preprocess_data(
    filepath=EUR_ZAR_FILE,
    value_column_in_csv='Price',
    output_value_column_name='EUR_ZAR',
    date_format='%m/%d/%Y',
    resample_freq='ME'
)

ppi_df = load_and_preprocess_data(
    filepath=PPI_FILE,
    date_column='Data_Date',
    value_column_in_csv='Actual_Percent',
    output_value_column_name='PPI_Actual_Percent',
    resample_freq=None,
    date_format=None,
    multiply_value=None
)

brent_oil_df = load_and_preprocess_data(
    filepath=BRENT_OIL_FILE,
    date_column='Date',
    value_column_in_csv='Price_USD_per_Barrel',
    output_value_column_name='Brent_Oil_USD',
    resample_freq='ME', # Resample daily oil prices to monthly average
    date_format=None, # Pandas should infer YYYY-MM-DD
    multiply_value=None
)

# Exit if any essential DataFrame failed to load
if cpi_df is None or usd_zar_monthly is None or eur_zar_monthly is None or \
   ppi_df is None or brent_oil_df is None:
    print("One or more data files could not be loaded or processed. Exiting.")
    exit()

# --- Sort DataFrames by index to ensure they are monotonic (important for .loc slicing) ---
if cpi_df is not None: cpi_df.sort_index(inplace=True)
if usd_zar_monthly is not None: usd_zar_monthly.sort_index(inplace=True)
if eur_zar_monthly is not None: eur_zar_monthly.sort_index(inplace=True)
if ppi_df is not None: ppi_df.sort_index(inplace=True)
if brent_oil_df is not None: brent_oil_df.sort_index(inplace=True)


# Filter data to the common time range
cpi_df_filtered = cpi_df.loc[START_DATE:END_DATE]
usd_zar_filtered = usd_zar_monthly.loc[START_DATE:END_DATE]
eur_zar_filtered = eur_zar_monthly.loc[START_DATE:END_DATE]
ppi_df_filtered = ppi_df.loc[START_DATE:END_DATE]
brent_oil_filtered = brent_oil_df.loc[START_DATE:END_DATE]


# --- Plotting ---
plt.style.use('seaborn-v0_8-darkgrid')

fig, ax1 = plt.subplots(figsize=(18, 9)) # Adjusted figure size for more data

# Plot Exchange Rates and Oil Price on the left y-axis
line1, = ax1.plot(usd_zar_filtered.index, usd_zar_filtered['USD_ZAR'], color='deepskyblue', linestyle='-', linewidth=2, label='USD/ZAR Exchange Rate')
line2, = ax1.plot(eur_zar_filtered.index, eur_zar_filtered['EUR_ZAR'], color='mediumseagreen', linestyle='--', linewidth=2, label='EUR/ZAR Exchange Rate')
line5, = ax1.plot(brent_oil_filtered.index, brent_oil_filtered['Brent_Oil_USD'], color='saddlebrown', linestyle=':', linewidth=2.5, label='Brent Crude Oil (USD/Barrel)') # New Brent Oil line

ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Exchange Rate / Oil Price (USD)', color='black', fontsize=12) # Updated label
ax1.tick_params(axis='y', labelcolor='black', labelsize=10)
ax1.tick_params(axis='x', labelsize=10, rotation=45)
ax1.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.YearLocator(1))
ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=range(1,13,3)))

# Create a second y-axis for CPI and PPI data
ax2 = ax1.twinx()
line3, = ax2.plot(cpi_df_filtered.index, cpi_df_filtered['CPI_YOY_Change'], color='salmon', linestyle=':', linewidth=2.5, label='SA CPI YoY Change (%)')
line4, = ax2.plot(ppi_df_filtered.index, ppi_df_filtered['PPI_Actual_Percent'], color='darkviolet', linestyle='-.', linewidth=2.5, label='SA PPI Actual Change (%)')

ax2.set_ylabel('Inflation / Producer Price Index Change (%)', color='black', fontsize=12)
ax2.tick_params(axis='y', labelcolor='black', labelsize=10)
ax2.grid(False)

# --- Title and Legend ---
plt.title('South African Economic Indicators: CPI, PPI, Oil & Key Exchange Rates (Jan 2015 - Mar 2025)', fontsize=16, pad=20)

handles = [line1, line2, line5, line3, line4] # Added line5 for Brent Oil, reordered for clarity
labels = [h.get_label() for h in handles]
# Adjust ncol and bbox_to_anchor if needed for 5 items
fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=10, frameon=True, bbox_transform=fig.transFigure)

fig.subplots_adjust(bottom=0.25) # Adjusted for potentially taller legend

# --- Save and Close Plot ---
output_filename = 'economic_indicators_plot_with_oil.png'
try:
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to '{output_filename}'")
except Exception as e:
    print(f"Error saving plot: {e}")
finally:
    plt.close(fig)

print("Script finished.")
