#!/bin/bash

# Arquivo onde as tarefas serão armazenadas
TASK_FILE="tarefas.txt"

# Função para exibir o menu
show_menu() {
    echo "Gerenciador de Tarefas"
    echo "1) Adicionar Tarefa"
    echo "2) Listar Tarefas"
    echo "3) Atualizar Tarefa"
    echo "4) Deletar Tarefa"
    echo "5) Sair"
}

# Função para adicionar uma nova tarefa
add_task() {
    read -p "Digite a descrição da nova tarefa: " task
    echo "$task" >> "$TASK_FILE"
    echo "Tarefa adicionada: $task"
}

# Função para listar todas as tarefas
list_tasks() {
    if [ ! -s "$TASK_FILE" ]; then
        echo "Nenhuma tarefa encontrada."
        return
    fi
    
    echo "Tarefas:"
    nl -w2 -s") " "$TASK_FILE"
}

# Função para atualizar uma tarefa existente
update_task() {
    list_tasks
    read -p "Digite o número da tarefa que deseja atualizar: " task_number

    if ! [[ "$task_number" =~ ^[0-9]+$ ]]; then
        echo "Número inválido."
        return
    fi

    # Verifica se a tarefa existe
    task_line=$(sed -n "${task_number}p" "$TASK_FILE")
    if [ -z "$task_line" ]; then
        echo "Tarefa não encontrada."
        return
    fi

    read -p "Digite a nova descrição para a tarefa: " new_task
    sed -i "${task_number}s/.*/$new_task/" "$TASK_FILE"
    echo "Tarefa atualizada: $new_task"
}

# Função para deletar uma tarefa
delete_task() {
    list_tasks
    read -p "Digite o número da tarefa que deseja deletar: " task_number

    if ! [[ "$task_number" =~ ^[0-9]+$ ]]; then
        echo "Número inválido."
        return
    fi

    # Verifica se a tarefa existe
    task_line=$(sed -n "${task_number}p" "$TASK_FILE")
    if [ -z "$task_line" ]; then
        echo "Tarefa não encontrada."
        return
    fi

    # Remove a tarefa
    sed -i "${task_number}d" "$TASK_FILE"
    echo "Tarefa deletada: $task_line"
}

# Loop principal do programa
while true; do
    show_menu
    read -p "Escolha uma opção (1-5): " option

    case $option in
        1) add_task ;;
        2) list_tasks ;;
        3) update_task ;;
        4) delete_task ;;
        5) echo "Saindo..."; exit 0 ;;
        *) echo "Opção inválida." ;;
    esac

    echo
done
