#!/bin/bash

# Função para obter a lista de APIs públicas
function get_public_apis() {
    echo "### Listando APIs Públicas ###"
    response=$(curl -s https://api.publicapis.org/entries)
    if [[ $? -ne 0 || -z $response ]]; then
        echo "Erro ao acessar a API de Public APIs."
    else
        echo "$response" | jq '.entries[] | {API: .API, Description: .Description, Link: .Link}' | head -n 10
    fi
    echo
}

# Função para obter informações sobre países
function get_countries_info() {
    echo "### Informações sobre Países ###"
    response=$(curl -s https://restcountries.com/v3.1/all)
    if [[ $? -ne 0 || -z $response ]]; then
        echo "Erro ao acessar a API de REST Countries."
    else
        echo "$response" | jq '.[] | {Name: .name.common, Capital: .capital, Population: .population, Area: .area, Languages: .languages, Flag: .flags.svg}' | head -n 5
    fi
    echo
}

# Função para obter a hora atual de São Paulo
function get_time_in_sao_paulo() {
    echo "### Hora Atual em São Paulo ###"
    response=$(curl -s http://worldtimeapi.org/api/timezone/America/Sao_Paulo)
    if [[ $? -ne 0 || -z $response ]]; then
        echo "Erro ao acessar a API WorldTimeAPI."
    else
        echo "$response" | jq '{Datetime: .datetime, Timezone: .timezone, Abbreviation: .abbreviation}'
    fi
    echo
}

# Função para obter as últimas notícias
function get_latest_news() {
    echo "### Últimas Notícias ###"
    response=$(curl -s "https://gnews.io/api/v4/top-headlines?token=YOUR_API_KEY")  # Substitua YOUR_API_KEY
    if [[ $? -ne 0 || -z $response ]]; then
        echo "Erro ao acessar a API GNews."
    else
        echo "$response" | jq '.articles[] | {Title: .title, Description: .description, URL: .url, Source: .source.name}' || echo "Nenhuma notícia disponível."
    fi
    echo
}

# Função para obter uma atividade aleatória
function get_random_activity() {
    echo "### Atividade Aleatória ###"
    response=$(curl -s "https://www.boredapi.com/api/activity/")
    if [[ $? -ne 0 || -z $response ]]; then
        echo "Erro ao acessar a API Bored API."
    else
        echo "$response" | jq '{Activity: .activity, Type: .type}'
    fi
    echo
}

# Executando as funções
get_public_apis
get_countries_info
get_time_in_sao_paulo
get_latest_news
get_random_activity

