import os
import argparse
import ftplib

def ensure_remote_dir(ftp: ftplib.FTP, path: str) -> None:
    """Create remote directories if they do not exist."""
    if not path:
        return
    current = ftp.pwd()
    for part in path.split('/'):
        if not part:
            continue
        try:
            ftp.mkd(part)
        except ftplib.error_perm:
            pass
        ftp.cwd(part)
    ftp.cwd(current)


def upload_file(host: str, port: int, user: str, password: str,
                local_file: str, remote_path: str) -> None:
    with ftplib.FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(user, password)
        remote_dir, remote_name = os.path.split(remote_path)
        ensure_remote_dir(ftp, remote_dir)
        if remote_dir:
            ftp.cwd(remote_dir)
        with open(local_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote_name}', f)
        print(f'Uploaded {local_file} to {remote_path}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Upload a file to an FTP server')
    parser.add_argument('local_file', help='Path to the local file to upload')
    parser.add_argument('remote_path', help='Destination path on the FTP server')
    parser.add_argument('--host', default=os.getenv('FTP_HOST'), help='FTP server host')
    parser.add_argument('--port', type=int, default=int(os.getenv('FTP_PORT', '21')), help='FTP server port')
    parser.add_argument('--user', default=os.getenv('FTP_USER'), help='FTP username')
    parser.add_argument('--password', default=os.getenv('FTP_PASS'), help='FTP password')

    args = parser.parse_args()

    missing = [name for name in ['host', 'user', 'password'] if not getattr(args, name)]
    if missing:
        parser.error('Missing required connection info: ' + ', '.join(missing))

    upload_file(args.host, args.port, args.user, args.password,
                args.local_file, args.remote_path)

if __name__ == '__main__':
    main()
