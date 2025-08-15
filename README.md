# Proyecto Final: Streaming y Análisis de Sentimiento

Este proyecto implementa un pipeline completo de **streaming de datos** para analizar comentarios de Twitter en tiempo real utilizando un modelo de *Deep Learning* pre-entrenado. La arquitectura incluye servicios de Kafka, MongoDB, MySQL y Metabase desplegados con Docker.

## Componentes

1. **Clientes (Producers)** – Scripts de Python que envían mensajes aleatorios a Kafka.
2. **Consumer** – Escucha mensajes de Kafka y los almacena como datos crudos en MongoDB.
3. **Pipeline de Deep Learning** – Obtiene datos sin procesar de MongoDB, predice el sentimiento con un modelo de HuggingFace y guarda resultados en MySQL.
4. **Dashboard** – Metabase se conecta a MySQL para visualizar los resultados.

## Requisitos

- Docker y Docker Compose
- Python 3.10+
- Dependencias Python (`pip install -r requirements.txt`)

## Puesta en marcha

1. **Levantar los servicios de infraestructura**:

   ```bash
   docker-compose up -d
   ```

2. **Crear el tópico de Kafka** (una sola vez):

   ```bash
   docker exec -it proyecto-final-kafka-1 kafka-topics --create \
     --topic twitter --bootstrap-server localhost:9092
   ```

3. **Instalar dependencias de Python**:

   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

### Productores

Cada productor genera entre 5 y 15 mensajes con un intervalo aleatorio (0.5 a 3s).

```bash
python scripts/producer.py
```

Ejecute múltiples instancias para simular varios clientes.

### Consumer

Escucha el tópico `twitter` y guarda los mensajes en MongoDB.

```bash
python scripts/consumer.py
```

### Pipeline de Deep Learning

Procesa los mensajes no tratados en MongoDB, predice su sentimiento y almacena los resultados en MySQL.

```bash
python scripts/ml_pipeline.py
```

## Dashboard en Metabase

1. Acceda a [http://localhost:3000](http://localhost:3000) y complete la configuración inicial.
2. Configure una conexión a la base de datos MySQL (`host: mysql`, `usuario: root`, `contraseña: example`, `base: twitter`).
3. Cree al menos **tres visualizaciones**, por ejemplo:
   - Conteo de mensajes por sentimiento.
   - Comentarios negativos por usuario.
   - Evolución temporal de comentarios positivos.

## Estructura de la base de datos

- **MongoDB** (`twitter_db.raw_comments`): almacena mensajes crudos con campos `user_id`, `comment`, `timestamp`, `processed` y `sentiment`.
- **MySQL** (`twitter.tweets`): contiene `user_id`, `comment`, `sentiment`, `score` y `created_at` para el análisis en el dashboard.

## Notas

- El modelo `distilbert-base-uncased-finetuned-sst-2-english` de Hugging Face se ejecuta directamente con PyTorch, sin utilizar `transformers.pipeline`.
- Ajuste las variables y puertos según sea necesario para su entorno.
