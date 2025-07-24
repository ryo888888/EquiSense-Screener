@echo off
REM 日本語が文字化けするのを防ぎます
chcp 65001 > nul

echo ==================================================
echo.
echo   JPX上場銘柄一覧 ダウンロード
echo.
echo ==================================================
echo.

REM バッチファイルがあるディレクトリに移動します
cd /d %~dp0

echo Pythonスクリプト (download_master_list.py) を実行しています...
python download_master_list.py

echo.
echo 処理が完了しました。このウィンドウは閉じて構いません。
echo.
pause