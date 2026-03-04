import argparse
import logging
from urllib.parse import quote

from dotenv import load_dotenv

from libs.crypto import encrypt

load_dotenv()
logger = logging.getLogger(__name__)


def main(work_id: str):
   encrypted_id = encrypt(work_id)
   encoded_id = quote(encrypted_id)
   logger.info(f"Encrypted ID for '{work_id}': {encoded_id}")


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Encrypt and encode a work ID")
   parser.add_argument("work_id", help="Work ID to encrypt")
   args = parser.parse_args()
   logging.basicConfig(level=logging.INFO)
   main(args.work_id)
