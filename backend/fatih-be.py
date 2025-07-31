
import pymysql
import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

def get_db_connection():
    db = pymysql.connect(
        host="localhost",
        user="root",
        passwd="Ylmzxfatih12355",
        database="stajDB",
        cursorclass=pymysql.cursors.DictCursor
    )
    return db

@app.route('/users', methods=['GET'])
def get_users():
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            for user in users:
                print(f"Kullanıcı ID: {user['id']} | Created at: {user['created_at']}")
        db.close()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/users', methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        print("Gelen JSON veri:", data) 
        firstName = data.get('firstName', '').strip()
        lastName = data.get('lastName', '').strip()
        email = data.get('email', '').strip()

        if not firstName or not lastName or not email:
            return jsonify({"error": "Eksik alan var"}), 400

        if not firstName.isalpha() or not lastName.isalpha():
            return jsonify({"error": "Ad ve soyad sadece harf içermelidir."}), 400

        if len(firstName) < 2 or len(lastName) < 2:
            return jsonify({"error": "Ad ve soyad bir harften uzun olmalıdır."}), 400
        
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Geçerli bir e-posta adresi girin."}), 400

        db = get_db_connection()
        with db.cursor() as cursor:
            check_sql = "SELECT COUNT(*) FROM users WHERE email = %s"
            cursor.execute(check_sql, (email,))
            result = cursor.fetchone()
            if result and list(result.values())[0] > 0:
                db.close()
                return jsonify({"error": "Bu email zaten kayıtlı!"}), 409
            sql = "INSERT INTO users (firstName, lastName, email, created_at) VALUES(%s, %s, %s, NOW())"
            cursor.execute(sql, (firstName, lastName, email))
            db.commit()
        db.close()

        return jsonify({"message": "Kullanıcı eklendi."}), 201
    except Exception as e:
        print("=== HATA BAŞLANGICI ===")
        traceback.print_exc()
        print("=== HATA BİTİŞİ ===")
        return jsonify({"error": str(e), "type": type(e).__name__ }), 500

@app.route('/users/<int:id>', methods=["DELETE"])
def delete_user(id):
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            sql = "DELETE FROM users WHERE id=%s "
            cursor.execute(sql, (id,))
            db.commit()
        db.close()

        return jsonify({"message":"Kullanıcı başarıyla silindi."})
    
    except Exception as e:
        print("=== HATA BAŞLANGICI ===")
        traceback.print_exc()
        print("=== HATA BİTİŞİ ===")
        return jsonify({"error": str(e)}), 500
    
@app.route('/users/<int:id>', methods=["PUT"])
def update_user(id):
    try:
        data = request.get_json()
        firstName = data.get("firstName", "").strip()
        lastName = data.get("lastName", "").strip()
        email = data.get("email", "").strip()

        if not firstName or not lastName or not email:
            return jsonify({"error": "Eksik alan var"}), 400
        
        if not firstName.isalpha() or not lastName.isalpha():
            return jsonify({"error": "Ad ve soyad sadece harf içermelidir."}), 400
        
        if len(firstName) < 2 or len(lastName) < 2:
            return jsonify({"error": "Ad ve soyad bir harften uzun olmalıdır."}), 400
        
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Geçerli bir e-posta adresi girin."}), 400

        db = get_db_connection()
        with db.cursor() as cursor:
            sql = """
                UPDATE users
                SET firstName=%s, lastName=%s, email=%s, created_at=NOW()
                WHERE id=%s
            """
            cursor.execute(sql, (firstName, lastName, email, id))
            db.commit()
        db.close()

        return jsonify({"message": "Kullanıcı güncellendi."}), 200
    
    except Exception as e:
        print("=== HATA BAŞLANGICI ===")
        traceback.print_exc()
        print("=== HATA BİTİŞİ ===")
        return jsonify({"error": str(e)}), 500

def create_users_table_if_exists():
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    firstName VARCHAR(55) NOT NULL,
                    lastName VARCHAR(55) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        db.commit()
        db.close()
        print("Tablo oluşturuldu.")
    except:
        print("Tablo oluşturulamadı!!!")
        traceback.print_exc()        

if __name__ == "__main__":
    create_users_table_if_exists()
    app.run(debug=True)