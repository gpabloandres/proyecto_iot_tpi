# Importa las librerías necesarias
import paho.mqtt.client as mqtt
import time
import random
import json
import socket

# --- Configuración del broker MQTT ---
MQTT_SERVER = "broker.hivemq.com"       # Broker público accesible por MQTT
MQTT_PORT = 1883                          # Puerto MQTT estándar
MQTT_TOPIC_TEMP = "comedor/dht11/temperatura" # Tópico para la temperatura
MQTT_TOPIC_HUM = "comedor/dht11/humedad"      # Tópico para la humedad
CLIENT_ID = f"simulador-dht11-{socket.gethostname()}-{random.randint(1000, 9999)}"

# Crea una instancia del cliente MQTT usando la API de callbacks actual
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID,
)

# --- Funciones de callback del cliente MQTT ---

def on_connect(client, userdata, flags, reason_code, properties):
    """Callback que se ejecuta al conectar al broker."""
    if reason_code == 0:
        print("Conectado exitosamente al broker MQTT.")
    else:
        print(f"Fallo en la conexión. Código de error: {reason_code}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """Callback que se ejecuta al desconectar del broker."""
    print("Desconectado del broker MQTT.")

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# --- Bucle principal de simulación ---
try:
    print(f"Intentando conectar a {MQTT_SERVER}:{MQTT_PORT}...")
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.loop_start() # Inicia el bucle de red en segundo plano

    while True:
        # Simula la lectura de un sensor DHT11
        # Temperatura en grados Celsius (ej. entre 18.0 y 30.0)
        temperatura = round(random.uniform(18.0, 30.0), 2)
        # Humedad relativa en porcentaje (ej. entre 40% y 80%)
        humedad = round(random.uniform(40.0, 80.0), 2)

        # Publica los valores en sus respectivos tópicos
        temp_result = client.publish(MQTT_TOPIC_TEMP, str(temperatura), qos=1)
        hum_result = client.publish(MQTT_TOPIC_HUM, str(humedad), qos=1)

        if temp_result.rc != mqtt.MQTT_ERR_SUCCESS or hum_result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(
                f"Error al publicar (temperatura: {temp_result.rc}, "
                f"humedad: {hum_result.rc})"
            )
        else:
            print(f"Publicado con éxito usando Client ID '{CLIENT_ID}'")
        
        print(f"Publicado -> Temp: {temperatura}°C en '{MQTT_TOPIC_TEMP}', Hum: {humedad}% en '{MQTT_TOPIC_HUM}'")

        time.sleep(5) # Espera 5 segundos antes de la siguiente lectura

except KeyboardInterrupt:
    print("\nSimulación terminada por el usuario.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    print("Cliente MQTT desconectado y programa finalizado.")