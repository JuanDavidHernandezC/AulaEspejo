import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier

# ==============================
# 🔹 Cargar y preparar los datos
# ==============================
try:
    df = pd.read_csv('data/hampite_clientes.csv')
except Exception as e:
    print("⚠️ Error al cargar el archivo CSV:", e)
    raise SystemExit

# Asegurar nombres consistentes (sin espacios ni mayúsculas accidentales)
df.columns = [c.strip().lower() for c in df.columns]

# Validar columnas esperadas
columnas_esperadas = [
    'id', 'edad', 'ciudad', 'educacion', 'ingresos_mensuales',
    'estilo_vida', 'frecuencia_consumo', 'preferencia_sabor',
    'interes_salud', 'segmento'
]
for col in columnas_esperadas:
    if col not in df.columns:
        raise ValueError(f"Falta la columna requerida: '{col}' en el CSV.")

# ==============================
# 🔹 Codificación de variables
# ==============================
label_encoders = {}
columnas_categoricas = ['ciudad', 'educacion', 'estilo_vida', 'preferencia_sabor', 'segmento']

for col in columnas_categoricas:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Asegurar que las columnas numéricas sean realmente numéricas
for col in ['edad', 'ingresos_mensuales', 'frecuencia_consumo', 'interes_salud']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ==============================
# 🔹 Entrenamiento del modelo
# ==============================
X = df[['edad', 'ciudad', 'educacion', 'ingresos_mensuales',
        'estilo_vida', 'frecuencia_consumo', 'preferencia_sabor', 'interes_salud']]
y = df['segmento']

modelo = KNeighborsClassifier(n_neighbors=3)
modelo.fit(X, y)

# ==============================
# 🔹 Función de predicción
# ==============================
def predecir_segmento(cliente):
    """
    Recibe un diccionario con:
      Edad, Ciudad, Educacion, Ingreso, EstiloVida,
      FrecuenciaConsumo, PreferenciaSabor, Salud.
    Retorna el nombre del segmento predicho.
    """
    try:
        # Transformar valores categóricos con seguridad
        datos = pd.DataFrame([{
            'edad': cliente.get('Edad', 0),
            'ciudad': label_encoders['ciudad'].transform([cliente.get('Ciudad', 'Bogotá')])[0]
                if cliente.get('Ciudad', 'Bogotá') in label_encoders['ciudad'].classes_
                else 0,
            'educacion': label_encoders['educacion'].transform([cliente.get('Educacion', 'Universitario')])[0]
                if cliente.get('Educacion', 'Universitario') in label_encoders['educacion'].classes_
                else 0,
            'ingresos_mensuales': cliente.get('Ingreso', 0),
            'estilo_vida': label_encoders['estilo_vida'].transform([cliente.get('EstiloVida', 'Activo')])[0]
                if cliente.get('EstiloVida', 'Activo') in label_encoders['estilo_vida'].classes_
                else 0,
            'frecuencia_consumo': cliente.get('FrecuenciaConsumo', 1),
            'preferencia_sabor': label_encoders['preferencia_sabor'].transform([cliente.get('PreferenciaSabor', 'Dulce')])[0]
                if cliente.get('PreferenciaSabor', 'Dulce') in label_encoders['preferencia_sabor'].classes_
                else 0,
            'interes_salud': cliente.get('Salud', 0)
        }])

        pred = modelo.predict(datos)[0]
        segmento_nombre = label_encoders['segmento'].inverse_transform([pred])[0]
        return segmento_nombre

    except Exception as e:
        print("⚠️ Error en predicción:", e)
        return "Desconocido"
