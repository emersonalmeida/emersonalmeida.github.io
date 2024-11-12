#! /bin/bash

origem="~/.local/share/todo.txt/todo.txt"
destino="/mnt/sda4/git/emersonalmeida.github.io/.tmp/obs/todo/todo.md"
sed -i 's/^ID:([0-9]+) VALOR:(.*)$/\1  VALOR>NOVA_VALE\n/' $origem
