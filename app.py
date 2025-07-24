import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 定数と設定 ---

# ページ設定 (ワイドモード、初期状態)
st.set_page_config(layout="wide", page_title="EquiSense - 株式スクリーニング")

# スクリプト自身の絶対パスを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
# 事前取得したデータファイルのパス
PREFETCHED_DATA_PATH = os.path.join(script_dir, 'all_stock_data.parquet')

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

# 用語解説
TERM_DESCRIPTIONS = {
    'forwardPE': '株価が1株当たり純利益の何倍まで買われているかを示す指標。数値が低いほど、株価は割安と判断される。',
    'priceToBook': '株価が1株当たり純資産の何倍まで買われているかを示す指標。1倍が株価の底値の目安とされ、低いほど割安と判断される。',
    'dividendYield': '株価に対する年間配当金の割合。数値が高いほど、投資額に対して多くの配当を受け取れることを示す。',
    'beta': '市場全体（例: TOPIX）の動きに対して、個別銘柄がどの程度連動して動くかを示す指標。1より小さいと市場平均より値動きが穏やかとされ、安定性を重視する場合に参照される。',
    'earningsGrowth': '企業の収益（利益）がどれくらいのペースで成長しているかを示す指標。数値が高いほど、企業の成長性が高いと評価される。'
}

# --- データ取得関数 (Streamlitのキャッシュ機能で高速化) ---

@st.cache_data # データをメモリにキャッシュして高速化
def load_prefetched_data(file_path):
    """事前取得されたParquetファイルから全銘柄データを読み込む"""
    try:
        return pd.read_parquet(file_path)
    except FileNotFoundError:
        st.error(f"データファイル '{os.path.basename(file_path)}' が見つかりません。")
        st.error("先に `python fetch_data.py` を実行して、データファイルを作成してください。")
        st.stop()
    except Exception as e:
        st.error(f"データファイルの読み込み中にエラーが発生しました: {e}")
        st.stop()

# --- UIの定義 ---

st.title('📈 EquiSense - 株式スクリーニングアプリ')
st.write('東証上場銘柄を対象に、指定した戦略でスクリーニングを実行します。')

# --- スクリーニング戦略の定義 (動的UI対応) ---
strategies = {
    '成長株': {
        'adjustable_params': [
            {'label': '収益成長率 (下限) %', 'key': 'earningsGrowth', 'operator': '>=', 'min_val': 0.0, 'max_val': 100.0, 'step': 5.0, 'default_val': 20.0, 'is_percent': True},
            {'label': '予想PER (下限)', 'key': 'forwardPE', 'operator': '>=', 'min_val': 10, 'max_val': 100, 'step': 5, 'default_val': 25}
        ],
        'display_cols': ['ticker', 'companyName', 'earningsGrowth', 'forwardPE', 'currentPrice']
    },
    '割安株': {
        'adjustable_params': [
            {'label': '予想PER (上限)', 'key': 'forwardPE', 'operator': '<=', 'min_val': 5, 'max_val': 50, 'step': 1, 'default_val': 15},
            {'label': 'PBR (上限)', 'key': 'priceToBook', 'operator': '<=', 'min_val': 0.5, 'max_val': 5.0, 'step': 0.1, 'default_val': 1.0},
            {'label': '配当利回り (下限) %', 'key': 'dividendYield', 'operator': '>=', 'min_val': 0.0, 'max_val': 10.0, 'step': 0.5, 'default_val': 3.0, 'is_percent': True}
        ],
        'display_cols': ['ticker', 'companyName', 'forwardPE', 'priceToBook', 'dividendYield', 'currentPrice']
    },
    '高配当株': {
        'adjustable_params': [
            {'label': '配当利回り (下限) %', 'key': 'dividendYield', 'operator': '>=', 'min_val': 0.0, 'max_val': 10.0, 'step': 0.5, 'default_val': 4.0, 'is_percent': True},
            {'label': 'PBR (上限)', 'key': 'priceToBook', 'operator': '<=', 'min_val': 0.5, 'max_val': 5.0, 'step': 0.1, 'default_val': 2.0}
        ],
        'display_cols': ['ticker', 'companyName', 'dividendYield', 'forwardPE', 'priceToBook', 'currentPrice']
    },
    '安定株': {
        'adjustable_params': [
            {'label': 'ベータ値 (上限)', 'key': 'beta', 'operator': '<', 'min_val': 0.0, 'max_val': 1.5, 'step': 0.1, 'default_val': 0.8}
        ],
        'display_cols': ['ticker', 'companyName', 'beta', 'dividendYield', 'forwardPE', 'currentPrice']
    }
}

# --- サイドバー (入力コントロール) ---
st.sidebar.header('ℹ️ データ情報')
try:
    # データファイルの最終更新日時を取得
    last_modified_unix = os.path.getmtime(PREFETCHED_DATA_PATH)
    last_modified_dt = datetime.fromtimestamp(last_modified_unix)
    last_modified_str = last_modified_dt.strftime("%Y年%m月%d日 %H:%M")
    st.sidebar.caption(f"データ最終更新: {last_modified_str}")
