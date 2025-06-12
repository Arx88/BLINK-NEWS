#!/usr/bin/env python3
"""
Script de prueba para verificar la integración con OLLAMA
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.topic_searcher import TopicSearcher
from models.superior_note_generator import SuperiorNoteGenerator
import ollama

def test_ollama_connection():
    """Prueba la conexión con OLLAMA"""
    try:
        client = ollama.Client(host='http://localhost:11434')
        
        # Verificar que el modelo llama3 esté disponible
        models = client.list()
        llama3_available = any('llama3' in model['name'] for model in models['models'])
        
        if not llama3_available:
            print("❌ Modelo llama3 no encontrado. Ejecute: ollama pull llama3")
            return False
        
        # Hacer una prueba simple
        response = client.chat(model='llama3', messages=[
            {'role': 'user', 'content': 'Responde solo con "OK" si puedes leer esto.'}
        ])
        
        if 'OK' in response['message']['content']:
            print("✅ OLLAMA funcionando correctamente")
            return True
        else:
            print("⚠️ OLLAMA responde pero de forma inesperada")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con OLLAMA: {e}")
        print("Asegúrese de que OLLAMA esté ejecutándose en localhost:11434")
        return False

def test_topic_searcher():
    """Prueba el buscador de temas"""
    try:
        searcher = TopicSearcher()
        print("✅ TopicSearcher inicializado correctamente")
        
        # Prueba básica de extracción de palabras clave
        keywords = searcher._extract_keywords("Argentina elecciones presidenciales 2023")
        print(f"✅ Extracción de palabras clave: {keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en TopicSearcher: {e}")
        return False

def test_superior_note_generator():
    """Prueba el generador de notas superiores"""
    try:
        generator = SuperiorNoteGenerator()
        print("✅ SuperiorNoteGenerator inicializado correctamente")
        
        # Crear datos de prueba
        test_articles = [
            {
                'source': 'Fuente 1',
                'title': 'Noticia de prueba sobre Argentina',
                'url': 'https://example.com/1',
                'summary': 'Esta es una noticia de prueba sobre Argentina para verificar el funcionamiento del sistema.'
            },
            {
                'source': 'Fuente 2', 
                'title': 'Otra perspectiva sobre Argentina',
                'url': 'https://example.com/2',
                'summary': 'Esta es otra perspectiva sobre el mismo tema para probar la generación de notas superiores.'
            }
        ]
        
        # Probar generación de título
        title = generator._generate_main_title(test_articles, "Argentina")
        print(f"✅ Generación de título: {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en SuperiorNoteGenerator: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de integración con OLLAMA\n")
    
    tests = [
        ("Conexión con OLLAMA", test_ollama_connection),
        ("TopicSearcher", test_topic_searcher),
        ("SuperiorNoteGenerator", test_superior_note_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Probando {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 Todas las pruebas pasaron. El sistema está listo para usar.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revise los errores arriba.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

