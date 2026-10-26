#!/bin/bash

# Nome do arquivo onde o relatório será salvo
RELATORIO="relatorio_sistema.txt"

# Função para gerar o cabeçalho do relatório
gerar_cabecalho() {
    echo "===================================" >> "$RELATORIO"
    echo "           Relatório de Sistema    " >> "$RELATORIO"
    echo "===================================" >> "$RELATORIO"
    echo "Data: $(date)" >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações do sistema operacional
informacoes_os() {
    echo "=== Informações do Sistema Operacional ===" >> "$RELATORIO"
    echo "Sistema: $(uname -o)" >> "$RELATORIO"
    echo "Kernel: $(uname -r)" >> "$RELATORIO"
    echo "Distribuição: $(cat /etc/os-release | grep PRETTY_NAME | cut -d '=' -f2 | tr -d '\"')" >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações do processador
informacoes_cpu() {
    echo "=== Informações do Processador ===" >> "$RELATORIO"
    lscpu >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações da memória
informacoes_memoria() {
    echo "=== Uso de Memória ===" >> "$RELATORIO"
    free -h >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações do disco
informacoes_disco() {
    echo "=== Uso de Disco ===" >> "$RELATORIO"
    df -h >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações dos dispositivos de bloco
informacoes_dispositivos() {
    echo "=== Dispositivos de Bloco ===" >> "$RELATORIO"
    lsblk >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para coletar informações sobre o uptime
informacoes_uptime() {
    echo "=== Uptime do Sistema ===" >> "$RELATORIO"
    uptime >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para listar usuários conectados
informacoes_usuarios() {
    echo "=== Usuários Conectados ===" >> "$RELATORIO"
    who >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Função para listar processos em execução
informacoes_processos() {
    echo "=== Processos em Execução ===" >> "$RELATORIO"
    ps aux | less >> "$RELATORIO"
    echo "" >> "$RELATORIO"
}

# Limpar o arquivo de relatório antes de gerar um novo
> "$RELATORIO"

# Gerar o cabeçalho do relatório
gerar_cabecalho

# Coletar informações do sistema
informacoes_os
informacoes_cpu
informacoes_memoria
informacoes_disco
informacoes_dispositivos
informacoes_uptime
informacoes_usuarios
informacoes_processos

# Exibir o relatório gerado
echo "Relatório gerado em: $RELATORIO"
