from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
import pymysql
import bcrypt
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__, static_url_path='/static')
CORS(app)

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

def registrar_usuario(nombre_aplica, password_hash, numero_aplica, encoding):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre_aplica, password, numero_aplica, encoding) VALUES (%s, %s, %s, %s)", 
                   (nombre_aplica, password_hash, numero_aplica, encoding))
    conn.commit()

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return send_from_directory('static/html', 'login.html')

@app.route('/recognition')
def recognition_page():
    return send_from_directory('static/html', 'recognition.html')

@app.route('/register')
def register_page():
    return send_from_directory('static/html', 'register.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    numero_aplica = data.get('numero_aplica')
    password = data.get('password')
    imagen_base64 = data.get('imagen_facial')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_aplica, password, encoding FROM usuarios WHERE numero_aplica = %s", (numero_aplica,))
        user = cursor.fetchone()
        if user:
            nombre_usuario, password_hash, user_encoding = user

            # Verifica la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                # Llamada a la función de reconocimiento facial
                if validate_face(imagen_base64, user_encoding):
                    return jsonify({"status": "success", "message": f"Inicio de sesión exitoso, bienvenido {nombre_usuario}", "redirect_url": url_for('recognition_page')})
                else:
                    return jsonify({"status": "error", "message": "Reconocimiento facial no coincide"})
            else:
                return jsonify({"status": "error", "message": "Contraseña incorrecta"})
        else:
            return jsonify({"status": "error", "message": "Número de trabajador no encontrado"})
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({"status": "error", "message": "Error en el servidor"})

@app.route('/recognition', methods=['POST'])
def recognition():
    data = request.json
    imagen_base64 = data.get('imagen_facial')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, apellido, genero, edad, nacionalidad, curp, APLescuela, APLturno, tipoexa, encoding FROM alumnos")
        users = cursor.fetchall()
        for user in users:
            nombre_usuario, apellido_usuario, genero, edad, nacionalidad, curp, APLescuela, APLturno, tipoexa, user_encoding = user

            if validate_face(imagen_base64, user_encoding):
                return jsonify({
                    "status": "success", 
                    "message": f"Persona reconocida: {nombre_usuario} {apellido_usuario}",
                    "data": {
                        "nombre": nombre_usuario,
                        "apellido": apellido_usuario,
                        "genero": genero,
                        "edad": edad,
                        "nacionalidad": nacionalidad,
                        "curp": curp,
                        "APLescuela": APLescuela,
                        "APLturno": APLturno,
                        "tipoexa": tipoexa
                    }
                })
        
        return jsonify({"status": "error", "message": "Reconocimiento facial no coincide con ningún usuario registrado"})
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({"status": "error", "message": "Error en el servidor"})

@app.route('/register', methods=['POST'])
def register():
    imagen_facial = request.files.get('imagen_facial')
    if imagen_facial:
        ruta_imagen = 'captura.png'
        imagen_facial.save(ruta_imagen)

        imagen = face_recognition.load_image_file(ruta_imagen)
        encodings = face_recognition.face_encodings(imagen)
        if len(encodings) > 0:
            encoding = encodings[0]
        else:
            return jsonify({"status": "error", "message": "No se pudo encontrar ningún rostro en la imagen."})
    else:
        return jsonify({"status": "error", "message": "No se proporcionó una imagen facial."})

    nombre_usuario = request.form['nombre_aplica']
    password = request.form['password']
    numero_aplica = request.form['numero_aplica']
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    registrar_usuario(nombre_usuario, password_hash, numero_aplica, encoding.tobytes())

    return jsonify({"status": "success", "message": "Usuario registrado con éxito"})

@app.route('/getAlumnosInfo', methods=['GET'])
def get_alumnos_info():
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT nombre, apellido, genero, edad, nacionalidad, curp, APLescuela, APLturno, tipoexa FROM alumnos")
        alumnos = cursor.fetchall()

        return jsonify(alumnos)
    except Exception as e:
        print(f"Error al obtener información de delincuentes: {e}")
        return jsonify({"status": "error", "message": "Error al obtener información"})

@app.route('/images_INTERPOL/<filename>')
def send_image(filename):
    return send_from_directory('D:\\ExamSecure\\images_alumnos', filename)

def validate_face(imagen_base64, user_encoding):
    try:
        im_bytes = base64.b64decode(imagen_base64)   
        im_file = BytesIO(im_bytes)  
        img = Image.open(im_file)

        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        known_encoding = np.frombuffer(user_encoding, dtype=np.float64)

        face_encodings = face_recognition.face_encodings(img_array)
        if face_encodings:
            face_distances = face_recognition.face_distance([known_encoding], face_encodings[0])
            best_match_index = np.argmin(face_distances)

            if face_distances[best_match_index] < 0.6:
                return True
        return False
    except Exception as e:
        print(f"Error en la validación facial: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
