import pandas as pd
import yfinance as yf
import os
from tqdm import tqdm
import sys

# このスクリプトは定期的に（例: 1日に1回）実行することを想定しています。
# 全上場銘柄のデータをyfinanceから取得し、高速なParquet形式で保存します。

# --- 定数定義 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TICKER_LIST_FILE_PATH = os.path.join(BASE_DIR, 'tosho_list.xlsx')
OUTPUT_PARQUET_PATH = os.path.join(BASE_DIR, 'all_stock_data.parquet')

# --- データ取得関数群 ---

def load_ticker_data_from_excel(file_path):
    """東証上場銘柄一覧のExcelファイルから銘柄コードと日本語社名を読み込む"""
    try:
        df = pd.read_excel(file_path)
        required_cols = ['コード', '銘柄名']
        if not all(col in df.columns for col in required_cols):
            print(f"エラー: Excelファイル '{file_path}' に 'コード' または '銘柄名' 列が見つかりません。")
            return None
        
        ticker_df = df[required_cols].copy()
        ticker_df.rename(columns={'銘柄名': 'japaneseName'}, inplace=True)
        ticker_df['ticker'] = ticker_df['コード'].astype(str) + '.T'
        return ticker_df[['ticker', 'japaneseName']]
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。JPXサイトからダウンロードしてください。")
        return None
    except Exception as e:
        print(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
        return None

def get_stock_info(ticker_symbol):
    """指定された銘柄コードの株式情報を取得する"""
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if 'longName' not in info or info['longName'] is None:
            return None

        # --- 配当利回りの計算 ---
        # 年間配当(dividendRate)と株価(currentPrice)から配当利回りを計算
        dividend_rate = info.get('dividendRate')
        current_price = info.get('currentPrice')

        dividend_yield = None
        # 配当と株価の両方が取得でき、株価が0より大きい場合のみ計算
        if dividend_rate is not None and current_price is not None and current_price > 0:
            dividend_yield = dividend_rate / current_price
        # --- ここまで ---

        return {
            'ticker': ticker_symbol,
            'companyName': info.get('longName'),
            'forwardPE': info.get('forwardPE'),
            'priceToBook': info.get('priceToBook'),
            'dividendYield': dividend_yield,
            'currentPrice': current_price,
            'beta': info.get('beta'),
            'earningsGrowth': info.get('earningsGrowth'),
        }
    except Exception:
        return None

def main():
    """メイン処理"""
    print("銘柄リストをExcelファイルから読み込んでいます...")
    ticker_df = load_ticker_data_from_excel(TICKER_LIST_FILE_PATH)
    if ticker_df is None:
        sys.exit(1)

    print(f"{len(ticker_df)}件の銘柄データをyfinanceから取得します。これには数分かかります...")
    
    stock_data = []
    for row in tqdm(ticker_df.itertuples(), total=len(ticker_df), desc="データ取得中"):
        info = get_stock_info(row.ticker)
        if info:
            info['companyName'] = row.japaneseName # 日本語社名で上書き
            stock_data.append(info)
            
    if not stock_data:
        print("有効な株式情報が取得できませんでした。")
        sys.exit(1)
        
    all_stock_df = pd.DataFrame(stock_data)
    
    print(f"\n取得した{len(all_stock_df)}件のデータをParquetファイルに保存します...")
    all_stock_df.to_parquet(OUTPUT_PARQUET_PATH, index=False)
    print(f"正常に '{OUTPUT_PARQUET_PATH}' へ保存しました。")

if __name__ == "__main__":
    main()