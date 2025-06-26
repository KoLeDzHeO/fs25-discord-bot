import argparse
import asyncio

import aioftp
from config import config


async def upload_file(local_file: str, remote_path: str) -> None:
    async with aioftp.Client.context(
        config.FTP_HOST,
        config.FTP_PORT,
        config.FTP_USER,
        config.FTP_PASS,
    ) as ftp:
        await ftp.upload(local_file, remote_path)
        print(f"Uploaded {local_file} to {remote_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a file to the FTP server")
    parser.add_argument("local_file", help="Path to the local file")
    parser.add_argument("remote_path", help="Destination path on the server")
    args = parser.parse_args()

    asyncio.run(upload_file(args.local_file, args.remote_path))


if __name__ == "__main__":
    main()
