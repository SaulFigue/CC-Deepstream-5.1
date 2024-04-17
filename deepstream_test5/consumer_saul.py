from kafka import KafkaConsumer
import json
import time
import datetime
import psycopg2



idx = 0

def insert_db(registers):
    global idx

    if registers:
        for reg in registers:
            #combined[cam] = {'acceso_id': "QN_CP_1", 'nombre_comercial_acceso': "EL COMERCIO", 'timestamp': timestamp, 'date': date, 'year': year, 'month': month, 'day': day, 'hour': hour, 'in': ingreso, 'out': salida}
            idx += 1
            print(f"{idx:<2} ||   {reg['id_cc']}   ||  {reg['id_cam']}  ||  {reg['acceso_id']}  ||       {reg['nombre_comercial_acceso']}       || {reg['timestamp']} || {reg['date']} || {reg['year']} ||    {reg['month']}  ||   {reg['day']} ||   {reg['hour']}  ||    {reg['in']}     ||    {reg['out']}    ||")
            

            # Query para ingresar datos a la base
            # cadena = f"insert into datos_ingresos(id, id_cc, id_cam, acceso_id, nombre_comercial_acceso, timestamp, date, year, month, day, hour, ingresos, salidas) VALUES ({idx}, {reg['id_cc']}, {reg['id_cam']}, '{reg['acceso_id']}', '{reg['nombre_comercial_acceso']}', '{reg['timestamp']}', '{reg['date']}', {reg['year']}, {reg['month']}, {reg['day']}, {reg['hour']}, {reg['in']}, {reg['out']});"
            
            # cur.execute(cadena)
            # conn.commit()

# ------------------------------------------------------- KAFKA FUNCTIONS ----------------------------------------

def construct_register(messages):
    combined = {}
    if messages:
        # ======= LEEREMOS EL ARCHIVO ANALITYCS PARA EXTRAER EL NOMBRE DE LA PUERTA DEL CC
        path_analytics = "/opt/nvidia/deepstream/deepstream-5.1/sources/apps/cc-lc/deepstream_test5/configs/config_nvdsanalytics.txt"
        lineas = []
        with open(path_analytics, 'r') as analytics:
            stream_actual = None
            for linea in analytics:
                lineas.append(linea)

        #Guardare los datos de acceso_id y nombre comercial dependiendo del stream
        Acceso_Comercio = {}

        #Itero entre las lineas del config de analytics
        for i in range (len(lineas)):
            if("line-crossing-stream-" in lineas[i]):
                #Aqui extraigo todo el line-crossing con el stream-x
                lc_stream = lineas[i]
                
                #Saco el stream_id en caso de necesitarse
                stream = ""
                for c in lc_stream:
                    if c.isdigit():
                        stream += c
                # stream = int(lc_stream[-3])
                stream = int(stream)

                #Aqui extraigo el nombre del acceso_id (es la puerta?)
                acceso = lineas[i-1]
                aux = acceso.split("=")
                if len(aux)>1:
                    accesoId = aux[1].strip()
                
                #Aqui extraigo el nombre_comercial_acceso
                nombre_com = lineas[i-2]
                aux2 = nombre_com.split("=")
                if len(aux2)>1:
                    nombre_comercial = aux2[1].strip()
                
                #Agrego al diccionario {0: {'acceso_id': 'QN_CP_0', 'nombre_comercial_acceso': 'El comercio'}} asi con los 4 streams
                Acceso_Comercio[stream] = {'acceso_id':accesoId, 'nombre_comercial_acceso':nombre_comercial}
        
        #Creo una lista de diccionarios ({},{},..)
        Acceso_list = list(Acceso_Comercio.values())

        # ======= AGREGAREMOS CONTENIDO A combined = {}
        for message in messages:
            # Aqui sumare cada lc_in y lc_out de cada frame
            cam = message['cam']
            ingreso = 0
            salida = 0

            # Para Obtener los datos de cada lc_in
            for i in range(1,51):
                lc_in = "in-"+str(i)
                if(lc_in in message):
                    ingreso += message[lc_in]

            # Para Obtener los datos de cada lc_out
            for i in range(1,51):
                lc_out = "out-"+str(i)
                if(lc_out in message):
                    salida += message[lc_out]

            #si ya existe el registro, voy sumando | sino creo el registro
            if cam in combined.keys():
                    combined[cam]['in'] += ingreso
                    combined[cam]['out'] += salida
            else:
                timestamp = datetime.datetime.now()
                date = timestamp.strftime("%Y-%m-%d")
                # time = timestamp.strftime("%H:%M:%S")
                year = timestamp.year
                month = timestamp.month
                day = timestamp.day
                hour = timestamp.hour
                #Cargamos datos de Puertas? y Nombre de Referencia?
                acceso_id = Acceso_list[cam]['acceso_id']
                nombre_comercial_acceso = Acceso_list[cam]['nombre_comercial_acceso']
                combined[cam] = {'id_cc': 1, 'id_cam': cam, 'acceso_id': acceso_id, 'nombre_comercial_acceso': nombre_comercial_acceso, 'timestamp': timestamp, 'date': date, 'year': year, 'month': month, 'day': day, 'hour': hour, 'in': ingreso, 'out': salida}

        combined_list = list(combined.values())
        return combined_list           

def clean_messages(partitions):
    # messages es una lista [] de diccionarios [{cam,in,out},{cam,in,out},{cam,in,out}]
    messages = []
    if partitions:
        for partition in partitions:
            message = partition.value
            if message is None:
                    continue
            else:
                messages.append(message)
        return messages

def consume_messages():
    try:
        while True:
            start_time = time.time()
            # partitions es una lista [] llena de ConsumerRecord(... values={cam,in,out}).. 
            # partitions = [ConRc(), ConRc(),...]
            partitions = []
            while time.time() - start_time < 5:
                partition = consumer.poll(0).values()
                if partition:
                    partition = list(partition)[0]
                    partitions.extend(partition)

            messages = clean_messages(partitions)
            registers = construct_register(messages)
            insert_db(registers)

    except KeyboardInterrupt:
        exit()


# --------------------------------------- MAIN CODE ---------------------------------------------
topic = 'quickstart-events'
consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'], 
                        value_deserializer=lambda v: json.loads(v.decode('utf-8')))

# print("Index ||    Date    |||    Time    ||| CC || CAM || Ingreso || Salida ")
# print("------++------------+++------------+++----++-----++---------++--------")
print("id || id_cc || CAM || acceso_id || nombre_comercial_acceso ||          timestamp         ||    date    || year || month || day || hour || Ingresos || Salidas ||")
print("---++-------++-----++-----------++-------------------------++----------------------------++------------++------++-------++-----++------++----------++---------++")
consume_messages()
"""
try:
    conn = psycopg2.connect(
        dbname="pruebalc", # se puede buscar el nombre con \l
        user="postgres", # Se puede buscar el nombre con \du o SELECT usename FROM pg_user;
        password="12345", # Se puede cambiar contrasena con: ALTER USER nombre_de_usuario WITH PASSWORD 'nueva_contraseña';
        host="localhost", # por defecto
        port="5432" # por defecto, pero se puede buscar con: SELECT inet_server_addr() AS server_address, current_setting('port') AS port;p

    )
    cur = conn.cursor()
    consume_messages()
    cur.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
"""