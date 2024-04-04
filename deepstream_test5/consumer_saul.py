from kafka import KafkaConsumer
import json
import time
import datetime


from kafka import KafkaConsumer
import json
import time
import datetime

"""
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="prueba_saul", # se puede buscar el nombre con \l
        user="postgres", # Se puede buscar el nombre con \du o SELECT usename FROM pg_user;
        password="12345", # Se puede cambiar contrasena con: ALTER USER nombre_de_usuario WITH PASSWORD 'nueva_contraseña';
        host="localhost", # por defecto
        port="5432" # por defecto, pero se puede buscar con: SELECT inet_server_addr() AS server_address, current_setting('port') AS port;p

    )

    cur = conn.cursor()
    cur.execute("INSERT INTO mensaje (cam, in_1, out_1) " + 
                "VALUES (3, 0, 1)")
    
    conn.commit()
    cur.close()
    conn.close()

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
"""


def insert_db(registers):
    if registers:
        for idx, reg in enumerate(registers):
            #combined[cam] = {'acceso_id': "QN_CP_1", 'nombre_comercial_acceso': "EL COMERCIO", 'timestamp': timestamp, 'date': date, 'year': year, 'month': month, 'day': day, 'hour': hour, 'in': ingreso, 'out': salida}
            print(f"{idx:<2} ||   {reg['id_cc']}   ||  {reg['id_cam']}  ||  {reg['acceso_id']}  ||       {reg['nombre_comercial_acceso']}       || {reg['timestamp']} || {reg['date']} || {reg['year']} ||    {reg['month']}  ||   {reg['day']} ||   {reg['hour']}  ||    {reg['in']}     ||    {reg['out']}    ||")

# ------------------------------------------------------- KAFKA FUNCTIONS ----------------------------------------

def construct_register(messages):
    combined = {}
    if messages:
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
            
            
            if cam in combined.keys():
                    combined[cam]['in'] += ingreso
                    combined[cam]['out'] += salida
            else:
                timestamp = datetime.datetime.now()
                date = timestamp.strftime("%Y-%m-%d")
                time = timestamp.strftime("%H:%M:%S")
                year = timestamp.year
                month = timestamp.month
                day = timestamp.day
                hour = timestamp.hour
                combined[cam] = {'id_cc': 1, 'id_cam': cam, 'acceso_id': "QN_CP_1", 'nombre_comercial_acceso': "EL COMERCIO", 'timestamp': timestamp, 'date': date, 'year': year, 'month': month, 'day': day, 'hour': hour, 'in': ingreso, 'out': salida}

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