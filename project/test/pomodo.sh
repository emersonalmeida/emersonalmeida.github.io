#!/bin/bash

# Caminho do arquivo de histórico
HISTORICO="historico_pomodoro.txt"

# Função para registrar a tarefa no histórico
registrar_tarefa() {
    local tarefa="$1"
    local tempo_gasto="$2"
    local pomodoros="$3"
    local atraso="$4"
    echo -e "Tarefa: $tarefa\nTempo Total: $tempo_gasto minutos\nPomodoros: $pomodoros\nAtraso: $atraso minutos\n---" >> "$HISTORICO"
}

# Função para calcular o tempo em atraso
calcular_atraso() {
    local tempo_inicial="$1"
    local tempo_esperado="$2"
    local tempo_real="$(( ( $(date +%s) - tempo_inicial ) / 60 ))"
    if (( tempo_real > tempo_esperado )); then
        echo "$(( tempo_real - tempo_esperado ))"
    else
        echo 0
    fi
}

# Função para o Pomodoro
pomodoro() {
    echo "Digite o nome da tarefa:"
    read -r tarefa

    echo "Defina o tempo do Pomodoro (em minutos):"
    read -r pomodoro_tempo

    local inicio=$(date +%s)
    local tempo_passado=0
    local pomodoros=0
    local tarefa_finalizada=false

    # Loop do pomodoro
    while true; do
        echo "Iniciando Pomodoro para a tarefa: $tarefa - Tempo definido: $pomodoro_tempo minutos"
        
        # Espera pelo tempo do pomodoro em minutos
        sleep "$((pomodoro_tempo * 60))" &
        local timer_pid=$!

        # Aguardar a confirmação do usuário para terminar a tarefa ou sinal de conclusão do pomodoro
        while kill -0 $timer_pid 2>/dev/null; do
            echo -n "Digite 'fim' se concluir a tarefa antes do tempo: "
            read -t 1 resposta
            if [[ "$resposta" == "fim" ]]; then
                tarefa_finalizada=true
                break
            fi
        done

        # Interrompe o temporizador caso a tarefa tenha sido concluída
        if [ "$tarefa_finalizada" = true ]; then
            kill "$timer_pid" 2>/dev/null
            break
        fi

        # Incrementa o contador de pomodoros
        pomodoros=$((pomodoros + 1))
        tempo_passado=$((pomodoros * pomodoro_tempo))
        echo "Pomodoro $pomodoros concluído."

        # Checa se a tarefa foi finalizada
        if [ "$tarefa_finalizada" = true ]; then
            break
        fi
    done

    # Calcula o atraso, caso haja
    local atraso=$(calcular_atraso "$inicio" "$tempo_passado")
    if (( atraso > 0 )); then
        echo "A tarefa foi finalizada com um atraso de $atraso minutos."
    fi

    # Registra a tarefa no histórico
    registrar_tarefa "$tarefa" "$tempo_passado" "$pomodoros" "$atraso"
    echo "Tarefa '$tarefa' registrada com sucesso!"
}

# Função para exibir o histórico
exibir_historico() {
    echo -e "\n==== Histórico de Tarefas Pomodoro ===="
    if [ -f "$HISTORICO" ]; then
        cat "$HISTORICO"
    else
        echo "Nenhum histórico encontrado."
    fi
    echo -e "=======================================\n"
}

# Loop principal
while true; do
    exibir_historico
    pomodoro
    echo "Deseja iniciar uma nova tarefa? (s/n)"
    read -r resposta
    if [[ "$resposta" != "s" ]]; then
        break
    fi
done