except FileNotFoundError:
    # ファイルがない場合は警告を表示
    st.sidebar.warning("データファイルがありません。\n`python fetch_data.py` を実行してください。")
    
st.sidebar.header('⚙️ スクリーニング条件')
selected_strategy_name = st.sidebar.selectbox('戦略を選択してください:', list(strategies.keys()))
selected_strategy = strategies[selected_strategy_name]

st.sidebar.subheader('条件を調整')
user_inputs = {}
descriptions = []
for param in selected_strategy['adjustable_params']:
    user_value = st.sidebar.slider(
        label=param['label'],
        min_value=param['min_val'],
        max_value=param['max_val'],
        value=param['default_val'],
        step=param['step']
    )
    user_inputs[param['key']] = user_value
    
    # 説明文を動的に生成
    display_value = f"{user_value:g}%" if param.get('is_percent', False) else f"{user_value:g}"
    desc_text = param['label'].replace('(上限)', f'が {display_value} 以下').replace('(下限)', f'が {display_value} 以上')
    descriptions.append(f"- {desc_text}")

st.sidebar.info('**現在のスクリーニング条件:**\n\n' + '\n\n'.join(descriptions))

st.sidebar.subheader('共通フィルター')
price_range = st.sidebar.slider(
    '株価範囲 (円)',
    min_value=0,
    max_value=50000, # 5万円を上限とする
    value=(0, 50000), # デフォルトは全範囲
    step=100
)

run_button = st.sidebar.button('スクリーニング実行', type="primary")

# --- メイン画面 (結果表示) ---
if run_button:
    all_stock_df = load_prefetched_data(PREFETCHED_DATA_PATH)

    st.header(f"📊 「{selected_strategy_name}」スクリーニング結果")

    # スクリーニング実行
    required_cols = [p['key'] for p in selected_strategy['adjustable_params']]
    # 株価フィルターも適用するため、'currentPrice'を必須カラムに追加
    if 'currentPrice' not in required_cols:
        required_cols.append('currentPrice')
    result_df = all_stock_df.dropna(subset=required_cols).copy()
    
    # 動的に生成された条件でフィルタリング (query()を廃止し、より堅牢な直接比較に変更)
    for param in selected_strategy['adjustable_params']:
        key = param['key']
        operator = param['operator']
        user_value = user_inputs[key]
        
        if operator == '>=':
            result_df = result_df[result_df[key] >= user_value]
        elif operator == '<=':
            result_df = result_df[result_df[key] <= user_value]
        elif operator == '>':
            result_df = result_df[result_df[key] > user_value]
        elif operator == '<':
            result_df = result_df[result_df[key] < user_value]

    # 共通フィルター（株価）を適用
    min_price, max_price = price_range
    result_df = result_df[result_df['currentPrice'].between(min_price, max_price)]

    if result_df.empty:
        st.warning('条件に合致する銘柄は見つかりませんでした。')
    else:
        # 結果表示用のDataFrameを準備
        display_cols = selected_strategy['display_cols']
        display_df = result_df[display_cols].rename(columns=COLUMN_MAPPING)
        
        st.info(f"**{len(result_df)}件** の銘柄が見つかりました。")

        # --- テーブル表示 (ソート可能) ---
        # カラムヘッダクリックでソート可能にするため、st.column_config を使用
        column_configs = {
            "配当利回り": st.column_config.NumberColumn(
                "配当利回り (%)", format="%.2f"
            ),
            "収益成長率": st.column_config.NumberColumn(
                "収益成長率 (%)", format="%.2f"
            ),
            "現在株価": st.column_config.NumberColumn(
                "現在株価 (円)", format="¥%d"
            ),
            "予想PER": st.column_config.NumberColumn("予想PER (倍)", format="%.2f"),
            "PBR": st.column_config.NumberColumn("PBR (倍)", format="%.2f"),
            "ベータ値": st.column_config.NumberColumn("ベータ値", format="%.2f"),
        }

        # 表示用にパーセント値を100倍する (CSV保存用とは別のDataFrameを操作)
        display_df_formatted = display_df.copy()
        if '収益成長率' in display_df_formatted.columns:
            display_df_formatted['収益成長率'] *= 100

        st.dataframe(
            display_df_formatted,
            column_config=column_configs,
            use_container_width=True,
            hide_index=True
        )

        # CSVダウンロードボタン
        csv_data = display_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"スクリーニング結果_{selected_strategy_name}_{timestamp}.csv"
        
        st.download_button(
           label="結果をCSVでダウンロード",
           data=csv_data,
           file_name=filename,
           mime='text/csv',
        )

        # --- 用語解説の表示 ---
        st.divider()
        st.subheader('📈 用語解説')

        # 表示されている列のキーに基づいて解説を表示
        for col_key in display_cols:
            if col_key in TERM_DESCRIPTIONS:
                st.markdown(f"- **{COLUMN_MAPPING.get(col_key, col_key)}**: {TERM_DESCRIPTIONS[col_key]}")
else:
    st.info('サイドバーで戦略を選択し、「スクリーニング実行」ボタンを押してください。')
