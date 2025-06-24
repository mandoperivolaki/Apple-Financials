import pandas as pd

import matplotlib.pyplot as plt
import os
CSV_PATH      = '"C:\Users\Me\Documents\APPLE INC (01-06-2020 _ 05-05-2025).csv"'
TEMPLATE_PATH = 'index_template.html'
OUTPUT_DIR    = 'output'
IMG_NAME      = 'stock.png'
OUTPUT_HTML   = os.path.join(OUTPUT_DIR, 'index.html')

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_stock():
    # 1) Read CSV
    df = pd.read_csv(CSV_PATH, parse_dates=['Date'])
    df.sort_values('Date', inplace=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Close'], linewidth=1)
    plt.title("Apple Weekly Closing Price (2020–Present)")
    plt.xlabel("Date")
    plt.ylabel("Close Price (USD)")
    plt.tight_layout()

    img_path = os.path.join(OUTPUT_DIR, IMG_NAME)
    plt.savefig(img_path)
    plt.close()
    print(f"Saved chart → {img_path}")
    return IMG_NAME

def build_html(img_filename):
    # 4) Read your HTML template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        html = html.replace('{{STOCK_IMG}}', img_filename)

        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        
            f.write(html)
    print(f"Generated page → {OUTPUT_HTML}")

def main():
    ensure_output_dir()
    img_file = plot_stock()
    build_html(img_file)

if __name__ == '__main__':
    main()
