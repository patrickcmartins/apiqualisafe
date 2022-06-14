from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from pyami_asterisk import AMIClient
from datetime import datetime
import mysql.connector
import requests
from random import randint
import os


class Usuario(BaseModel):
    id_usuario: str
    usuario: str
    id_fila: str

class ASTAMI():
    def callback_originate(events):
        return events
        
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8WrXeMbg8tUppBsd",
    database="mbilling"
    )

    ami = AMIClient(host='127.0.0.1', port=5038, username='magnus', secret='magnussolution')

    def pause_queue(telefonista):
        resposta = ASTAMI.ami.create_action(
        {
            "Action": "QueuePause",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
            "Paused": "true",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()
        return resposta

    def unpause_queue(telefonista):
        resposta = ASTAMI.ami.create_action(
        {
            "Action": "QueuePause",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
            "Paused": "false",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()
        return resposta

    def login(telefonista):
        resposta = ASTAMI.ami.create_action(
        {
            "Action": "QueueAdd",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
            "Paused": "false",

        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect() 
        return resposta

    def logout(telefonista):
        resposta = ASTAMI.ami.create_action(
        {
            "Action": "QueueRemove",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()
        return resposta
    
    def retornaNumeros():
        hoje = datetime.today().strftime('%Y-%m-%d')
        
        mycursor = ASTAMI.mydb.cursor()

        mycursor.execute("SELECT number AS numero, id as id_oportunidade FROM pkg_phonenumber WHERE status = 1 LIMIT 100")

        # final = [item[0] for item in mycursor.fetchall()] +  [item[1] for item in mycursor.fetchall()]
        
        final = mycursor.fetchall()
        
        return final
    
    def fila():
        hoje = datetime.today().strftime('%Y-%m-%d')
        
        mycursor = ASTAMI.mydb.cursor()

        mycursor.execute("SELECT callerId AS numero, status, agentName AS operador, time AS darahora FROM pkg_queue_status ")

        final = mycursor.fetchall()
        
        return final
    
    
    def numerosFila():
        resposta = ASTAMI.ami.create_action(
        {
            "Action": "QueueStatus",
            "Queue": "URA-BRADESCO",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()
        return resposta
    
    def verificaWhatsapp(numero):
        url = "https://msging.net/commands"

        payload = "{\r\n \"id\": \"55" + str(numero) + "_" + str(randint(111111111111111111,999999999999999999)) + "\",\r\n \"to\": \"postmaster@wa.gw.msging.net\",\r\n \"method\": \"get\",\r\n \"uri\": \"lime://wa.gw.msging.net/accounts/+" + str(numero) + "\"\r\n}"        
        headers = {
        'Content-Type': 'application/json; charset=utf8',
        'Authorization': '',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        jsonResponse = response.json()

        if(jsonResponse["status"] == "success" ):

            mycursor = ASTAMI.mydb.cursor()
            sql = "INSERT INTO pkg_phonenumber (`id_phonebook`, `number`) VALUES  (%s, %s)"
            values = (2, numero)

            mycursor.execute(sql, values)
            ASTAMI.mydb.commit()

            print(mycursor.rowcount, " registros inseridos")

        print(jsonResponse["status"])
        return jsonResponse["status"]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/login")
def login(usuario: Usuario):
    saida = ASTAMI.login(usuario.usuario)
    return "true", 200

@app.post("/logout")
def logout(usuario: Usuario):
    saida = ASTAMI.logout(usuario.usuario)
    return "true", 200

@app.get("/filasum")
def filasum():
    statusFila = ASTAMI.fila()
    jsonResposta = jsonable_encoder(statusFila)
    headers = {"Access-Control-Allow-Origin": '*'}
    return JSONResponse(content=jsonResposta, headers=headers)

@app.post("/pausa")
def pausa(usuario: Usuario):
    saida = ASTAMI.pause_queue(usuario.usuario)
    return "true", 200

@app.post("/despausa")
def despausa(usuario: Usuario):
    saida = ASTAMI.unpause_queue(usuario.usuario)
    return "true", 200

@app.get("/numeros")
def numerosAtivos():
    numeros = ASTAMI.retornaNumeros()
    jsonResposta = jsonable_encoder(numeros)
    headers = {"Access-Control-Allow-Origin": '*'}
    return JSONResponse(content=numeros, headers=headers)

@app.get("/whatsapp/{numero}")
async def whatsappInsere(numero):
    ASTAMI.verificaWhatsapp(numero)
    return JSONResponse(content="bosta")

# {'Response': 'Success', 'ActionID': 'action/243ccc6b-9fad-4466-ba44-61113584dc3b/1/1', 'EventList': 'start', 'Message': 'Queue status will follow'}
# {'Event': 'QueueParams', 'Queue': 'URA-BRADESCO', 'Max': '0', 'Strategy': 'rrmemory', 'Calls': '1', 'Holdtime': '0', 'TalkTime': '39', 'Completed': '19', 'Abandoned': '0', 'ServiceLevel': '0', 'ServicelevelPerf': '15.8', 'Weight': '0', 'ActionID': 'action/243ccc6b-9fad-4466-ba44-61113584dc3b/1/1'}
# {'Event': 'QueueMember', 'Queue': 'URA-BRADESCO', 'Name': 'SIP/telefonista10', 'Location': 'SIP/telefonista10', 'StateInterface': 'SIP/telefonista10', 'Membership': 'dynamic', 'Penalty': '0', 'CallsTaken': '0', 'LastCall': '0', 'InCall': '0', 'Status': '1', 'Paused': '1', 'PausedReason': '', 'ActionID': 'action/243ccc6b-9fad-4466-ba44-61113584dc3b/1/1'}
# {'Event': 'QueueEntry', 'Queue': 'URA-BRADESCO', 'Position': '1', 'Channel': 'SIP/telefonista102-2-0005780d', 'Uniqueid': '1654627863.358413', 'CallerIDNum': '5543991332449', 'CallerIDName': 'unknown', 'ConnectedLineNum': 'unknown', 'ConnectedLineName': 'unknown', 'Wait': '427', 'Priority': '0', 'ActionID': 'action/243ccc6b-9fad-4466-ba44-61113584dc3b/1/1'}
# {'Event': 'QueueStatusComplete', 'ActionID': 'action/243ccc6b-9fad-4466-ba44-61113584dc3b/1/1', 'EventList': 'Complete', 'ListItems': '3'}
