import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# Paths
CSV_PATH = 'APPLE INC (01-06-2020 _ 05-05-2025).csv'
JSON_PATH = 'AAPL (1).json'
TEMPLATE_PATH = 'index_template.html'
OUTPUT_DIR = 'output'
IMG_NAME = 'stock.png'
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'index.html')
SP500_CSV_PATH = 'sp500.csv'



# Setup
def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


#  Plot 
def plot_stock():
    df = pd.read_csv(CSV_PATH, parse_dates=['Date'])
    df.sort_values('Date', inplace=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Close'], linewidth=1)
    plt.title("Apple Inc. Stock Price (2020-2025)")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.tight_layout()

    img_path = os.path.join(OUTPUT_DIR, IMG_NAME)
    plt.savefig(img_path)
    plt.close()
    print(f"Saved chart → {img_path}")
    return IMG_NAME


# Financials JSON 
def extract_financial_table():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lookup = {entry['id']: entry['d'] for entry in data}
    idx_range = range(6, 11)
    years = list(range(2019, 2024))

    def sliced(key):
        return [lookup[key][i] for i in idx_range]

    sales = sliced('SALES')
    cogs = sliced('COGS')
    r_and_d = sliced('R_AND_D')
    sga = sliced('SGA')
    taxes = sliced('TAX')
    int_inc = sliced('IS_INT_INC')
    int_exp = sliced('IS_INT_EXPENSE')
    other = sliced('OTHER_NON_O')

    gross_margin = [s - c for s, c in zip(sales, cogs)]
    operating_income = [gm - r - s for gm, r, s in zip(gross_margin, r_and_d, sga)]
    other_income = [ii + o + ie for ii, o, ie in zip(int_inc, other, int_exp)]
    income_before_tax = [op + oi for op, oi in zip(operating_income, other_income)]
    net_income = [ibt - t for ibt, t in zip(income_before_tax, taxes)]

    rows = [
        ("Revenue", sales),
        ("Cost of Goods Sold", cogs),
        ("Gross Margin", gross_margin),
        ("R&D Expenses", r_and_d),
        ("SG&A Expenses", sga),
        ("Operating Income", operating_income),
        ("Other Income (net)", other_income),
        ("Income Before Tax", income_before_tax),
        ("Income Tax", taxes),
        ("Net Income", net_income)
    ]

    html = '<table>\n  <tr><th></th>' + ''.join(f'<th>{y}</th>' for y in years) + '</tr>\n'
    for name, values in rows:
        html += f'  <tr><td>{name}</td>' + ''.join(f'<td>{v:,}</td>' for v in values) + '</tr>\n'
    html += '</table>'
    return html


# Stock Metrics 
def calculate_stock_metrics(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['Date'])
    df.sort_values('Date', inplace=True)
    df = df.dropna(subset=['Close'])

    start_date = df['Date'].min()
    end_date = df['Date'].max()

    price_start = df.loc[df['Date'] == start_date, 'Close'].values[0]
    price_end = df.loc[df['Date'] == end_date, 'Close'].values[0]

    num_years = (end_date - start_date).days / 365.25
    cagr = (price_end / price_start) ** (1 / num_years) - 1

    current_year = pd.Timestamp.now().year
    jan_first = pd.Timestamp(f"{current_year}-01-01")
    df_ytd = df[df['Date'] >= jan_first]
    if not df_ytd.empty:
        price_ytd_start = df_ytd.iloc[0]['Close']
        ytd_change = (price_end - price_ytd_start) / price_ytd_start
    else:
        ytd_change = None

    # Beta daily data
    beta = calculate_beta('APPLE INC.csv', 'sp500.csv')

    return {
        "CAGR": cagr,
        "YTD": ytd_change,
        "Beta": f"{beta:.2f}"
    }



def calculate_beta(stock_csv, benchmark_csv):
    # Read Apple
    stock_df = pd.read_csv(stock_csv, parse_dates=['Date'], 
                           date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%Y'))
    stock_df['Close'] = stock_df['Close/Last'].replace('[\$,]', '', regex=True).astype(float)
    stock_df = stock_df[['Date', 'Close']].rename(columns={'Close': 'Stock'})

    # Read S&P 500
    bench_df = pd.read_csv(benchmark_csv, parse_dates=['Date'], 
                           date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%Y'))
    bench_df['Close'] = bench_df['Close/Last'].replace('[\$,]', '', regex=True).astype(float)
    bench_df = bench_df[['Date', 'Close']].rename(columns={'Close': 'Benchmark'})

    # Merge date
    df = pd.merge(stock_df, bench_df, on='Date', how='inner')
    df['Stock_Return'] = df['Stock'].pct_change()
    df['Benchmark_Return'] = df['Benchmark'].pct_change()
    df.dropna(inplace=True)

    # Beta calculation
    cov_matrix = df[['Stock_Return', 'Benchmark_Return']].cov()
    beta = cov_matrix.loc['Stock_Return', 'Benchmark_Return'] / cov_matrix.loc['Benchmark_Return', 'Benchmark_Return']

    return beta




# HTML
def build_html(img_filename):
    financial_table = extract_financial_table()
    metrics = calculate_stock_metrics(CSV_PATH)

    cagr_str = f"{metrics['CAGR']:.2%}"
    ytd_str = f"{metrics['YTD']:.2%}" if metrics['YTD'] is not None else "N/A"
    beta_str = metrics['Beta']

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        html = html.replace('{{STOCK_IMG}}', img_filename)
        html = html.replace('{{FINANCIAL_TABLE}}', financial_table)
        html = html.replace('{{CAGR}}', cagr_str)
        html = html.replace('{{YTD}}', ytd_str)
        html = html.replace('{{BETA}}', beta_str)

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated page → {OUTPUT_HTML}")


# Main
def main():
    ensure_output_dir()
    img_file = plot_stock()
    build_html(img_file)

if __name__ == '__main__':
    main()

