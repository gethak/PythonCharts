import pandas as pd
import matplotlib.pyplot as plt

# Load the CPI data
cpi_df = pd.read_csv('sa_cpi_monthly_yoy.csv')
cpi_df['Date'] = pd.to_datetime(cpi_df['Date'])
cpi_df.set_index('Date', inplace=True)

# Convert CPI YoY change to percentage for plotting
cpi_df['CPI_YOY_Change'] = cpi_df['CPI_YOY_Change'] * 100  # e.g., 0.044 to 4.4%

# Load the USD/ZAR data
usd_zar_df = pd.read_csv('USD_ZAR Historical Data.csv')
usd_zar_df['Date'] = pd.to_datetime(usd_zar_df['Date'], format='%m/%d/%Y')
usd_zar_df.set_index('Date', inplace=True)

# Convert USD/ZAR to ZAR/USD (reciprocal)
usd_zar_df['ZAR_USD'] = 1 / usd_zar_df['Price']

# Resample ZAR/USD to monthly averages
zar_usd_monthly = usd_zar_df['ZAR_USD'].resample('ME').mean().to_frame()

# Load the EUR/ZAR data
eur_zar_df = pd.read_csv('EUR_ZAR Historical Data.csv')
eur_zar_df['Date'] = pd.to_datetime(eur_zar_df['Date'], format='%m/%d/%Y')
eur_zar_df.set_index('Date', inplace=True)

# Convert EUR/ZAR to ZAR/EUR (reciprocal)
eur_zar_df['ZAR_EUR'] = 1 / eur_zar_df['Price']

# Resample ZAR/EUR to monthly averages
zar_eur_monthly = eur_zar_df['ZAR_EUR'].resample('ME').mean().to_frame()

# Filter data to the common time range (Jan 2015 to Mar 2025)
start_date = '2015-01-01'
end_date = '2025-03-31'
cpi_df = cpi_df[start_date:end_date]
zar_usd_monthly = zar_usd_monthly[start_date:end_date]
zar_eur_monthly = zar_eur_monthly[start_date:end_date]

# Create a dual-axis plot
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot ZAR/USD on the left y-axis
ax1.plot(zar_usd_monthly.index, zar_usd_monthly['ZAR_USD'], color='blue', label='ZAR/USD Exchange Rate')
# Plot ZAR/EUR on the left y-axis
ax1.plot(zar_eur_monthly.index, zar_eur_monthly['ZAR_EUR'], color='green', label='ZAR/EUR Exchange Rate')
ax1.set_xlabel('Date')
ax1.set_ylabel('Exchange Rate (ZAR/USD, ZAR/EUR)', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(True)

# Create a second y-axis for CPI
ax2 = ax1.twinx()
ax2.plot(cpi_df.index, cpi_df['CPI_YOY_Change'], color='red', label='CPI YoY Change (%)')
ax2.set_ylabel('CPI YoY Change (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Title and legend
plt.title('South African CPI YoY Change, ZAR/USD, and ZAR/EUR Exchange Rates (Jan 2015 - Mar 2025)')
fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, bbox_transform=fig.transFigure)

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot to a file
plt.savefig('cpi_zarusd_zareur_plot.png')
# Close the plot to free memory
plt.close()