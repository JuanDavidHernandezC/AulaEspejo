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
    'preferencia_publico', 'beneficios'
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

features = label_cols + num_cols
X = data[features]
knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
knn.fit(X)

def recomendar_te(preferencias):
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
    recomendaciones = data.iloc[indices[0]]

    return recomendaciones[['nombre', 'tipo', 'categoria', 'beneficios', 'precio_estimado_usd']]
