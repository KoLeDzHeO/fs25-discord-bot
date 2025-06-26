fs25-discord-bot

Отображение техники которая нуждается в обслуживании
( damage: <5% , dirt: <5%, fuel: >80% )

Загрузчик FTP-файлов

Скрипт ftp_upload.py позволяет загружать произвольные файлы на FTP-сервер.
Параметры подключения можно передавать через аргументы командной строки
или переменные окружения FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS.

Пример запуска:

python ftp_upload.py local.zip /remote/path/remote.zip --host example.com --user user --password pass

