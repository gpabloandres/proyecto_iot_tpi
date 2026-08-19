# Guía para poner en funcionamiento el circuito de medición de temperatura y humedad con ESP8266 + DHT11 + MQTT + Node-RED

## Paso 1: Conectar los dispositivos a la misma red
- Asegurarse de que **la PC** y el **ESP8266** estén conectados a la misma red WiFi.  
- Apuntar el nombre de la red (SSID) y la contraseña.  

## Paso 2: Verificar direcciones IP
- Abrir la terminal de Windows (CMD) y ejecutar:  
  ```
  ipconfig
  ```  
- Identificar la **IP de la PC**.  
- La **IP del ESP8266** se verá luego en el **monitor serial** del IDE de Arduino una vez cargado el programa.  

## Paso 3: Conectar y programar el ESP8266
- Conectar el **sensor DHT11** al ESP8266:  
  - VCC → 3.3V  
  - GND → GND  
  - DATA → Pin digital (ej. D4)  
- Abrir el **IDE de Arduino**.  
- Seleccionar la **placa ESP8266** (Ejemplo: NodeMCU 1.0).  
- Seleccionar el **puerto COM** correcto.  
- Instalar las librerías necesarias:  
  - `DHT sensor library`  
  - `Adafruit Unified Sensor`  
  - `PubSubClient`  
- Cargar un programa que:  
  - Configure el **WiFi** con el SSID y contraseña.  
  - Lea los valores de **temperatura y humedad** desde el DHT11.  
  - Se conecte al **servidor MQTT** (Broker).  
  - Publique los datos en los tópicos MQTT del proyecto:  
    - `comedor/dht11/temperatura`  
    - `comedor/dht11/humedad`  

## Paso 4: Verificar conexión
- Abrir el **monitor serial** del IDE de Arduino.  
- Revisar que:  
  - El ESP8266 se conecte correctamente a la red WiFi.  
  - Se muestre la **IP asignada al ESP8266**.  
  - Se confirme la conexión al broker MQTT.  
  - Se publiquen valores de temperatura y humedad.  

## Paso 5: Configurar el broker MQTT
- Si se usa **Mosquitto** en la PC como broker:  
  - Asegurarse de que esté instalado y en ejecución.  
  - Usar el puerto estándar **1883**.  
- Si hay problemas de conexión por IP:  
  - Revisar con:  
    ```
    netsh interface portproxy show all
    ```  
  - En caso de conflicto, borrar y volver a crear la regla con:  
    ```
    netsh interface portproxy delete v4tov4 listenaddress=192.168.x.x listenport=1883
    netsh interface portproxy add v4tov4 listenaddress=MI_IP_LOCAL listenport=1883 connectaddress=127.0.0.1 connectport=1883
    ```  

## Paso 6: Configurar Node-RED
- Abrir Node-RED en el navegador (`http://localhost:1880`).  
- Añadir **dos nodos MQTT IN** y configurarlos con:  
  - Servidor: `broker.hivemq.com`.  
  - Puerto: 1883.  
  - Tópicos:  
    - `comedor/dht11/temperatura`  
    - `comedor/dht11/humedad`  
- Conectar cada nodo a un **debug** para probar que llegan los datos.  

## Paso 7: Crear la interfaz web
- Usar los nodos de **Node-RED Dashboard** (`node-red-dashboard`).  
- Insertar un **gauge** para mostrar la temperatura.  
- Insertar un **gauge** o **chart** para mostrar la humedad.  
  ```
  http://localhost:1880/ui
  ```  

## Paso 8: Importar y configurar el flujo actualizado
- Importar `NodeRedflowsMQTTDHT11.json` desde el menú **Import** de Node-RED.
- El flujo escucha el broker público `broker.hivemq.com:1883` en los tópicos:
  - `comedor/dht11/temperatura`
  - `comedor/dht11/humedad`
- La alerta se activa cuando la temperatura está fuera de `18–30 °C` o la humedad fuera de `40–80 %`.

## Paso 9: Configurar Telegram
- Crear un bot con `@BotFather` y obtener su token.
- Enviar al bot un mensaje desde el chat que recibirá las alertas.
- Obtener el `chat_id` mediante la API de Telegram o un bot de consulta.
- Definir estas variables de entorno en el proceso de Node-RED:
  ```text
  TELEGRAM_BOT_TOKEN=token_del_bot
  TELEGRAM_CHAT_ID=id_del_chat
  ```
