#!/usr/bin/env bash

# Установить нужную версию Python
echo "python-3.11.8" > runtime.txt

# Запустить обычную установку
pip install -r requirements.txt
