#!/bin/bash

# Configurações
LATITUDE="52.52"  # Substitua pela latitude da sua localização
LONGITUDE="13.41" # Substitua pela longitude da sua localização

# Obtendo data e hora do sistema
DATA_HORA=$(date "+%Y-%m-%d %H:%M:%S")
HORA=$(date "+%H")

# Verificando a parte do dia
if [ $HORA -lt 12 ]; then
    SAUDACAO="Bom dia"
elif [ $HORA -lt 18 ]; then
    SAUDACAO="Boa tarde"
else
    SAUDACAO="Boa noite"
fi

# Fazendo a requisição à API para obter a temperatura
RESPOSTA=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=${LATITUDE}&longitude=${LONGITUDE}&current=temperature_2m,wind_speed_10m")

# Extraindo os dados da resposta JSON
TEMP=$(echo $RESPOSTA | jq '.current.temperature_2m')
LOCALIZACAO="$LATITUDE, $LONGITUDE" # A localização pode ser definida pela latitude e longitude

# Verificando se a API retornou um erro
if [ $? -ne 0 ]; then
    echo "Erro ao obter informações do clima."
    exit 1
fi

# Exibindo os resultados
echo "$SAUDACAO!"
echo "Data e Hora: $DATA_HORA"
echo "Localização: $LOCALIZACAO"
echo "Temperatura: $TEMP °C"
