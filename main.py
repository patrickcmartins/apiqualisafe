from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from pyami_asterisk import AMIClient
from datetime import datetime
import mysql.connector


class Usuario(BaseModel):
    id_usuario: str
    usuario: str
    id_fila: str

class ASTAMI():
    def callback_originate(events):
        print(events)

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
        
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="8WrXeMbg8tUppBsd",
        database="mbilling"
        )
        
        mycursor = mydb.cursor()

        mycursor.execute("SELECT number AS numero FROM pkg_phonenumber WHERE status = 1 LIMIT 100")

        resposta = mycursor.fetchall()
        
        final = [list(i) for i in resposta]
        
        return final

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