from flask import Flask, jsonify, request
from main import get_game_details_v2

app = Flask(__name__)

@app.route('/api/game/<int:game_id>', methods=['GET'])
def api_get_game_details(game_id):
    game_details = get_game_details_v2(game_id)
    if 'error' in game_details:
        # Retourner une réponse d'erreur avec le code HTTP approprié
        error_message = game_details['error']
        # Déterminer le code HTTP basé sur le message d'erreur
        if 'Bad Request' in error_message:
            return jsonify(game_details), 400
        elif 'Unauthorized' in error_message:
            return jsonify(game_details), 401
        elif 'Forbidden' in error_message:
            return jsonify(game_details), 403
        elif 'Not Found' in error_message:
            return jsonify(game_details), 404
        elif 'Too Many Requests' in error_message:
            return jsonify(game_details), 429
        else:
            return jsonify(game_details), 500
    else:
        # Retourner les détails du jeu avec un statut 200
        return jsonify(game_details), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
