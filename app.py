from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import os

app = Flask(__name__)
CORS(app)

# Configurar la clave de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("La clave de OpenAI no está configurada. Establece la variable de entorno 'OPENAI_API_KEY'.")

# Endpoint para obtener la transcripción del video
@app.route('/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.get_json()
        video_url = data.get("url", "")

        if not video_url:
            return jsonify({"error": "No se proporcionó la URL del video"}), 400

        # Extraer el ID del video de la URL
        video_id = video_url.split("v=")[1].split("&")[0]

        # Obtener la transcripción en español (si está disponible)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])

        # Convertir la transcripción a texto
        transcript_text = " ".join([t['text'] for t in transcript])

        return jsonify({"transcript": transcript_text})

    except Exception as e:
        return jsonify({"error": f"Error al obtener la transcripción: {str(e)}"}), 500

# Endpoint para generar un resumen del texto
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        text_to_summarize = data.get("text", "")

        if not text_to_summarize:
            return jsonify({"error": "No se proporcionó texto para resumir"}), 400

        # Llamar a la API de OpenAI para generar el resumen
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en generar resúmenes claros y concisos."},
                {"role": "user", "content": f"Por favor, resume el siguiente texto:\n\n{text_to_summarize}"}
            ]
        )

        # Acceder al contenido del mensaje de respuesta
        summary = response['choices'][0]['message']['content'].strip()
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": f"Error al generar el resumen: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
