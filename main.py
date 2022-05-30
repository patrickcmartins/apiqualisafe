from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from pyami_asterisk import AMIClient

class Usuario(BaseModel):
    id_usuario: str
    usuario: str
    id_fila: str

class ASTAMI():
    def callback_originate(events):
        return events

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

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/login")
def login(usuario: Usuario):
    saida = ASTAMI.login(usuario.usuario)
    return saida

@app.post("/logout")
def logout(usuario: Usuario):
    saida = ASTAMI.logout(usuario.usuario)
    return saida

@app.post("/pausa")
def pausa(usuario: Usuario):
    saida = ASTAMI.pause_queue(usuario.usuario)
    return saida

@app.post("/despausa")
def despausa(usuario: Usuario):
    saida = ASTAMI.unpause_queue(usuario.usuario)
    return saida