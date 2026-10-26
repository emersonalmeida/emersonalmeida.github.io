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

# Exibe a saudação inicial
zenity --info --text="$GREETING, $USER_NAME!"

# Pergunta pela cidade e previsão do tempo
CITY=$(zenity --entry --text="Qual é a sua cidade?")

# Obtém informações sobre o tempo
WEATHER_DATA=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=-23.5505&longitude=-46.6333&current_weather=true")
CITY_NAME=$(echo $WEATHER_DATA | jq -r '.current_weather')

# Exibe clima atual
zenity --info --text="Clima atual: $CITY_NAME"

# Pergunta sobre a tarefa
TASK=$(zenity --entry --text="Qual tarefa você deseja focar?")

# Início do temporizador
START_TIME=$(date +%s)

# Cria a janela de progresso
(
    for (( ELAPSED=0; ; ELAPSED++ )); do
        # Calcula o tempo decorrido
        DIFF=$(( $(date +%s) - START_TIME ))
        
        # Atualiza a barra de progresso com o tempo decorrido
        echo "$DIFF"
        echo "# Tempo gasto na tarefa: $DIFF segundos"
        sleep 1
        
        # Verifica se o usuário deseja parar
        if ! zenity --question --text="A tarefa '$TASK' ainda está em andamento. Pressione OK para finalizar ou Cancelar para continuar."; then
            break
        fi
    done
) | zenity --progress --title="Contador de Tarefa" --text="Iniciando o temporizador para a tarefa: $TASK" --percentage=0 --auto-close

# Finaliza o contador
END_TIME=$(date +%s)
TOTAL_TIME=$(( END_TIME - START_TIME ))

# Registra a tarefa e o tempo gasto
echo "$(date +'%Y-%m-%d %H:%M:%S') - Tarefa: $TASK - Tempo: $TOTAL_TIME segundos" >> historico_tarefas.txt

# Exibe tempo total gasto na tarefa
zenity --info --text="Tempo total gasto na tarefa '$TASK': $TOTAL_TIME segundos"

