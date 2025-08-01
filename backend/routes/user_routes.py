from flask import Blueprint, request, jsonify
from db.mysql_connection import get_db_connection
import traceback
import re

ALLOWED_TEAMS = ['Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'SAMSUNSPOR', 'trabzonspor']

#uygulamandaki yönlendirme (routing) ve işlevlerin gruplanmasını sağlar.
user_routes = Blueprint("user_routes", __name__)

@user_routes.route('/init-db', methods=['GET'])
def create_users_table_if_not_exists():
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    firstName VARCHAR(55) NOT NULL,
                    lastName VARCHAR(55) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    team VARCHAR(50) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        db.commit()
        db.close()
        return jsonify({"message": "Tablo oluşturuldu."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@user_routes.route('/users', methods=['GET'])
def get_users():
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        db.close()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 #Sunucu tarafında bir hata olduğunu belirtir.

@user_routes.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        firstName = data.get('firstName', '').strip()
        lastName = data.get('lastName', '').strip()
        email = data.get('email', '').strip()
        team = data.get('team', '').strip()

        if not firstName or not lastName or not email or not team:
            return jsonify({"error": "Eksik alan var"}), 400 #İstemci (kullanıcı) hatalı veya eksik veri göndermiştir.
        if not firstName.isalpha() or not lastName.isalpha():
            return jsonify({"error": "Ad ve soyad sadece harf içermelidir."}), 400
        if len(firstName) < 2 or len(lastName) < 2:
            return jsonify({"error": "Ad ve soyad bir harften uzun olmalıdır."}), 400
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Geçerli bir e-posta adresi girin."}), 400
        if team not in ALLOWED_TEAMS:
            return jsonify({"error": "Lütfen bir takım seçiniz."}), 400
        
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result and list(result.values())[0] > 0:
                db.close()
                return jsonify({"error": "Bu email zaten kayıtlı!"}), 409 #çakışma var.
            cursor.execute("INSERT INTO users (firstName, lastName, email, team, created_at) VALUES(%s, %s, %s, %s, NOW())",
                           (firstName, lastName, email))
            db.commit()
        db.close()
        return jsonify({"message": "Kullanıcı eklendi."}), 201 #oluşturuldu.

    except Exception as e:
        traceback.print_exc() #loglarda detaylı hata izi tutar.
        return jsonify({"error": str(e), "type": type(e).__name__ }), 500

@user_routes.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        data = request.get_json()
        firstName = data.get("firstName", "").strip()
        lastName = data.get("lastName", "").strip()
        email = data.get("email", "").strip()
        team = data.get('team', '').strip()

        if not firstName or not lastName or not email or not team:
            return jsonify({"error": "Eksik alan var"}), 400
        if team not in ALLOWED_TEAMS:
            return jsonify({"error": "Lütfen bir takım seçin."}), 400
        if not firstName.isalpha() or not lastName.isalpha():
            return jsonify({"error": "Ad ve soyad sadece harf içermelidir."}), 400
        if len(firstName) < 2 or len(lastName) < 2:
            return jsonify({"error": "Ad ve soyad bir harften uzun olmalıdır."}), 400
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Geçerli bir e-posta adresi girin."}), 400

        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET firstName=%s, lastName=%s, email=%s, team=%s, created_at=NOW()
                WHERE id=%s
            """, (firstName, lastName, email, team, id))
            db.commit()
        db.close()
        return jsonify({"message": "Kullanıcı güncellendi."}), 200 #istek başarıyla tamamlandı.

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@user_routes.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id=%s", (id,))
            db.commit()
        db.close()
        return jsonify({"message": "Kullanıcı başarıyla silindi."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@user_routes.route('/alter-table', methods=['GET'])
def add_team_column():
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            # Önce sütun var mı kontrol et
            cursor.execute("SHOW COLUMNS FROM users LIKE 'team'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("ALTER TABLE users ADD COLUMN team VARCHAR(100)")
                db.commit()
                message = "team sütunu eklendi."
            else:
                message = "team sütunu zaten mevcut."
        db.close()
        return jsonify({"message": message})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


