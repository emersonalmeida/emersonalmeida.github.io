#!/bin/bash

# Obtém o nome do usuário ativo
USER_NAME=$(whoami)

# Obtém a hora atual
HOUR=$(date +%H)

# Determina a saudação
if [ $HOUR -lt 12 ]; then
    GREETING="Bom dia"
elif [ $HOUR -lt 18 ]; then
    GREETING="Boa tarde"
else
    GREETING="Boa noite"
fi

echo "$GREETING, $USER_NAME!"

# Altere 'Sao Paulo' pela cidade desejada
CITY="Sao Paulo"
API_KEY="your_api_key_here" # Se necessário, você pode utilizar uma API pública

# Obtém informações sobre o tempo
WEATHER_DATA=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=-23.5505&longitude=-46.6333&current_weather=true")

# Extraindo as informações de clima
CITY_NAME=$(echo $WEATHER_DATA | jq -r '.current_weather')
echo "Clima atual: $CITY_NAME"

echo "Qual tarefa você deseja focar?"
read TASK

echo "Iniciando o temporizador para a tarefa: $TASK"
START_TIME=$(date +%s)

# Espera o usuário pressionar 'Enter' para finalizar
read -p "Pressione Enter quando a tarefa estiver concluída..."

END_TIME=$(date +%s)
DIFF=$(( END_TIME - START_TIME ))

echo "Tempo gasto na tarefa '$TASK': $DIFF segundos"

echo "$(date +'%Y-%m-%d %H:%M:%S') - Tarefa: $TASK - Tempo: $DIFF segundos" >> historico_tarefas.txt