- Reiniciar Node-RED después de definir las variables. El token no se guarda dentro del archivo JSON.

## Paso 10: Instalar InfluxDB local
- InfluxDB 2.9 debe estar iniciado como servicio de Windows.
- Abrir la interfaz local en `http://localhost:8086`.
- Crear o verificar la organización `tpi2026` y el bucket `dht11`.
- Crear un token con permiso **Write** sobre el bucket `dht11` desde **Load Data > API Tokens**.
- Guardar el token: se utilizará únicamente en la configuración de Node-RED.

## Paso 11: Configurar Node-RED para InfluxDB local
- Definir estas variables de entorno en el proceso de Node-RED:
  ```text
  INFLUXDB_URL=http://localhost:8086
  INFLUXDB_ORG=tpi2026
  INFLUXDB_BUCKET=dht11
  INFLUXDB_TOKEN=token_de_escritura_local
  ```
- Como Node-RED e InfluxDB están instalados en Windows, `localhost` es correcto.
- Reiniciar Node-RED después de definir las variables. El flujo escribe la medición `dht11`, con la etiqueta `ubicacion=comedor` y los campos `temperatura` y `humedad`.
- Consultar los datos desde **Data Explorer** en `http://localhost:8086`.

## Paso 12: Preparar el entorno de Windows
- Instalar Node.js LTS, Node-RED, Python y las dependencias del proyecto.
- Comprobar las instalaciones desde una terminal:
  ```cmd
  node --version
  npm --version
  node-red --version
  python --version
  ```
- Si Node-RED no reconoce los nodos `ui_gauge`, `ui_chart` o `ui_group`, instalar Dashboard:
  ```cmd
  npm install -g --unsafe-perm node-red-dashboard
  ```
- Desde la carpeta del proyecto, instalar la dependencia Python del simulador:
  ```cmd
  python -m pip install -r requirements.txt
  ```

## Paso 13: Configurar las variables de entorno
- Las variables deben registrarse en Windows antes de iniciar Node-RED. Sustituir todos los valores de ejemplo por los valores reales.
- Opción A: registrarlas permanentemente desde **PowerShell** con `setx`:
  ```powershell
  setx INFLUXDB_URL "http://localhost:8086"
  setx INFLUXDB_ORG "tpi2026"
  setx INFLUXDB_BUCKET "dht11"
  setx INFLUXDB_TOKEN "token_de_escritura_local"
  setx TELEGRAM_BOT_TOKEN "token_del_bot"
  setx TELEGRAM_CHAT_ID "id_del_chat"
  ```
- `setx` guarda las variables para futuras terminales, pero no las agrega a la terminal que ya está abierta.
- Opción B: registrarlas mediante la interfaz gráfica de Windows:
  1. Presionar `Win + R`, escribir `sysdm.cpl` y pulsar **Enter**.
  2. Abrir **Opciones avanzadas > Variables de entorno**.
  3. En **Variables de usuario**, pulsar **Nueva**.
  4. Crear cada variable con su nombre y valor:
     - `INFLUXDB_URL` = `http://localhost:8086`
     - `INFLUXDB_ORG` = `tpi2026`
     - `INFLUXDB_BUCKET` = `dht11`
     - `INFLUXDB_TOKEN` = token local con permiso **Write**
     - `TELEGRAM_BOT_TOKEN` = token entregado por `@BotFather`
     - `TELEGRAM_CHAT_ID` = identificador del chat de Telegram
  5. Pulsar **Aceptar** en todas las ventanas.
- No es necesario utilizar ambas opciones: elegir PowerShell o la interfaz gráfica.
- Cerrar las terminales abiertas de Node-RED y abrir una nueva. Después reiniciar Node-RED, porque las variables se cargan cuando se inicia el proceso.
- Para verificar las variables en una terminal nueva:
  ```powershell
  Get-ChildItem Env:INFLUXDB*
  Get-ChildItem Env:TELEGRAM*
  ```
