#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes unitários básicos para uni_v7.4.py
"""

import unittest
import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulos do uni_v7.4
try:
    from uni_v7_4 import (
        DataValidator,
        sanitize_term,
        sanitize_filename,
        validate_url,
        APIKeyRotator
    )
except ImportError:
    # Tentar importar do arquivo principal
    import importlib.util
    spec = importlib.util.spec_from_file_location("uni_v7_4", "uni_v7.4.py")
    uni_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(uni_module)
    DataValidator = uni_module.DataValidator
    sanitize_term = uni_module.DataValidator.sanitize_term
    sanitize_filename = uni_module.DataValidator.sanitize_filename
    validate_url = uni_module.DataValidator.validate_url
    APIKeyRotator = uni_module.APIKeyRotator


class TestDataValidator(unittest.TestCase):
    """Testes para DataValidator"""
    
    def test_validate_url_valid(self):
        """Testa validação de URLs válidas"""
        valid_urls = [
            "https://www.example.com",
            "http://example.com/path",
            "https://subdomain.example.com:8080/path?query=value"
        ]
        for url in valid_urls:
            self.assertTrue(DataValidator.validate_url(url), f"URL deveria ser válida: {url}")
    
    def test_validate_url_invalid(self):
        """Testa validação de URLs inválidas"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            ""
        ]
        for url in invalid_urls:
            self.assertFalse(DataValidator.validate_url(url), f"URL deveria ser inválida: {url}")
    
    def test_sanitize_term_safe(self):
        """Testa sanitização de termos seguros"""
        safe_terms = [
            "bitcoin",
            "cryptocurrency market",
            "teste 123",
            "análise de dados"
        ]
        for term in safe_terms:
            sanitized = DataValidator.sanitize_term(term)
            self.assertIsInstance(sanitized, str)
            self.assertTrue(len(sanitized) > 0)
    
    def test_sanitize_term_dangerous(self):
        """Testa sanitização de termos perigosos"""
        dangerous_terms = [
            "<script>alert('xss')</script>",
            "test; rm -rf /",
            "../../etc/passwd",
            "javascript:void(0)"
        ]
        for term in dangerous_terms:
            sanitized = DataValidator.sanitize_term(term)
            # Verificar que caracteres perigosos foram removidos
            self.assertNotIn("<script>", sanitized.lower())
            self.assertNotIn("javascript:", sanitized.lower())
            self.assertNotIn("../", sanitized)
    
    def test_sanitize_term_length(self):
        """Testa truncamento de termos longos"""
        long_term = "a" * 300
        sanitized = DataValidator.sanitize_term(long_term, max_length=200)
        self.assertLessEqual(len(sanitized), 200)
    
    def test_sanitize_filename(self):
        """Testa sanitização de nomes de arquivo"""
        test_cases = [
            ("normal_file.csv", "normal_file.csv"),
            ("file with spaces.csv", "file_with_spaces.csv"),
            ("file/with/slashes.csv", "file_with_slashes.csv"),
            ("file<>with|special.csv", "file__with_special.csv")
        ]
        for input_name, expected_pattern in test_cases:
            sanitized = DataValidator.sanitize_filename(input_name)
            # Verificar que não contém caracteres perigosos
            self.assertNotIn("/", sanitized)
            self.assertNotIn("\\", sanitized)
            self.assertNotIn("<", sanitized)
            self.assertNotIn(">", sanitized)


class TestAPIKeyRotator(unittest.TestCase):
    """Testes para APIKeyRotator"""
    
    def test_register_and_get_key(self):
        """Testa registro e obtenção de keys"""
        rotator = APIKeyRotator()
        keys = ["key1", "key2", "key3"]
        rotator.register_keys("test_service", keys)
        
        # Deve retornar keys em ordem
        retrieved = [rotator.get_key("test_service") for _ in range(6)]
        # Verificar que todas as keys foram usadas
        self.assertIn("key1", retrieved)
        self.assertIn("key2", retrieved)
        self.assertIn("key3", retrieved)
    
    def test_mark_failed_key(self):
        """Testa marcação de key como falha"""
        rotator = APIKeyRotator()
        keys = ["key1", "key2", "key3"]
        rotator.register_keys("test_service", keys)
        
        # Marcar key1 como falha
        rotator.mark_failed("test_service", "key1")
        
        # Próximas keys não devem incluir key1
        retrieved = [rotator.get_key("test_service") for _ in range(4)]
        self.assertNotIn("key1", retrieved)
    
    def test_reset_failures(self):
        """Testa reset de keys marcadas como falhas"""
        rotator = APIKeyRotator()
        keys = ["key1", "key2"]
        rotator.register_keys("test_service", keys)
        
        rotator.mark_failed("test_service", "key1")
        rotator.reset_failures("test_service")
        
        # Agora key1 deve estar disponível novamente
        retrieved = rotator.get_key("test_service")
        self.assertIn(retrieved, keys)


class TestInputSanitization(unittest.TestCase):
    """Testes para sanitização de inputs"""
    
    def test_sanitize_input_term(self):
        """Testa sanitização de input tipo term"""
        dangerous_input = "<script>alert('xss')</script>test"
        sanitized = DataValidator.validate_and_sanitize_input(dangerous_input, "term")
        self.assertNotIn("<script>", sanitized.lower())
        self.assertIn("test", sanitized)
    
    def test_sanitize_input_filename(self):
        """Testa sanitização de input tipo filename"""
        dangerous_input = "../../etc/passwd"
        sanitized = DataValidator.validate_and_sanitize_input(dangerous_input, "filename")
        self.assertNotIn("../", sanitized)
        self.assertNotIn("/", sanitized)


if __name__ == '__main__':
    unittest.main()


