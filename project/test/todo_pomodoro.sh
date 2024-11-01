#!/bin/bash

# Inicializa a lista de tarefas
TAREFAS=()

# Função para exibir o menu
mostrar_menu() {
    echo "======================"
    echo " Sistema de To Do"
    echo "======================"
    echo "1. Adicionar tarefa"
    echo "2. Listar tarefas"
    echo "3. Iniciar Pomodoro"
    echo "4. Sair"
    echo "======================"
}

# Função para adicionar uma tarefa
adicionar_tarefa() {
    read -p "Digite a nova tarefa: " tarefa
    TAREFAS+=("$tarefa")
    echo "Tarefa adicionada: $tarefa"
}

# Função para listar tarefas
listar_tarefas() {
    if [ ${#TAREFAS[@]} -eq 0 ]; then
        echo "Nenhuma tarefa na lista."
    else
        echo "Tarefas:"
        for i in "${!TAREFAS[@]}"; do
            echo "$((i + 1)). ${TAREFAS[i]}"
        done
    fi
}

# Função para iniciar o temporizador Pomodoro com contagem regressiva
iniciar_pomodoro() {
    echo "Iniciando Pomodoro de 1 minuto..."
    for ((i=60; i>0; i--)); do
        mins=$((i / 60))
        secs=$((i % 60))
        printf "\rContagem regressiva: %02d:%02d" $mins $secs
        sleep 1
    done
    echo -e "\nTempo do Pomodoro terminado!"
    notify-send "Pomodoro terminado!" "É hora de fazer uma pausa."

    for ((j=300; j>0; j--)); do
        mins=$((j / 60))
        secs=$((j % 60))
        printf "\rPausa de 5 minutos: %02d:%02d" $mins $secs
        sleep 1
    done
    echo -e "\nPausa de 5 minutos terminada!"
    notify-send "Pausa terminada!" "Volte ao trabalho!"
}

# Loop principal
while true; do
    mostrar_menu
    read -p "Escolha uma opção: " opcao

    case $opcao in
        1)
            adicionar_tarefa
            ;;
        2)
            listar_tarefas
            ;;
        3)
            iniciar_pomodoro
            ;;
        4)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            ;;
    esac
done

