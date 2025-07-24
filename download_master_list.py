import os
import sys

# このスクリプトは、JPXサイトから最新の上場銘柄一覧ファイルをダウンロードし、
# 'tosho_list.xlsx' という名前で保存します。

try:
    import requests
except ImportError:
    print("エラー: このスクリプトの実行には 'requests' ライブラリが必要です。")
    print("コマンドプロンプトで `pip install requests` を実行してインストールしてください。")
    sys.exit(1)

# --- 定数定義 ---
URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILENAME = "tosho_list.xlsx"
OUTPUT_PATH = os.path.join(BASE_DIR, OUTPUT_FILENAME)

def main():
    """JPXから上場企業一覧ファイルをダウンロードして保存する"""
    print("=" * 50)
    print("  JPX上場銘柄一覧 ダウンロードツール")
    print("=" * 50)
    print(f"\nダウンロード元URL: {URL}")
    print(f"保存先: {OUTPUT_PATH}\n")

    try:
        print("ダウンロードを開始します...")
        # タイムアウトを60秒に設定し、ストリーミングでダウンロード
        response = requests.get(URL, stream=True, timeout=60)
        # HTTPエラー(4xx, 5xx)の場合に例外を発生させる
        response.raise_for_status()

        # ファイルに書き込み
        with open(OUTPUT_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("\nダウンロードが正常に完了しました。")
        print(f"'{os.path.basename(OUTPUT_PATH)}' を更新しました。")

    except requests.exceptions.RequestException as e:
        print(f"\nエラー: ダウンロードに失敗しました。ネットワーク接続やURLを確認してください。\n詳細: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"\nエラー: ファイルの書き込みに失敗しました。アクセス権を確認してください。\n詳細: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()