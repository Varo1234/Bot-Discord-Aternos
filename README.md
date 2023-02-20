# Bot-Discord-Aternos
Bot de Discord para encender/apagar servidores de Minecraft en Aternos

## Para python 3.10

### Instalar el archivo de requerimientos:
```bash
pip install -r requirements.txt
```

### Modifica el archivo credentials.json con tus credenciales (claves) para que funcione el bot

#### Bot-Discord-Aternos\credentials.json
```json

{
    "credentials": {
        "discord_bot": "Token de bot de discord",
        "discord_channel": tu ID de canal ,
        "aternos_user": "Usuario de aternos",
        "aternos_pwsd": "Contraseña de aternos",
	  "n_servidor": Numero de servidor,
    }
}
```
## Servicio Inicio/apagado
El bot solo soporta un websocket, por lo que solo es posible que te avise si se prendio o apago un solo servidor, y tendras que añadir el numero se servidor empezando desde el 0 en srv_ws en el archivo de credentials.json, default (0)

## Los comandos:

1.- $servidores                 -> Muestra la lista de servidores

2.- $info [n° de servidor]      -> Muestra la información del servidor seleccionado

3.- $estatus [n° de servidor]   -> Muestra el estatus del servidor seleccionado

4.- $inicio [n° de servidor]    -> Inicia el servidor seleccionado (tendrás que esperar a que inicie el servidor, cuando se inicie por completo te avisará)

5.- $apagar [n° de servidor]	  -> Apaga el servidor seleccionado

6.- $reinicio [n° de servidor]  -> Reinicia el servidor seleccionado

7.- $jugadores [n° de servidor] -> Muestra los jugadores del servidor

### El prefijo por defecto para usar los comandos es "$"
Para cambiarlo tendras que editar el archivo bot.py el valor prefix
