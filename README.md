# EquiSense - 株式スクリーニングアプリ 📈

EquiSenseは、PythonとStreamlitで構築された、日本株を対象としたインタラクティブな株式スクリーニングWebアプリケーションです。様々な投資戦略に基づき、あなたの基準に合った銘柄を簡単に見つけることができます。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://equisense-screener-da3rf8fey27lpfbpcdjuob.streamlit.app/)

**アプリはこちらからアクセスできます: [https://equisense-screener-da3rf8fey27lpfbpcdjuob.streamlit.app/](https://equisense-screener-da3rf8fey27lpfbpcdjuob.streamlit.app/)**

---

## ✨ 主な機能

*   **多彩なスクリーニング戦略**: 「成長株」「割安株」「高配当株」「安定株」といった代表的な投資戦略をプリセット。
*   **柔軟な条件調整**: PER、PBR、配当利回りなどのスクリーニング条件をスライダーで直感的に調整可能。
*   **株価での絞り込み**: 指定した株価の範囲で銘柄をフィルタリング。
*   **インタラクティブな結果表示**: スクリーニング結果はソート可能なテーブルで表示。
*   **データのエクスポート**: スクリーニング結果をCSVファイルとしてダウンロード可能。
*   **日次データ自動更新**: GitHub Actionsを利用して、毎日市場が閉まった後（15:30 JST）に株価データを自動で更新。

## 🚀 使い方

1.  サイドバーから分析したい**投資戦略**を選択します。
2.  表示されるスライダーを操作して、**PERやPBRなどの条件**を自由に調整します。
3.  必要に応じて、**株価の範囲**でさらに絞り込みます。
4.  「スクリーニング実行」ボタンをクリックすると、条件に合致した銘柄が一覧で表示されます。
