import os
import json
import math
from flask import Blueprint, jsonify, request, current_app
from functools import cmp_to_key
from datetime import datetime

api_bp = Blueprint('api_bp', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
BLINKS_DIR = os.path.join(DATA_DIR, 'blinks')
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')

# Factor de confianza para el cálculo del interés.
CONFIDENCE_FACTOR = 5

def get_blink_data(blink_id):
    """Lee los datos de un blink desde su archivo JSON."""
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_blink_data(blink_id, data):
    """Guarda los datos de un blink en su archivo JSON."""
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_interest(blink):
    """Calcula el porcentaje de interés de un blink usando la fórmula revisada."""
    positive_votes = blink.get('positive_votes', 0)
    negative_votes = blink.get('negative_votes', 0)

    total_votes = positive_votes + negative_votes
    net_vote_difference = positive_votes - negative_votes

    if total_votes == 0:
        return 0.0

    interest = (net_vote_difference / (total_votes + CONFIDENCE_FACTOR)) * 100.0
    return interest

def compare_blinks(item1, item2):
    """Función de comparación para ordenar los blinks según las reglas especificadas."""
    # Criterio Principal: Ordenar por 'interest' de forma DESCENDENTE.
    if item1['interest'] > item2['interest']:
        return -1
    if item1['interest'] < item2['interest']:
        return 1

    # Si hay empate en 'interest', aplicar criterios secundarios.
    # Regla A (Noticias sin votos): Interés 0, 0 positivos, 0 negativos
    is_item1_unvoted = item1['positive_votes'] == 0 and item1['negative_votes'] == 0
    is_item2_unvoted = item2['positive_votes'] == 0 and item2['negative_votes'] == 0

    if is_item1_unvoted and is_item2_unvoted:
        # Ordenar por fecha de publicación DESCENDENTE (más recientes primero)
        date1 = datetime.fromisoformat(item1['publication_date'].replace('Z', '+00:00'))
        date2 = datetime.fromisoformat(item2['publication_date'].replace('Z', '+00:00'))
        return -1 if date1 > date2 else 1

    # Regla B (Noticias con 0 positivos y >0 negativos)
    is_item1_rule_b = item1['positive_votes'] == 0 and item1['negative_votes'] > 0
    is_item2_rule_b = item2['positive_votes'] == 0 and item2['negative_votes'] > 0

    if is_item1_rule_b and is_item2_rule_b:
        # Ordenar por Votos Negativos de forma ASCENDENTE
        # (las que tienen menos votos negativos aparecerán primero en este subgrupo)
        return item1['negative_votes'] - item2['negative_votes']

    # Desempate general por fecha si las otras reglas no aplican
    date1 = datetime.fromisoformat(item1['publication_date'].replace('Z', '+00:00'))
    date2 = datetime.fromisoformat(item2['publication_date'].replace('Z', '+00:00'))
    return -1 if date1 > date2 else 1

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    """Obtiene todos los blinks, calcula su interés y los ordena."""
    try:
        all_blinks = []
        for filename in os.listdir(BLINKS_DIR):
            if filename.endswith('.json'):
                blink_id = filename.split('.')[0]
                blink_data = get_blink_data(blink_id)
                if blink_data:
                    # Asegurar que los contadores de votos existen
                    blink_data.setdefault('positive_votes', 0)
                    blink_data.setdefault('negative_votes', 0)
                    # Calcular y añadir el interés a cada blink
                    blink_data['interest'] = calculate_interest(blink_data)
                    all_blinks.append(blink_data)

        # Ordenar la lista de blinks usando la función de comparación personalizada
        sorted_blinks = sorted(all_blinks, key=cmp_to_key(compare_blinks))

        # Defensive check to ensure 'interest' is present and valid before jsonify
        for blink_item in sorted_blinks: # Changed loop variable name to avoid conflict if 'blink' is used above
            if 'interest' not in blink_item or not isinstance(blink_item.get('interest'), (int, float)) or not math.isfinite(blink_item.get('interest', float('nan'))):
                current_app.logger.warning(
                    f"Blink {blink_item.get('id', 'Unknown ID')} missing, invalid, or non-finite interest before jsonify. Recalculating."
                )
                # Ensure positive_votes and negative_votes are present, defaulting to 0
                blink_item.setdefault('positive_votes', 0)
                blink_item.setdefault('negative_votes', 0)
                # Recalculate interest
                blink_item['interest'] = calculate_interest(blink_item)

        # Aggressively ensure 'interest' is a float for all items
        for blink_to_serialize in sorted_blinks:
            blink_to_serialize.setdefault('positive_votes', 0)
            blink_to_serialize.setdefault('negative_votes', 0)
            calculated_float_interest = float(calculate_interest(blink_to_serialize)) # Explicitly cast to float
            blink_to_serialize['interest'] = calculated_float_interest

        # Optional: Log a sample of blinks right before jsonify for final backend state verification
        if sorted_blinks: # Check if list is not empty
            sample_size = min(3, len(sorted_blinks))
            sample_blinks_for_log = []
            for i in range(sample_size):
                blink_sample = sorted_blinks[i]
                sample_blinks_for_log.append({
                    "id": blink_sample.get("id"),
                    "interest": blink_sample.get("interest"),
                    "type_of_interest": str(type(blink_sample.get("interest")))
                })
            current_app.logger.info(f"Sample of blinks before jsonify: {sample_blinks_for_log}")

        return jsonify(sorted_blinks)
    except Exception as e:
        current_app.logger.error(f"Error fetching blinks: {e}")
        return jsonify({"error": "Failed to fetch blinks"}), 500

@api_bp.route('/blink/<string:id>/vote', methods=['POST'])
def vote_blink(id):
    """Procesa un voto para un blink específico."""
    try:
        data = request.get_json()
        vote_type = data.get('vote_type')
        previous_vote_status = data.get('previous_vote_status') # Puede ser 'positive', 'negative', o null

        if vote_type not in ['positive', 'negative']:
            return jsonify({"error": "Invalid vote type"}), 400

        blink_data = get_blink_data(id)
        if not blink_data:
            return jsonify({"error": "Blink not found"}), 404

        # Asegurar que los contadores de votos existen y tienen valor por defecto
        blink_data.setdefault('positive_votes', 0)
        blink_data.setdefault('negative_votes', 0)

        # Si el usuario hace clic en el mismo voto, no hacer nada. (Esto se maneja en frontend, pero una doble verificación aquí es buena)
        # Esta lógica asume que el frontend envía el estado *antes* del nuevo voto.
        # Si el nuevo voto es el mismo que el estado anterior, teóricamente no debería llegar aquí si el frontend lo maneja.
        # Sin embargo, la lógica de ajuste de votos debe considerar el estado *actual* del backend.

        if vote_type == 'positive':
            if previous_vote_status == 'positive': # Clic en positivo cuando ya era positivo (quitar voto)
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
            elif previous_vote_status == 'negative': # Cambiar de negativo a positivo
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
                blink_data['positive_votes'] += 1
            else: # Voto positivo por primera vez
                blink_data['positive_votes'] += 1
        elif vote_type == 'negative':
            if previous_vote_status == 'negative': # Clic en negativo cuando ya era negativo (quitar voto)
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
            elif previous_vote_status == 'positive': # Cambiar de positivo a negativo
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
                blink_data['negative_votes'] += 1
            else: # Voto negativo por primera vez
                blink_data['negative_votes'] += 1

        save_blink_data(id, blink_data)
        # Devolver el blink actualizado con su nuevo interés para consistencia, aunque el frontend recargará todo.
        blink_data['interest'] = calculate_interest(blink_data)
        return jsonify(blink_data)

    except Exception as e:
        current_app.logger.error(f"Error processing vote for blink {id}: {e}")
        return jsonify({"error": "Failed to process vote"}), 500

@api_bp.route('/blink/<string:id>/details', methods=['GET'])
def get_blink_details(id):
    """Obtiene los detalles de un blink específico y su artículo asociado."""
    try:
        blink_data = get_blink_data(id)
        if not blink_data:
            return jsonify({"error": "Blink not found"}), 404

        # Calcular y añadir el interés al blink
        blink_data['interest'] = calculate_interest(blink_data)

        article_file_path = os.path.join(ARTICLES_DIR, f"{id}.json")
        if not os.path.exists(article_file_path):
            # Si no hay artículo, devolver solo la info del blink con su interés
            return jsonify(blink_data)

        with open(article_file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)

        # Combinar datos del blink y del artículo
        detailed_blink = {**blink_data, "article_content": article_data}

        return jsonify(detailed_blink)
    except Exception as e:
        current_app.logger.error(f"Error fetching blink detail for {id}: {e}")
        return jsonify({"error": "Failed to fetch blink details"}), 500
