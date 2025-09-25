import requests
import re
from transformers import pipeline

# === 1. Configuración ===
API_BASE = "http://127.0.0.1:8000"  # Cambia si tu API corre en otro puerto/servidor
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Posibles intenciones
INTENTS = ["listar", "consultar_por_id", "buscar"]

# === 2. Interpretar la intención ===
def interpretar_intencion(consulta):
    result = classifier(consulta, INTENTS)
    intent = result["labels"][0]  # la más probable
    return intent

# === 3. Ejecutar acción ===
def ejecutar_accion(intent, consulta):
    if intent == "listar":
        resp = requests.get(f"{API_BASE}/registros")
        data = resp.json()
        resumen = data[:5]  # solo mostrar los 5 primeros
        return resumen

    elif intent == "consultar_por_id":
        match = re.search(r"\d+", consulta)
        if not match:
            return "⚠️ No encontré un ID en tu consulta. Por favor especifica uno (ej: 'consulta id 10')."
        record_id = match.group()
        resp = requests.get(f"{API_BASE}/registros/{record_id}")
        if resp.status_code == 404:
            return f"⚠️ No encontré el registro con id {record_id}."
        return resp.json()

    elif intent == "buscar":
        palabras = consulta.split()
        if len(palabras) < 2:
            return "⚠️ Necesito una palabra clave para buscar (ej: 'buscar Kennedy')."
        keyword = palabras[-1]
        resp = requests.get(f"{API_BASE}/buscar", params={"keyword": keyword})
        data = resp.json()
        if not data:
            return f"⚠️ No encontré resultados con la palabra '{keyword}'."
        return data[:5]

    else:
        return "⚠️ No entendí tu consulta. ¿Puedes reformularla?"

# === 4. Loop principal en terminal ===
def main():
    print("🤖 Agente IA conectado. Escribe tu consulta en lenguaje natural.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        consulta = input("Tú: ")
        if consulta.lower() in ["salir", "exit", "quit"]:
            print("👋 Adiós!")
            break

        intent = interpretar_intencion(consulta)
        resultado = ejecutar_accion(intent, consulta)

        print("\nAgente:")
        if isinstance(resultado, list):
            for r in resultado:
                print(f"- {r}")
        else:
            print(resultado)
        print()

if __name__ == "__main__":
    main()
