# review_code.py
import os
import sys
import requests # Necesitarás instalar esta librería

def get_code_review_from_model(code_diff, model_name, github_token):
    """
    Envía el 'diff' de código a un modelo de GitHub Models para obtener una revisión.
    """
    if not github_token:
        raise ValueError("El token de acceso de GitHub (GH_MODELS_TOKEN) no está configurado.")

    # El endpoint de la API de GitHub Models tiene este formato.
    # Debes reemplazar 'MODEL_NAME' por el identificador del modelo que elegiste.
    # Por ejemplo: 'deepseek/deepseek-coder-6.7b-instruct'
    api_url = f"https://api.github.com/models/{model_name}/completions"

    # Este es el 'prompt' que le indica al modelo cómo actuar.
    # Es muy similar al que se usa en el proyecto de la librería inteligente [5, 6].
    prompt = (
        "Actúa como un revisor de código experto en Python. "
        "Analiza los siguientes cambios de código (diff) y proporciona sugerencias concisas y útiles. "
        "Enfócate en posibles errores, mejoras de estilo y buenas prácticas. "
        "Si no hay nada que sugerir, simplemente di 'El código se ve bien'.\n\n"
        "--- DIFF ---\n"
        f"{code_diff}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }

    # El cuerpo de la solicitud (payload) con el prompt y los parámetros.
    # Puedes ajustar 'max_tokens' o 'temperature' como en el Playground de GitHub Models.
    data = {
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.2,
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Lanza un error si la respuesta es 4xx o 5xx
        
        # Extraemos la respuesta del modelo del JSON que devuelve la API.
        # La estructura exacta puede variar un poco, pero usualmente está en 'choices'.
        review = response.json().get("choices", [{}]).get("text", "No se pudo obtener una respuesta del modelo.")
        return review

    except requests.exceptions.RequestException as e:
        return f"Error al contactar la API de GitHub Models: {e}"

if __name__ == "__main__":
    # El código 'diff' se pasa como un argumento desde el archivo .yml
    diff_content = sys.argv[1]
    
    # El nombre del modelo que quieres usar. ¡Cámbialo por el de tu prototipo!
    # Puedes encontrarlo en github.com/marketplace/models [7].
    MODEL_TO_USE = "deepseek/deepseek-coder-6.7b-instruct" # <-- CAMBIA ESTO

    # El token se lee desde los secretos de la GitHub Action.
    token = os.environ.get("GH_MODELS_TOKEN")

    review_comment = get_code_review_from_model(diff_content, MODEL_TO_USE, token)
    
    print(review_comment)
