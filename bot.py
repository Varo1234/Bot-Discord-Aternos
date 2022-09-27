import json
import discord
from discord.ext import commands
from python_aternos import Client, atserver, atwss

# Configuración del bot
intents = discord.Intents(messages=True, guilds=True, message_content=True)
bot = commands.Bot(command_prefix='$', intents=intents)     # Cambiar command_prefix si lo deseas

# archivo de credenciales
with open('credentials.json') as file:
    data = json.load(file)

# Credenciales para Discord y Aternos
secret_key = data["credentials"]["discord_bot"]
user = data["credentials"]["aternos_user"]
pswd = data["credentials"]["aternos_pwsd"]
channel_id = data["credentials"]["discord_channel"]

# Para websocket
aternos = Client.from_credentials(user, pswd)
srv_1 = aternos.list_servers()[0]   # Cambiar numero para websocket de servidor
socket = srv_1.wss()

print("Iniciando Bot")


def sesion(user, password):
    """Función para iniciar sesion"""
    return Client.from_credentials(user, password)


def servidores(credentials):
    """Función para obtener los servidores"""
    return credentials.list_servers()


def selec_server(srv_no):
    """Función para seleccionar el servidor deseado"""
    srv_name = int(srv_no) - 1
    i = 0
    for srv in servidores(sesion(user=user, password=pswd)):
        if i is srv_name:
            return srv
        i += 1


@bot.command(name="servidores", pass_context=True, help="Lists available servers")
@commands.has_role("Jugador")   #ROL
async def list_servers(ctx):
    """Manda la lista de servidores registrados"""
    resp = []
    i = 0
    print("Request: @server_list")
    for srv in servidores(sesion(user=user, password=pswd)):
        resp.append(str(i + 1) + ": " + srv.subdomain)
        i += 1
    await ctx.send("Los servidores registrados son: \n" + "\n".join(resp))


@bot.command(name="estatus", pass_context=True, help="States the current state of the mentioned server")
@commands.has_role("Jugador")   # ROL
async def status(ctx, srv_no):
    """Manda el estatus del servidor"""
    try:
        srv = selec_server(srv_no)
        print("Request: @status " + srv.subdomain)
        if srv is not None:
            await ctx.send(srv.subdomain + " servidor está actualmente " + srv.status)
    except IndexError:
        await ctx.send("No existe")


@bot.command(name="inicio", pass_context=True, help="Startes the mentioned server")
@commands.has_role("Jugador")   # ROl
async def start(ctx, srv_no):
    """Inicia el servidor"""
    # if 0 == int(srv_no) - 1:
    await socket.connect()
    try:
        srv = selec_server(srv_no)
        print("Request: @start  " + srv.subdomain)
        if srv.status != "online":
            srv.start()
            await ctx.send("Se iniciará el servidor: " + srv.subdomain)
        else:
            await ctx.send("El servidor está activo: " + srv.subdomain)
    except IndexError:
        await ctx.send("No existe")


@bot.command(name="reinicio", pass_context=True, help="restartes the mentioned server")
@commands.has_role("Administrador")     # ROL
async def restart(ctx, srv_no):
    """Reinicia el servidor"""
    try:
        srv = selec_server(srv_no)
        print("Request: @restart  " + srv.subdomain)
        if srv.status != "online":
            await ctx.send("Se iniciará el servidor: " + srv.subdomain)
            srv.restart()
        else:
            await ctx.send("Se reiniciará el servidor: " + srv.subdomain)
    except IndexError:
        await ctx.send("No existe")


@bot.command(name="apagar", pass_context=True, help="Stopes the mentioned server REQUIRED ROLE: MCS manager")
@commands.has_role("Administrador")     # Puedes cambiar el rol que puede parar el servidor
async def stop(ctx, srv_no):
    """Apaga el servidor"""
    try:
        srv = selec_server(srv_no)
        print("Request: @stop   " + srv.subdomain)
        if srv.status != "online":
            await ctx.send("El servidor: " + srv.subdomain + " está apagado")
        else:
            await ctx.send("Se apagará el servidor: " + srv.subdomain)
            srv.stop()
    except IndexError:
        await ctx.send("No existe")


@bot.command(name="info", pass_context=True, help="States the information about the mentioned server")
@commands.has_role("Jugador")   # ROL
async def getinfo(ctx, srv_no):
    """Retorna la principal información del servidor"""
    try:
        srv = selec_server(srv_no)
        print("Request: @getinfo")
        print('*** ' + srv.domain + ' ***' + '\n' +
              '*** Address: ' + srv.address + ' ***' + '\n' +
              '*** Status: ' + srv.status + ' ***' + '\n' +
              '*** Port: ' + str(srv.port) + ' ***' + '\n' +
              '*** Name: ' + srv.subdomain + ' ***' + '\n' +
              '*** Minecraft: ' + srv.software + srv.version + ' ***' + '\n' +
              '*** Bedrock: ' + str(srv.edition == atserver.Edition.bedrock) + ' ***' + '\n' +
              '*** Java: ' + str(srv.edition == atserver.Edition.java) + ' ***')
        await ctx.send('*** ' + srv.domain + ' ***' + '\n' +
                       '*** Dirección: ' + srv.address + ' ***' + '\n' +
                       '*** Estatus: ' + srv.status + ' ***' + '\n' +
                       '*** Puerto: ' + str(srv.port) + ' ***' + '\n' +
                       '*** Nombre: ' + srv.subdomain + ' ***' + '\n' +
                       '*** Minecraft: ' + srv.software + srv.version + ' ***' + '\n' +
                       '*** Bedrock: ' + str(srv.edition == atserver.Edition.bedrock) + ' ***' + '\n' +
                       '*** Java: ' + str(srv.edition == atserver.Edition.java) + ' ***')
    except IndexError:
        await ctx.send("No existe")


@bot.event  # para eventos
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        await ctx.send("No eres administrador")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("El comando no existe")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Menciona un servidor Ej: 1")
    else:
        print(error)


@socket.wssreceiver(atwss.Streams.console)
async def console(msg):
    """Función que retorna la consola de aternos al iniciar y apagarse, para verla completa imprime msg"""
    # print(msg)
    if 'Done' in msg:
    # if 'Timings Reset' in msg:      # Si no funciona con Timings reset, cambialo a Done
        await bot.get_channel(channel_id).send("El servidor: " + srv_1.subdomain + " está encendido")
    if 'Stopping server' in msg:
        await bot.get_channel(channel_id).send("El servidor: " + srv_1.subdomain + " se apagó")

# corre el bot con la llave de discord
bot.run(secret_key)
