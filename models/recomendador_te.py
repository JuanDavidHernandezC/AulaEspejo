import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.neighbors import NearestNeighbors

data = pd.read_csv('data/hampite_tes.csv')
data.columns = data.columns.str.lower()

mapeos = {
    'muy bajo': 0,
    'bajo': 1,
    'medio': 2,
    'alto': 3,
    'muy alto': 4
}

for col in ['nivel_acidez', 'intensidad_sabor', 'nivel_quimico']:
    data[col] = data[col].astype(str).str.lower().map(mapeos).fillna(data[col])
    data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

label_cols = [
    'tipo', 'categoria', 'ingredientes',
    'uso_recomendado', 'target_principal',
    'edad_recomendada', 'preferencia_publico', 'beneficios'
]
label_encoders = {}
for col in label_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))
    label_encoders[col] = le

num_cols = [
    'nivel_acidez',
    'intensidad_sabor',
    'tiempo_secado_horas',
    'nivel_quimico',
    'precio_estimado_usd',
    'calificacion_consumidor'
]
scaler = MinMaxScaler()
data[num_cols] = scaler.fit_transform(data[num_cols])

# Entrenamiento del modelo de vecinos más cercanos
features = label_cols + num_cols
X = data[features]
knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
knn.fit(X)

def recomendar_te(preferencias):
    """
    Recibe:
    {
      'Tipo': ...,
      'Efecto': ...,
      'Sabor': ...,
      'Temperatura': ...,
      'Edad': ...
    }
    Retorna recomendaciones de tés y hábitos saludables.
    """
    entrada = pd.DataFrame([preferencias])
    entrada.columns = entrada.columns.str.lower()

    for col in label_cols:
        if col in entrada.columns:
            le = label_encoders[col]
            entrada[col] = entrada[col].apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else 0
            )

    for col in ['nivel_acidez', 'intensidad_sabor', 'nivel_quimico']:
        if col in entrada.columns:
            valor = str(entrada[col].iloc[0]).lower()
            entrada[col] = mapeos.get(valor, entrada[col].iloc[0])

    for col in features:
        if col not in entrada.columns:
            entrada[col] = 0

    entrada[num_cols] = scaler.transform(entrada[num_cols])

    distancias, indices = knn.kneighbors(entrada[features])
    recomendaciones = data.iloc[indices[0]][['nombre', 'tipo', 'categoria', 'beneficios', 'precio_estimado_usd']].copy()

    for col in ['tipo', 'categoria', 'beneficios']:
        le = label_encoders[col]
        recomendaciones[col] = le.inverse_transform(recomendaciones[col])

    recomendaciones = recomendaciones[['nombre', 'beneficios', 'precio_estimado_usd']]

    edad = int(preferencias.get('Edad', 30))
    efecto = preferencias.get('Efecto', '').lower()

    habitos = []

    if edad < 18:
        habitos.append("🥗 Incluye frutas y verduras todos los días para crecer fuerte.")
        habitos.append("🏃 Realiza al menos 1 hora de actividad física diaria.")
        habitos.append("😴 Duerme entre 8 y 10 horas para mantener tu energía y concentración.")
    elif edad < 25:
        habitos.append("💧 Mantén buena hidratación (8 vasos de agua al día).")
        habitos.append("🥦 Añade frutas y verduras frescas en cada comida.")
        habitos.append("🧠 Evita trasnochar y regula tu tiempo frente a pantallas.")
    elif edad < 45:
        habitos.append("🚶 Realiza caminatas diarias de 30 minutos.")
        habitos.append("🧘 Prueba meditación o yoga si buscas equilibrio mental.")
        habitos.append("🍎 Mantén una dieta balanceada con bajo consumo de azúcares procesados.")
    else:
        habitos.append("❤️ Controla tu presión y azúcar periódicamente.")
        habitos.append("🕊️ Consume infusiones suaves antes de dormir.")
        habitos.append("💪 Realiza ejercicios de bajo impacto para mantener la movilidad.")

    # Hábitos adicionales según el tipo de efecto del té
    if "energ" in efecto:
        habitos.append("☀️ Aprovecha la luz solar matutina para activar tu energía.")
    elif "relaj" in efecto:
        habitos.append("🌙 Evita pantallas brillantes 1 hora antes de dormir.")
    elif "digest" in efecto:
        habitos.append("🍽️ Mastica lentamente y evita comidas pesadas en la noche.")

    texto_final = "✨ Tés Recomendados\n\n"

    for _, row in recomendaciones.iterrows():
        nombre = row['nombre']
        beneficios = row['beneficios']
        precio = f"${row['precio_estimado_usd']:.2f}"
        
        texto_final += f"🍃 {nombre}\n"
        texto_final += f"   💚 Beneficios: {beneficios}\n"
        texto_final += f"   💰 Precio: {precio}\n\n"

    texto_final += "🌟 Hábitos Saludables Sugeridos\n\n"
    for habito in habitos:
        texto_final += f"• {habito}\n"
    return texto_final