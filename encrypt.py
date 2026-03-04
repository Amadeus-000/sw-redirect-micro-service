import argparse
from urllib.parse import quote

from dotenv import load_dotenv

from libs.crypto import encrypt

# .envファイルから環境変数を読み込む
load_dotenv()


def main(work_id: str):
   encrypted_id = encrypt(work_id)
   encoded_id = quote(encrypted_id)
   print(f"Encrypted ID for '{work_id}': {encoded_id}")


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Encrypt and encode a work ID")
   parser.add_argument("work_id", help="Work ID to encrypt")
   args = parser.parse_args()

   main(args.work_id)
