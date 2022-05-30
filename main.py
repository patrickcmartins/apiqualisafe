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
        ASTAMI.ami.create_action(
        {
            "Action": "QueuePause",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
            "Paused": "true",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()

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
        ASTAMI.ami.create_action(
        {
            "Action": "QueueRemove",
            "Interface": "SIP/" + telefonista,
            "Queue": "URA-BRADESCO",
        },
        ASTAMI.callback_originate,
        )
        ASTAMI.ami.connect()

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
    ASTAMI.logout(usuario.usuario)
    return usuario

@app.post("/pausa")
def pausa(usuario: Usuario):
    ASTAMI.pause_queue(usuario.usuario)
    return usuario

@app.post("/despausa")
def despausa(usuario: Usuario):
    ASTAMI.unpause_queue(usuario.usuario)
    return usuario