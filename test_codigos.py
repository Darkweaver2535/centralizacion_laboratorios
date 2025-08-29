#!/usr/bin/env python3
"""
Script de prueba para verificar generación de códigos únicos
"""

import time

class TestCodigos:
    def __init__(self):
        self.contador = 0
        
    def generar_codigo_unico(self):
        """Genera un código de inventario único usando contador incremental"""
        self.contador += 1
        timestamp = int(time.time())
        return f"INS_{timestamp}_{self.contador:04d}"

# Probar generación de códigos
test = TestCodigos()
codigos = []

print("Generando 10 códigos de prueba:")
for i in range(10):
    codigo = test.generar_codigo_unico()
    codigos.append(codigo)
    print(f"{i+1}: {codigo}")

print(f"\n¿Hay códigos duplicados? {len(codigos) != len(set(codigos))}")
print(f"Códigos únicos: {len(set(codigos))}")
print(f"Total códigos: {len(codigos)}")
