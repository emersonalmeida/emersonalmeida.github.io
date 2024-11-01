#!/bin/bash

# Define o arquivo de log
LOG_FILE="/var/log/syslog"
# Define o arquivo de saída
OUTPUT_FILE="analise_logs.txt"

# Verifica se o arquivo de log existe
if [[ ! -f $LOG_FILE ]]; then
    echo "Arquivo de log não encontrado: $LOG_FILE"
    exit 1
fi

# Limpa o arquivo de saída anterior
> $OUTPUT_FILE

# Filtra erros e avisos
echo "Analisando logs do sistema em $LOG_FILE" >> $OUTPUT_FILE
echo "===================================" >> $OUTPUT_FILE

# Captura erros e avisos
ERRORS=$(grep -i "error" $LOG_FILE)
WARNINGS=$(grep -i "warning" $LOG_FILE)

# Escreve erros e avisos no arquivo de saída
echo "Erros encontrados:" >> $OUTPUT_FILE
echo "$ERRORS" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "Avisos encontrados:" >> $OUTPUT_FILE
echo "$WARNINGS" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Conta total de erros e avisos
ERROR_COUNT=$(echo "$ERRORS" | wc -l)
WARNING_COUNT=$(echo "$WARNINGS" | wc -l)

# Adiciona contagem ao arquivo de saída
echo "Total de erros: $ERROR_COUNT" >> $OUTPUT_FILE
echo "Total de avisos: $WARNING_COUNT" >> $OUTPUT_FILE

# Mensagem final
echo "Análise completa. Resultados salvos em $OUTPUT_FILE."
