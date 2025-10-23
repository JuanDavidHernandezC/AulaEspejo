from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pymysql
import pandas as pd

from models.recomendador_te import recomendar_te
from models.segmentador_clientes import predecir_segmento

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Contraseña2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/hampite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODELO DE USUARIO ------------------ #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esa página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id else None

# ------- Rutas principales ---------- #
@app.route('/')
def index():
    return render_template('index.html', user=g.user)

@app.route('/inicio', methods=['GET', 'POST'])
@login_required
def inicio():
    recomendacion = None
    segmento = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # --- Formulario del recomendador de té ---
        if form_type == 'te':
            preferencias = {
                'Tipo': request.form['tipo'],
                'Efecto': request.form['efecto'],
                'Sabor': request.form['sabor'],
                'TiempoInfusion': float(request.form['tiempo_infusion']),
                'Temperatura': float(request.form['temperatura']),
                'Edad': int(request.form['edad'])
            }
            recomendacion = recomendar_te(preferencias)
            flash('Recomendación generada con éxito 🍵', 'success')

        # --- Formulario del segmentador de clientes ---
        elif form_type == 'cliente':
            cliente = {
                'Edad': int(request.form['edad']),
                'Ingreso': float(request.form['ingreso']),
                'Salud': int(request.form['salud']),
                'Actividad': int(request.form['actividad']),
                'FrecuenciaConsumo': int(request.form['frecuencia']),
                'Ciudad': 'Bogotá',
                'Educacion': 'universitario',
                'EstiloVida': 'activo',
                'PreferenciaSabor': 'dulce'
            }
            segmento = predecir_segmento(cliente)
            flash('Segmento identificado correctamente 👥', 'info')

    return render_template('inicio.html', user=g.user, recomendacion=recomendacion, segmento=segmento)

@app.route('/products')
def products():
    return render_template('products.html', user=g.user)

@app.route('/about')
def about():
    return render_template('about.html', user=g.user)

@app.route('/contact')
def contact():
    return render_template('contact.html', user=g.user)

# ----- Registro y login ------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado', 'danger')
            return redirect(url_for('register'))

        nuevo_usuario = User(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            flash(f'¡Bienvenido, {user.nombre}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
