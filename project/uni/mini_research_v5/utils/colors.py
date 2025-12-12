"""
Sistema de cores padronizado
"""

def color(text: str, code: str) -> str:
    """Aplica código de cor ANSI ao texto"""
    return f"\033[{code}m{text}\033[0m"

def blue(text: str) -> str:
    """Progresso, informações"""
    return color(text, "34")

def green(text: str) -> str:
    """Sucesso, índices, destaques, ratings, checkmarks"""
    return color(text, "32")

def yellow(text: str) -> str:
    """Avisos, alertas"""
    return color(text, "33")

def red(text: str) -> str:
    """Erros, falhas"""
    return color(text, "31")

def gray(text: str) -> str:
    """Valores secundários, números, links, metadados, descrições"""
    return color(text, "90")

def cyan(text: str) -> str:
    """Informações especiais"""
    return color(text, "36")

def bold(text: str) -> str:
    """Texto em negrito"""
    return color(text, "1")

def magenta(text: str) -> str:
    """Destaques especiais"""
    return color(text, "35")


