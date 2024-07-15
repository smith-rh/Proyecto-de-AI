from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os
import datetime
from key import clave

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    QUERY_SAVE_PATH = 'queries'  # Ruta relativa

app = Flask(__name__)
app.config.from_object(Config)

genai.configure(api_key=clave)
model = genai.GenerativeModel(model_name="gemini-pro")

# Productos de ejemplo en la tienda con precios y descripciones detalladas
PRODUCTOS = {
    "iPhone 13": {
        "descripcion": "El último iPhone con tecnología avanzada.",
        "precio": "$799"
    },
    "iPhone 12": {
        "descripcion": "Un gran teléfono con muchas características.",
        "precio": "$699"
    },
    "iPhone SE": {
        "descripcion": "Un iPhone asequible con un gran rendimiento.",
        "precio": "$399"
    }
}

def save_response(question, response, vision_response=None):
    if not os.path.exists(app.config['QUERY_SAVE_PATH']):
        os.makedirs(app.config['QUERY_SAVE_PATH'])

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}.txt"
    filepath = os.path.join(app.config['QUERY_SAVE_PATH'], filename)

    with open(filepath, 'w') as f:
        f.write(f"Question: {question}\n\nResponse: {response}\n")
        if vision_response:
            f.write(f"\nVision Response: {vision_response}\n")

def get_product_recommendations(query):
    recommendations = []
    for product, details in PRODUCTOS.items():
        if product.lower() in query.lower() or any(word in query.lower() for word in product.lower().split()):
            recommendations.append(f"{product}: {details['descripcion']} - Precio: {details['precio']}")
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    specific_question = f"Marketing strategy for iPhone: {question}"

    try:
        response = model.generate_content(specific_question)
        response_text = response.text

        # Generar recomendaciones de productos basadas en la consulta
        recommendations = get_product_recommendations(question)

        # If you want to use gemini-pro-vision or another model, you can include it here.
        # For example, if there is an image processing aspect to the question:
        # vision_response = vision_model.some_method(specific_question)

        # Example placeholder for vision response
        vision_response = None

        save_response(specific_question, response_text, vision_response)
        return jsonify({'response': response_text, 'vision_response': vision_response, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
