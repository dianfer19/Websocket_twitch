import asyncio
import json
import os
import ssl
import sys
import uuid

import websockets

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

dispositivos_conectados = {}


async def registro_cliente(websocket):
    cliente_id = uuid.uuid4()
    dispositivos_conectados[cliente_id] = websocket
    print(f'Cliente {cliente_id} Conectado')
    return cliente_id


async def deshacer_registro(cliente_id):
    dispositivos_conectados.pop(cliente_id, None)


async def listen(websocket):
    cliente_id = await registro_cliente(websocket)
    try:
        async for mensaje in websocket:
            for cliente, client_websocket in dispositivos_conectados.items():
                # if cliente_id != cliente:
                print(f"{cliente} dice:{mensaje}")
                await client_websocket.send(json.dumps({'cliente_id': str(cliente), "mensaje": mensaje}))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Cliente Desconectado: {cliente_id}")
    finally:
        await deshacer_registro(cliente_id)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    os.path.join(application_path, 'mycert.crt'),
    os.path.join(application_path, 'mykey.key')
)
start_server = websockets.serve(listen, '192.168.2.104',
                                '2000', ssl=ssl_context)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
