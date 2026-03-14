import csv
import os
from typing import Any

import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


def fetch_all_redirects() -> list[dict[str, Any]]:
   """microCMSからすべてのリダイレクトデータを取得"""
   API_KEY = os.environ.get("MICRO_CMS_API_KEY")
   if not API_KEY:
      raise ValueError("MICRO_CMS_API_KEY environment variable is not set")

   all_contents = []
   offset = 0
   limit = 100  # 1回のリクエストで取得する件数

   while True:
      response = requests.get(
         url="https://sw-app.microcms.io/api/v1/redirect",
         headers={
            "X-MICROCMS-API-KEY": API_KEY,
         },
         params={
            "limit": limit,
            "offset": offset,
         },
      )
      response.raise_for_status()
      data = response.json()

      contents = data.get("contents", [])
      all_contents.extend(contents)

      # すべてのデータを取得したかチェック
      total_count = data.get("totalCount", 0)
      offset += limit

      print(f"取得済み: {len(all_contents)} / {total_count}")

      if len(all_contents) >= total_count:
         break

   return all_contents


def write_to_csv(data: list[dict[str, Any]], filename: str = "redirects.csv") -> None:
   """データをCSVファイルに書き出し"""
   if not data:
      print("データが空です")
      return

   # work_idでアルファベット順にソート
   sorted_data = sorted(data, key=lambda x: x.get("work_id", ""))

   # 各アイテムにリダイレクトURLを追加
   for item in sorted_data:
      item["full_redirect_url"] = f"https://sphereworld.org/redirect/?id={item.get('id', '')}"

   # すべてのキーを収集（データによってフィールドが異なる可能性があるため）
   all_keys = set()
   for item in sorted_data:
      all_keys.update(item.keys())

   # キーをソート（一貫性のため）
   fieldnames = sorted(all_keys)

   with open(filename, "w", newline="", encoding="utf-8") as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(sorted_data)

   print(f"CSVファイルを作成しました: {filename} ({len(sorted_data)}件)")


def main():
   """メイン処理"""
   try:
      print("リダイレクトデータを取得中...")
      redirects = fetch_all_redirects()
      print(f"合計 {len(redirects)} 件のデータを取得しました")

      write_to_csv(redirects)
      print("完了しました")

   except Exception as e:
      print(f"エラーが発生しました: {e}")
      raise


if __name__ == "__main__":
   main()
