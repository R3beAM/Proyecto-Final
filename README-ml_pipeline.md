Imports

torch: inferencia en GPU/CPU y utilidades tensoriales.

transformers (AutoModelForSequenceClassification, AutoTokenizer): carga del tokenizer y del modelo de clasificación de secuencias.

pymongo.MongoClient: cliente para conectarse a MongoDB.

mysql.connector: conector oficial de MySQL para Python.

Configuración

MONGO_URI, DB_NAME, COLLECTION: a qué base/colección de MongoDB conectarse.

MYSQL_CONFIG: parámetros de conexión a MySQL.

MODEL_NAME: nombre del modelo de Hugging Face a usar (distilbert fine-tuneado para sentimiento binario).

Clase SentimentModel
__init__

self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Selecciona GPU si hay CUDA; si no, CPU.

self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
Descarga/carga el tokenizer correspondiente al modelo.

self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(self.device).eval()
Descarga/carga el modelo, lo mueve al dispositivo elegido y lo pone en modo evaluación (eval() desactiva dropout, etc.).

predict(self, text: str) -> tuple[str, float]

inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
Tokeniza el texto y devuelve tensores PyTorch; se mueven a CPU/GPU.

with torch.no_grad():
Bloque sin gradientes (más rápido y ahorra memoria en inferencia).

logits = self.model(**inputs).logits
Pasa el input por el modelo; obtiene logits (puntuaciones sin normalizar).

probs = torch.nn.functional.softmax(logits, dim=1)
Convierte logits en probabilidades para cada clase.

score, idx = torch.max(probs, dim=1)
Toma la clase con probabilidad máxima y su valor.

label = self.model.config.id2label[idx.item()]
Mapea el índice de clase al nombre (p.ej., “POSITIVE” o “NEGATIVE”).

return label, float(score.item())
Devuelve la etiqueta y su probabilidad (como float).

Función run()
Conexiones y preparación

mongo = MongoClient(MONGO_URI)
Crea cliente de MongoDB.

collection = mongo[DB_NAME][COLLECTION]
Selecciona base y colección (twitter_db.raw_comments).

mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
Abre conexión a MySQL.

cursor = mysql_conn.cursor()
Crea cursor para ejecutar SQL.

cursor.execute(""" CREATE TABLE IF NOT EXISTS tweets ( ... ) """)
Crea la tabla tweets si no existe (id autoincremental, user_id, comment, sentiment, score, created_at).

mysql_conn.commit()
Confirma la creación de tabla.

Carga del modelo

model = SentimentModel()
Instancia el modelo de sentimiento (descarga modelos si es primera vez).

Bucle de procesamiento

while True: …
Itera hasta que no haya más documentos “pendientes”.

doc = collection.find_one({"processed": False})
Busca un documento sin procesar (campo processed: False).

if not doc: ... break
Si no hay más, sale del bucle.

sentiment, score = model.predict(doc["comment"])
Obtiene etiqueta y probabilidad para el texto del comentario.

collection.update_one({"_id": doc["_id"]}, {"$set": {"processed": True, "sentiment": sentiment, "score": score}})
Marca el doc como procesado y guarda el resultado en MongoDB.

cursor.execute("INSERT INTO tweets (...) VALUES (%s, %s, %s, %s)", (...))
Inserta en MySQL el user_id, comment, sentiment, score.

mysql_conn.commit()
Confirma la inserción.

print(f"Processed {doc['_id']} -> {sentiment} ({score:.4f})")
Log simple en consola.

Limpieza

cursor.close() y mysql_conn.close()
Cierra el cursor y la conexión con MySQL.

Entry point

if __name__ == "__main__": run()
Ejecuta run() si se invoca el archivo directamente.
