@echo off
REM 日本語が文字化けするのを防ぎます
chcp 65001 > nul

echo ==================================================
echo.
echo   EquiSense - 株式データ更新ツール
echo.
echo ==================================================
echo.

REM バッチファイルがあるディレクトリに移動します
cd /d %~dp0

echo Pythonスクリプト (fetch_data.py) を実行しています...
python fetch_data.py

echo.
echo データ更新が完了しました。このウィンドウは閉じて構いません。
echo.
pause