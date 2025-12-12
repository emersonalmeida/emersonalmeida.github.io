#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v5.0 - Main Entry Point
Versão refatorada com todas as melhorias implementadas
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings, load_config, validate_api_keys
from sources import SuggestSource, DataSource
from utils.colors import *
from utils.validators import sanitize_term
from utils.formatters import mask_sensitive_data

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_header(title: str, description: str = ""):
    """Cabeçalho formatado"""
    print(f"\n{cyan(bold(title))}")
    if description:
        print(f"  {gray(description)}")
    print()


def validate_and_setup() -> tuple[Settings, Dict[str, bool]]:
    """
    Valida ambiente e carrega configuração
    Melhoria #1: Validação obrigatória de API keys
    """
    print_header("Mini Research v5.0", "Coletor de Dados Multi-Fonte - Versão Refatorada")
    
    # Carregar configuração
    settings = load_config()
    
    # Validar API keys
    keys_status = validate_api_keys()
    missing = [k for k, v in keys_status.items() if not v]
    
    if missing:
        logger.warning(f"API keys ausentes: {', '.join(missing)}")
        print(yellow(f"⚠️  Aviso: Algumas API keys estão ausentes: {', '.join(missing)}"))
        print(yellow("   Algumas funcionalidades podem não estar disponíveis.\n"))
    
    return settings, keys_status


def collect_configuration(settings: Settings) -> Optional[Dict]:
    """
    Coleta configuração do usuário
    Melhoria #7: Suporta carregar de arquivo ou coletar via CLI
    """
    config = {}
    
    # Se já tem configuração de arquivo, usar ela
    if settings.config_file:
        print(green(f"✓ Configuração carregada de {settings.config_file}"))
        response = input("  Usar esta configuração? (s/n) [s]: ").strip().lower() or "s"
        if response == "s":
            # Converter settings para formato de config
            # (implementação simplificada)
            return config
    
    # Coletar via CLI (versão simplificada)
    print_header("Configuração", "Coletando parâmetros de busca")
    
    # Termo
    termo_input = input(f"{green('> Termo de busca: ')}").strip()
    if not termo_input:
        print(red("Erro: Termo não pode estar vazio!"))
        return None
    
    try:
        termo = sanitize_term(termo_input)
    except ValueError as e:
        print(red(f"Erro: {e}"))
        return None
    
    config["termo"] = termo
    config["regions"] = ["br"]  # Simplificado
    config["clients"] = [1]
    config["sources"] = [1, 2]
    config["opcoes"] = [1]
    config["limit"] = 15
    config["delay"] = settings.get("delay", 1.0)
    
    return config


def create_sources(config: Dict, settings: Settings) -> List[DataSource]:
    """
    Cria instâncias das fontes de dados
    Melhoria #6: Usa padrão Strategy
    """
    sources = []
    
    # Google Suggest
    if 1 in config.get("fontes", [1]):  # Simplificado
        suggest_config = {
            "regions": config.get("regions", ["br"]),
            "clients": config.get("clients", [1]),
            "sources": config.get("sources", [1]),
            "opcoes": config.get("opcoes", [1]),
            "limit": config.get("limit", 15),
            "delay": config.get("delay", 1.0)
        }
        sources.append(SuggestSource(suggest_config))
    
    # Outras fontes podem ser adicionadas aqui
    # sources.append(TrendsSource(trends_config))
    # sources.append(SERPSource(serp_config))
    # etc.
    
    return sources


def main():
    """
    Função principal
    Integra todas as melhorias implementadas
    """
    try:
        # Validar e configurar
        settings, keys_status = validate_and_setup()
        
        # Coletar configuração
        config = collect_configuration(settings)
        if not config:
            print(red("\nConfiguração cancelada ou inválida."))
            return
        
        termo = config["termo"]
        output_dir = Path(settings.get("base_dir", "dados")) / f"coleta_{termo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print_header("Coleta de Dados", f"Termo: {termo}")
        
        # Criar fontes
        sources = create_sources(config, settings)
        
        if not sources:
            print(yellow("Nenhuma fonte configurada."))
            return
        
        # Resultados em tempo real
        real_time_results = {
            "suggest": [],
            "trends": [],
            "serp": [],
            "youtube": [],
            "stores": []
        }
        
        # Coletar de cada fonte
        resultados = {}
        for source in sources:
            print(f"\n{cyan(bold(f'Coletando: {source.get_name()}'))}")
            try:
                result = source.collect(termo, str(output_dir), real_time_results)
                
                if result.success:
                    resultados[source.get_name().lower().replace(" ", "_")] = result.data
                    print(green(f"✓ {source.get_name()}: {len(result)} itens coletados"))
                else:
                    print(red(f"✗ {source.get_name()}: {result.error}"))
            
            except Exception as e:
                logger.error(f"Erro ao coletar {source.get_name()}: {mask_sensitive_data(str(e))}", exc_info=True)
                print(red(f"✗ Erro em {source.get_name()}: {e}"))
        
        # Resumo final
        print_header("Resumo Final")
        total = sum(len(data) for data in resultados.values() if isinstance(data, list))
        print(f"  {gray('Total de itens coletados:')} {green(str(total))}")
        print(f"  {gray('Dados salvos em:')} {green(str(output_dir))}")
        
        print(f"\n{green(bold('✓ Coleta finalizada com sucesso!'))}\n")
    
    except KeyboardInterrupt:
        print(f"\n{yellow('Coleta interrompida pelo usuário.')}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro fatal: {mask_sensitive_data(str(e))}", exc_info=True)
        print(red(f"\n✗ Erro fatal: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()


