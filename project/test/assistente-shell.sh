#!/bin/bash

# Coloque sua chave de API aqui
API_KEY="SUA_CHAVE_DE_API"

# Função para exibir a previsão do tempo
get_weather() {
    read -p "Digite o nome da cidade: " city
    response=$(curl -s "https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric")

    if [ $(echo "$response" | jq '.cod') -ne 200 ]; then
        echo "Erro ao obter dados: $(echo "$response" | jq '.message')"
        return
    fi

    # Extraindo informações
    weather=$(echo "$response" | jq '.weather[0].description')
    temperature=$(echo "$response" | jq '.main.temp')
    humidity=$(echo "$response" | jq '.main.humidity')
    wind_speed=$(echo "$response" | jq '.wind.speed')

    # Exibindo resultados
    echo "Previsão do Tempo em $city:"
    echo "Descrição: $weather"
    echo "Temperatura: $temperature°C"
    echo "Umidade: $humidity%"
    echo "Velocidade do Vento: $wind_speed m/s"
}

# Executar a função
get_weather

