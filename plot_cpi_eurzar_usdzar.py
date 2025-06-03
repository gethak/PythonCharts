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
        if len(df.columns) == 1:
            current_values_series = df.iloc[:, 0]
        else:
            print(f"Error: 'value_column_in_csv' must be specified for '{filepath}' "
                  "if it has multiple data columns or if the target column is not the only one.")
            return None
    
    current_values_series = pd.to_numeric(current_values_series, errors='coerce')

    if multiply_value is not None:
        current_values_series = current_values_series * multiply_value

    if resample_freq:
        current_values_series = current_values_series.resample(resample_freq).mean()

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
END_DATE = '2025-03-31'

# --- Load and Prepare Data ---
cpi_df = load_and_preprocess_data(
    filepath=CPI_FILE, value_column_in_csv='CPI_YOY_Change', output_value_column_name='CPI_YOY_Change',
    multiply_value=100
)
usd_zar_monthly = load_and_preprocess_data(
    filepath=USD_ZAR_FILE, value_column_in_csv='Price', output_value_column_name='USD_ZAR',
    date_format='%m/%d/%Y', resample_freq='ME'
)
eur_zar_monthly = load_and_preprocess_data(
    filepath=EUR_ZAR_FILE, value_column_in_csv='Price', output_value_column_name='EUR_ZAR',
    date_format='%m/%d/%Y', resample_freq='ME'
)
ppi_df = load_and_preprocess_data(
    filepath=PPI_FILE, date_column='Data_Date', value_column_in_csv='Actual_Percent',
    output_value_column_name='PPI_Actual_Percent'
)
brent_oil_df = load_and_preprocess_data(
    filepath=BRENT_OIL_FILE, date_column='Date', value_column_in_csv='Price_USD_per_Barrel',
    output_value_column_name='Brent_Oil_USD', resample_freq='ME'
)

if not all([df is not None for df in [cpi_df, usd_zar_monthly, eur_zar_monthly, ppi_df, brent_oil_df]]):
    print("One or more data files could not be loaded or processed. Exiting.")
    exit()

for df in [cpi_df, usd_zar_monthly, eur_zar_monthly, ppi_df, brent_oil_df]:
    df.sort_index(inplace=True)

cpi_df_filtered = cpi_df.loc[START_DATE:END_DATE]
usd_zar_filtered = usd_zar_monthly.loc[START_DATE:END_DATE]
eur_zar_filtered = eur_zar_monthly.loc[START_DATE:END_DATE]
ppi_df_filtered = ppi_df.loc[START_DATE:END_DATE]
brent_oil_filtered = brent_oil_df.loc[START_DATE:END_DATE]

# --- Plotting ---
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax1 = plt.subplots(figsize=(20, 10)) # Increased figure size

# Axis 1: USD/ZAR (Leftmost)
color_usd_zar = 'deepskyblue'
line1, = ax1.plot(usd_zar_filtered.index, usd_zar_filtered['USD_ZAR'], color=color_usd_zar, linestyle='-', linewidth=2, label='USD/ZAR Exchange Rate')
ax1.set_xlabel('Date', fontsize=14)
ax1.set_ylabel('USD/ZAR Rate', color=color_usd_zar, fontsize=14)
ax1.tick_params(axis='y', labelcolor=color_usd_zar, labelsize=12)
ax1.tick_params(axis='x', labelsize=12, rotation=45)
ax1.grid(True, which='major', linestyle=':', linewidth=0.5, alpha=0.7) # More subtle grid for primary

# Axis 2: EUR/ZAR (Right, offset 1)
ax_eur = ax1.twinx()
color_eur_zar = 'mediumseagreen'
line2, = ax_eur.plot(eur_zar_filtered.index, eur_zar_filtered['EUR_ZAR'], color=color_eur_zar, linestyle='--', linewidth=2, label='EUR/ZAR Exchange Rate')
ax_eur.set_ylabel('EUR/ZAR Rate', color=color_eur_zar, fontsize=14)
ax_eur.tick_params(axis='y', labelcolor=color_eur_zar, labelsize=12)
ax_eur.spines["right"].set_position(("outward", 0)) # Position at the default right
ax_eur.grid(False)

# Axis 3: Brent Crude Oil (Right, offset 2)
ax_oil = ax1.twinx()
color_brent = 'saddlebrown'
line5, = ax_oil.plot(brent_oil_filtered.index, brent_oil_filtered['Brent_Oil_USD'], color=color_brent, linestyle=':', linewidth=2.5, label='Brent Crude Oil (USD/Barrel)')
ax_oil.set_ylabel('Brent Oil (USD/Barrel)', color=color_brent, fontsize=14)
ax_oil.tick_params(axis='y', labelcolor=color_brent, labelsize=12)
ax_oil.spines["right"].set_position(("outward", 60)) # Offset further to the right
ax_oil.grid(False)

# Axis 4: CPI and PPI (Right, offset 3 - furthest)
ax_inflation = ax1.twinx()
color_cpi = 'salmon'
color_ppi = 'darkviolet'
line3, = ax_inflation.plot(cpi_df_filtered.index, cpi_df_filtered['CPI_YOY_Change'], color=color_cpi, linestyle=':', linewidth=2, alpha=0.8, label='SA CPI YoY Change (%)')
line4, = ax_inflation.plot(ppi_df_filtered.index, ppi_df_filtered['PPI_Actual_Percent'], color=color_ppi, linestyle='-.', linewidth=2, alpha=0.8, label='SA PPI Actual Change (%)')
ax_inflation.set_ylabel('Inflation/PPI Change (%)', color='black', fontsize=14) # General label
ax_inflation.tick_params(axis='y', labelcolor='black', labelsize=12)
ax_inflation.spines["right"].set_position(("outward", 120)) # Offset even further
ax_inflation.grid(False)


# X-axis formatting (apply to ax1 as it's the base)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.YearLocator(2)) # Major tick every 2 years for less clutter
ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1,7])) # Minor ticks for Jan, Jul

# --- Title and Legend ---
plt.title('South African Economic Indicators (Jan 2015 - Mar 2025)', fontsize=18, pad=25)

handles = [line1, line2, line5, line3, line4]
labels = [h.get_label() for h in handles]
fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=12, frameon=True, bbox_transform=fig.transFigure)

fig.subplots_adjust(left=0.08, right=0.75, bottom=0.25, top=0.9) # Adjust spacing

# --- Save and Close Plot ---
output_filename = 'economic_indicators_multi_axis_plot.png'
try:
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to '{output_filename}'")
except Exception as e:
    print(f"Error saving plot: {e}")
finally:
    plt.close(fig)

print("Script finished.")
