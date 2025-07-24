import pandas as pd
import yfinance as yf
from tqdm import tqdm
import sys
from datetime import datetime
import os

# --- 定数定義 ---


# スクリプト自身の絶対パスを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
# Excelファイルの絶対パスを構築することで、どこから実行してもファイルを見つけられるようにする
TICKER_LIST_FILE_PATH = os.path.join(script_dir, 'tosho_list.xlsx')

# 表示するカラムと日本語名のマッピング
COLUMN_MAPPING = {
    'ticker': '銘柄コード',
    'companyName': '企業名',
    'forwardPE': '予想PER',
    'priceToBook': 'PBR',
    'dividendYield': '配当利回り',
    'currentPrice': '現在株価',
    'beta': 'ベータ値',
    'earningsGrowth': '収益成長率'
}

def load_tickers_from_excel(file_path):
    """
    東証上場銘柄一覧のExcelファイルから銘柄コードのリストを読み込む
    """
    try:
        df = pd.read_excel(file_path)
        # 'コード'列を抽出し、yfinanceで使えるように末尾に'.T'を付与する
        # JPXのファイルでは銘柄コードは 'コード' という列名で格納されている
        if 'コード' not in df.columns:
            print(f"エラー: Excelファイル '{file_path}' に 'コード' 列が見つかりません。")
            sys.exit() # プログラムを終了
            
        tickers = df['コード'].astype(str) + '.T'
        return tickers.tolist()
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        print("JPXサイトから「東証上場銘柄一覧」をダウンロードし、同じフォルダに配置してください。")
        sys.exit() # プログラムを終了
    except Exception as e:
        print(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
        sys.exit()

def get_stock_info(ticker_symbol):
    """
    指定された銘柄コードの株式情報を取得する（取得項目を拡張）
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        return {
            'ticker': ticker_symbol,
            'companyName': info.get('longName'),
            'forwardPE': info.get('forwardPE'),
            'priceToBook': info.get('priceToBook'),
            'dividendYield': info.get('dividendYield', 0) * 100,
            'currentPrice': info.get('currentPrice'),
            'beta': info.get('beta'), # 安定株スクリーニング用
            'earningsGrowth': info.get('earningsGrowth'), # 成長株スクリーニング用
        }
    except Exception:
        # 多くの銘柄を処理するため、個別のエラーはコンソールに出さずスキップする
        return None

def screen_stocks(df, strategy):
    """
    指定された戦略に基づいて株式をスクリーニングする
    """
    print(f"\n--- 「{strategy['name']}」の条件でスクリーニングを実行します ---")
    for condition_text in strategy['description']:
        print(f"- {condition_text}")
    print("--------------------------------------------------\n")

    # スクリーニングに必要なカラムが存在しない行を削除
    required_cols = [col for col in strategy['conditions'].keys()]
    screened_df = df.dropna(subset=required_cols).copy()

    # 条件式を適用
    for col, condition in strategy['conditions'].items():
        screened_df = screened_df.query(condition)
        
    return screened_df

def display_results(df, display_cols, strategy_name):
    """
    スクリーニング結果を整形して表示し、CSVファイルに保存する機能を提供する
    """
    if df.empty:
        print("条件に合致する銘柄は見つかりませんでした。")
        return

    # --- データの準備 ---
    # 表示・保存用に元データから必要な列を抽出し、列名を日本語に変換
    result_jp_df = df[display_cols].copy()
    result_jp_df.rename(columns=COLUMN_MAPPING, inplace=True)

    # --- コンソール表示用のデータ整形 ---
    display_df = result_jp_df.copy()
    formatters = {
        '配当利回り': '{:,.2f}%',
        '予想PER': '{:,.2f}',
        'PBR': '{:,.2f}',
        'ベータ値': '{:,.2f}',
        '収益成長率': '{:.2%}'
    }
    for col, fmt in formatters.items():
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: fmt.format(x) if pd.notna(x) else 'N/A')

    print("--- スクリーニング結果 ---")
    print(display_df.to_string(index=False))

    # --- CSVファイルへの保存 ---
    while True:
        save_choice = input("\nこの結果をCSVファイルに保存しますか？ (y/n): ").lower()
        if save_choice in ['y', 'n']:
            break
        print("無効な入力です。'y'または'n'を入力してください。")

    if save_choice == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"スクリーニング結果_{strategy_name}_{timestamp}.csv"
        save_path = os.path.join(script_dir, filename)

        try:
            # フォーマット前の生データを日本語列名で保存（Excelで開きやすいようにutf-8-sigを指定）
            result_jp_df.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"\n結果を '{save_path}' に保存しました。")
        except Exception as e:
            print(f"\nファイルの保存中にエラーが発生しました: {e}")

def main():
    """
    メインの処理
    """
    # --- スクリーニング戦略の定義 ---
    strategies = {
        '1': {
            'name': '成長株',
            'description': ['収益成長率が20%以上', '予想PERが25倍以上 (高い成長性を評価)'],
            'conditions': {'earningsGrowth': 'earningsGrowth >= 0.2', 'forwardPE': 'forwardPE >= 25'},
            'display_cols': ['ticker', 'companyName', 'earningsGrowth', 'forwardPE', 'currentPrice']
        },
        '2': {
            'name': '割安株',
            'description': ['予想PERが15倍以下', 'PBRが1倍以下', '配当利回りが3%以上'],
            'conditions': {'forwardPE': 'forwardPE <= 15', 'priceToBook': 'priceToBook <= 1', 'dividendYield': 'dividendYield >= 3'},
            'display_cols': ['ticker', 'companyName', 'forwardPE', 'priceToBook', 'dividendYield', 'currentPrice']
        },
        '3': {
            'name': '高配当株',
            'description': ['配当利回りが4%以上', 'PBRが2倍以下 (割高すぎない)'],
            'conditions': {'dividendYield': 'dividendYield >= 4', 'priceToBook': 'priceToBook <= 2'},
            'display_cols': ['ticker', 'companyName', 'dividendYield', 'forwardPE', 'PBR', 'currentPrice']
        },
        '4': {
            'name': '安定株',
            'description': ['ベータ値が0.8未満 (市場平均より変動が小さい)'],
            'conditions': {'beta': 'beta < 0.8'},
            'display_cols': ['ticker', 'companyName', 'beta', 'dividendYield', 'forwardPE', 'currentPrice']
        }
    }

    # --- ユーザーに戦略を選択させる ---
    print("どの戦略でスクリーニングしますか？番号を入力してください。")
    for key, value in strategies.items():
        print(f"{key}: {value['name']}")
    
    choice = input("番号: ")
    
    if choice not in strategies:
        print("無効な選択です。プログラムを終了します。")
        return
        
    selected_strategy = strategies[choice]

    # --- データ取得 ---
    ticker_list = load_tickers_from_excel(TICKER_LIST_FILE_PATH)
    # 動作テスト用に銘柄数を制限したい場合は、以下のコメントを解除
    # ticker_list = ticker_list[:50] 

    stock_data = []
    for ticker in tqdm(ticker_list, desc="全上場銘柄の情報を取得中"):
        info = get_stock_info(ticker)
        if info:
            stock_data.append(info)

    if not stock_data:
        print("有効な株式情報が取得できませんでした。")
        return

    df = pd.DataFrame(stock_data)

    # --- スクリーニングと結果表示 ---
    result_df = screen_stocks(df, selected_strategy)
    display_results(result_df, selected_strategy['display_cols'], selected_strategy['name'])

if __name__ == "__main__":
    main()