- También se pueden comprobar individualmente sin mostrar los tokens completos:
  ```powershell
  $env:INFLUXDB_URL
  $env:INFLUXDB_ORG
  $env:INFLUXDB_BUCKET
  $env:INFLUXDB_TOKEN.Length
  $env:TELEGRAM_BOT_TOKEN.Length
  $env:TELEGRAM_CHAT_ID
  ```
- Si una variable no aparece, cerrar la terminal, abrir otra y repetir la comprobación. No colocar los tokens directamente en `NodeRedflowsMQTTDHT11.json` ni publicarlos en capturas o repositorios.

## Paso 14: Iniciar InfluxDB local
- Abrir una ventana de **PowerShell**.
- Ejecutar el servicio de InfluxDB desde su carpeta de instalación:
  ```powershell
  cd -Path 'C:\Program Files\InfluxData\influxdb'
  ./influxd
  ```
- Mantener esta ventana abierta mientras se ejecuta el proyecto.
- Verificar desde el navegador que InfluxDB responde en `http://localhost:8086`.
- También se puede comprobar desde PowerShell:
  ```powershell
  Invoke-WebRequest http://localhost:8086/health
  ```

## Paso 15: Iniciar Node-RED
- Abrir una segunda ventana de **CMD**. No cerrar la ventana de InfluxDB.
- Iniciar Node-RED:
  ```cmd
  node-red
  ```
- Esperar un mensaje similar a `Server now running at http://127.0.0.1:1880/`.
- Abrir `http://localhost:1880` en el navegador.
- Importar `NodeRedflowsMQTTDHT11.json` si todavía no se importó.
- Comprobar que el broker MQTT sea `broker.hivemq.com:1883` y pulsar **Deploy**.
- Abrir el dashboard en `http://localhost:1880/ui`.
- Mantener esta ventana abierta mientras se ejecuta el proyecto.

## Paso 16: Iniciar el simulador o el ESP8266
- Para utilizar el simulador Python, abrir una tercera ventana de **CMD** en la carpeta del proyecto:
  ```cmd
  cd /d D:\Proceso2026\CTPAMM\TPI\TPI2026
  .venv\Scripts\activate
  python SimulaESP8266DHT11MQTT.py
  ```
- Si no se creó el entorno virtual, utilizar directamente:
  ```cmd
  .venv\Scripts\python.exe SimulaESP8266DHT11MQTT.py
  ```
- Para utilizar el ESP8266, detener el simulador y cargar `ESP8266DHT11MQTT.ino` desde Arduino IDE.
- El simulador y el ESP8266 no deben publicar simultáneamente con el mismo `CLIENT_ID`.

## Paso 17: Verificar el funcionamiento completo
- En la consola del simulador o del ESP8266, confirmar publicaciones en los tópicos MQTT.
- En Node-RED, revisar los nodos `Respuesta Telegram` y `Respuesta InfluxDB` en la pestaña **Debug**.
- En InfluxDB, abrir **Data Explorer**, seleccionar el bucket `dht11` y consultar la medición `dht11`.
- En Node-RED Dashboard, comprobar los gauges y gráficos en `http://localhost:1880/ui`.
- Para probar Telegram, publicar temporalmente una temperatura mayor que `30` °C o una humedad mayor que `80` %.
- Para detener cada servicio, presionar `Ctrl+C` en su ventana correspondiente.

## Paso 18: Solución de problemas frecuentes
- Si Node-RED muestra `ECONNREFUSED` para InfluxDB, comprobar que `influxd` siga ejecutándose y que `http://localhost:8086/health` responda.
- Si InfluxDB responde `401 Unauthorized`, revisar `INFLUXDB_TOKEN` y que el token tenga permiso **Write** sobre el bucket `dht11`.
- Si Node-RED no recibe mensajes, comprobar que el broker sea `broker.hivemq.com`, el puerto sea `1883` y los tópicos coincidan exactamente.
- Si Telegram no envía alertas, revisar `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` y que el usuario haya iniciado una conversación con el bot.
- Si aparece `node-red: command not found`, instalar Node-RED globalmente con `npm install -g --unsafe-perm node-red` y abrir una terminal nueva.

---
✅ Con esto, el circuito estará funcionando: el **ESP8266 mide la temperatura y humedad con el DHT11**, **envía los datos por MQTT**, **Node-RED los recibe y muestra en la web**, **notifica valores fuera de rango por Telegram** y **guarda el histórico en InfluxDB local**.
