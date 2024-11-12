#!/bin/bash

# Função para exibir uma mensagem de introdução
intro() {
    echo "Bem-vindo ao mundo de Matrix."
    echo "Você é um hacker que suspeita que a realidade ao seu redor é uma ilusão."
    echo "O que você fará? (Digite 'começar' para iniciar)"
}

# Função para processar as escolhas do jogador
decisao() {
    echo "Você está em um quarto escuro. Há uma tela de computador e uma porta à sua frente."
    echo "Você pode (1) usar o computador ou (2) sair pela porta."
    read -p "Escolha uma opção: " escolha

    if [ "$escolha" -eq 1 ]; then
        echo "Você se aproxima do computador e começa a hackear..."
        hackear
    elif [ "$escolha" -eq 2 ]; then
        echo "Você abre a porta e sai. Você é abordado por um agente!"
        agente
    else
        echo "Escolha inválida. Tente novamente."
        decisao
    fi
}

# Função para o hacking
hackear() {
    echo "Você descobriu uma mensagem codificada. Deseja decifrá-la? (sim/não)"
    read resposta
    if [[ "$resposta" == "sim" ]]; then
        echo "Mensagem decifrada: 'A verdade é que você está preso na Matrix.'"
        echo "Você sente um chamado para se juntar à resistência."
    else
        echo "Você decidiu ignorar a mensagem."
    fi
    decisao
}

# Função para lidar com o agente
agente() {
    echo "O agente pergunta: 'Você está preparado para enfrentar a verdade?'"
    echo "Você pode (1) lutar ou (2) correr."
    read escolha_agente

    if [ "$escolha_agente" -eq 1 ]; then
        echo "Você luta bravamente, mas é capturado!"
        echo "Fim do jogo."
    elif [ "$escolha_agente" -eq 2 ]; then
        echo "Você corre e consegue escapar para a próxima sala!"
        decisao
    else
        echo "Escolha inválida. Tente novamente."
        agente
    fi
}

# Execução do jogo
intro
read -p "Pressione Enter para continuar..."
decisao
