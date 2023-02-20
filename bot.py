import json
import discord
from discord.ext import commands
from python_aternos import Client, atserver, atwss, Lists

# Configuración del bot
prefix = '$'  # Cambiar command_prefix si lo deseas
intents = discord.Intents(messages=True, guilds=True, message_content=True)
bot = commands.Bot(command_prefix=prefix, intents=intents)

# archivo de credenciales
with open('credentials.json') as file:
	data = json.load(file)

# Credenciales para Discord y Aternos
secret_key = data["credentials"]["discord_bot"]
user = data["credentials"]["aternos_user"]
pswd = data["credentials"]["aternos_pwsd"]
channel_id = data["credentials"]["discord_channel"]
srv_ws = data["credentials"]["n_servidor"]

# Para websocket
aternos = Client.from_credentials(user, pswd)
srv_1 = aternos.list_servers()[srv_ws]  # Cambiar numero para websocket de servidor
socket = srv_1.wss()

print("Iniciando Bot")


def sesion(user, password):
	"""Función para iniciar sesion"""
	return Client.from_credentials(user, password)


def servidores(credentials):
	"""Función para obtener los servidores"""
	return credentials.list_servers()


def selec_server(srv_no, ctx):
	"""Función para seleccionar el servidor deseado"""
	try:
		srv_name = int(srv_no) - 1
	except ValueError:
		embed = discord.Embed(
			colour=discord.Colour.dark_red(),
			title="Error de tipo",
			description=f"Hola {ctx.author.name}! el índice del servidor debe ser un número entero",
		)
		return False, embed

	srv_list = servidores(sesion(user=user, password=pswd))
	i = 0
	for srv in srv_list:
		if i == srv_name:
			return srv, False
		i += 1

	# Si el servidor no se encuentra en la lista
	embed = discord.Embed(
		colour=discord.Colour.dark_red(),
		title="Error de índice",
		description=f"Hola {ctx.author.name}! el índice del servidor no se encuentra en la lista de servidores",
	)
	return False, embed


@bot.command(name="servidores", pass_context=True, help="Lists available servers",
             description="Lista de servidores disponibles")
@commands.has_role("Jugador")  # ROL
async def list_servers(ctx):
	"""Manda la lista de servidores registrados"""
	try:
		resp = []
		i = 0
		print("Request: @server_list")
		for srv in servidores(sesion(user=user, password=pswd)):
			resp.append(str(i + 1) + ": " + srv.subdomain)
			i += 1

		embed = discord.Embed(
			colour=discord.Colour.light_gray(),
			title="Servidores",
			description=f"Hola {ctx.author.name}! Los servidores registrados son: \n" + "\n".join(resp),
		)
		await ctx.reply(embed=embed)
	except IndexError:
		await ctx.send("No existe")


@bot.command(name="jugadores", pass_context=True, help="List all players on the server",
             description="Lista de jugadores del servidor")
@commands.has_role("Jugador")  # ROL
async def list_players(ctx, srv_no):
	"""Manda la lista de jugadores en el servidor"""
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			players = srv.players(Lists.whl).list_players()
			embed = discord.Embed(
				colour=discord.Colour.greyple(),
				title="Jugadores",
				description=f"Hola {ctx.author.name}! Los jugadores del servidor son:",
			)
			for player in players:
				embed.add_field(name="Jugador", value=player, inline=False)
			await ctx.reply(embed=embed)
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		await ctx.send("No existe")


@bot.command(name="estatus", pass_context=True, help="States the current state of the mentioned server")
@commands.has_role("Jugador")  # ROL
async def status(ctx, srv_no):
	"""Manda el estatus del servidor"""
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			print("Request: @status " + srv.subdomain)
			if srv.status == "online":
				color = discord.Colour.red()
				estatus = "Encendido"
			elif srv.status == "loading starting":
				color = discord.Colour.yellow()
				estatus = "Cargando, espera solo un poco"
			else:
				color = discord.Colour.red()
				estatus = "Apagado\n\n Puedes encenderlo con el comando $inicio + el índice del servidor"
			embed = discord.Embed(
				colour=color,
				title="Estatus del servidor " + srv.subdomain,
				description=f"Hola {ctx.author.name}! \n El servidor está actualmente " + estatus,
			)
			await ctx.reply(embed=embed)
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		embed = discord.Embed(
			colour=discord.Colour.dark_red(),
			title="No existe",
			description=f"Hola {ctx.author.name}! \n El índice: " + srv_no + "no existe, te puedo mostrar la lista de "
			                                                                 "servidores con el comando $servidores "
		)
		await ctx.reply(embed=embed)


@bot.command(name="inicio", pass_context=True, help="Startes the mentioned server")
@commands.has_role("Jugador")  # ROl
async def start(ctx, srv_no):
	"""Inicia el servidor"""
	await socket.connect()
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			print("Request: @start  " + srv.subdomain)
			if srv.status != "online":
				srv.start()
				embed = discord.Embed(
					colour=discord.Colour.dark_green(),
					title="Encender " + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nSe iniciará el servidor: " + srv.subdomain
				)
				await ctx.reply(embed=embed)
			else:
				embed = discord.Embed(
					colour=discord.Colour.green(),
					title="Encender " + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nEl servidor: " + srv.subdomain + " está activo!"
				)
				await ctx.reply(embed=embed)
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		await ctx.send("No existe")


@bot.command(name="reinicio", pass_context=True, help="restartes the mentioned server")
@commands.has_role("Administrador")  # ROL
async def restart(ctx, srv_no):
	"""Reinicia el servidor"""
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			print("Request: @restart  " + srv.subdomain)
			if srv.status != "online":
				embed = discord.Embed(
					colour=discord.Colour.green(),
					title="Iniciar" + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nEl servidor: " + srv.subdomain + " se iniciará"
				)
				await ctx.reply(embed=embed)
				srv.start()
			else:
				embed = discord.Embed(
					colour=discord.Colour.green(),
					title="Reiniciar" + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nEl servidor: " + srv.subdomain + " se reiniciará"
				)
				await ctx.reply(embed=embed)
				srv.restart()
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		await ctx.send("No existe")


@bot.command(name="apagar", pass_context=True, help="Stopes the mentioned server REQUIRED ROLE: MCS manager")
@commands.has_role("Administrador")  # Puedes cambiar el rol que puede parar el servidor
async def stop(ctx, srv_no):
	"""Apaga el servidor"""
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			print("Request: @stop   " + srv.subdomain)
			if srv.status != "online":
				embed = discord.Embed(
					colour=discord.Colour.green(),
					title="Apagar" + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nEl servidor: " + srv.subdomain + " está apagado"
				)
				await ctx.reply(embed=embed)
			else:
				embed = discord.Embed(
					colour=discord.Colour.green(),
					title="Apagar" + srv.subdomain,
					description=f"Hola {ctx.author.name}! \nEl servidor: " + srv.subdomain + " se apagagará"
				)
				await ctx.reply(embed=embed)
				srv.stop()
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		await ctx.send("No existe")


@bot.command(name="info", pass_context=True, help="States the information about the mentioned server")
@commands.has_role("Jugador")  # ROL
async def getinfo(ctx, srv_no):
	"""Retorna la principal información del servidor"""
	try:
		srv = selec_server(srv_no, ctx)[0]
		embed_error = selec_server(srv_no, ctx)[1]
		if srv:
			embed = discord.Embed(
				colour=discord.Colour.blue(),
				title="Información del servidor: " + srv.subdomain,
				# description=f"Hola {ctx.author.name}! \nAqui está la información del servidor"
			)
			embed.add_field(name="Nombre", value=srv.subdomain, inline=False)
			embed.add_field(name="Dominio", value=srv.domain, inline=False)
			embed.add_field(name="Estatus", value=srv.status)
			embed.add_field(name="Puerto", value=str(srv.port))
			if srv.edition == atserver.Edition.bedrock:
				embed.add_field(name="Edición", value="Bedrock")
			else:
				embed.add_field(name="Edición", value="Java")
			embed.add_field(name="Minecraft", value=srv.software + srv.version, inline=False)
			await ctx.reply(embed=embed)
			print("Request: @getinfo")
			print('*** ' + srv.domain + ' ***' + '\n' +
			      '*** Address: ' + srv.address + ' ***' + '\n' +
			      '*** Status: ' + srv.status + ' ***' + '\n' +
			      '*** Port: ' + str(srv.port) + ' ***' + '\n' +
			      '*** Name: ' + srv.subdomain + ' ***' + '\n' +
			      '*** Minecraft: ' + srv.software + srv.version + ' ***' + '\n' +
			      '*** Bedrock: ' + str(srv.edition == atserver.Edition.bedrock) + ' ***' + '\n' +
			      '*** Java: ' + str(srv.edition == atserver.Edition.java) + ' ***')
		else:
			await ctx.reply(embed=embed_error)
	except IndexError:
		await ctx.send("No existe")


@bot.event  # para eventos
async def on_command_error(ctx, error):
	print(ctx)
	if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
		await ctx.reply(embed=discord.Embed(
			colour=discord.Colour.red(),
			title="No tienes permiso"
		))
	elif isinstance(error, commands.CommandNotFound):
		await ctx.reply(embed=discord.Embed(
			colour=discord.Colour.red(),
			title="El comando no existe"
			# description=f"Hola {ctx.author.name}! \nAqui está la información del servidor"
		))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply(embed=discord.Embed(
			colour=discord.Colour.red(),
			title="Menciona un servidor",
			description="Ej: " + prefix + "inicio 1"
		))
	else:
		await ctx.reply(embed=discord.Embed(
			colour=discord.Colour.red(),
			title="Error",
		))
		print(error)


@socket.wssreceiver(atwss.Streams.console)
async def console(msg):
	"""Función que retorna la consola de aternos al iniciar y apagarse, para verla completa imprime msg"""
	# print(msg)
	if 'Done' in msg:
		# if 'Timings Reset' in msg:      # Si no funciona con Timings reset, cambialo a Done
		embed = discord.Embed(
			colour=discord.Colour.green(),
			title="El servidor " + srv_1.subdomain + " está encendido",
			description="¡BUENA SUERTE!"
		)
		await bot.get_channel(channel_id).send(embed=embed)
	if 'Stopping server' in msg:
		embed = discord.Embed(
			colour=discord.Colour.red(),
			title="El servidor " + srv_1.subdomain + " se apagó"
		)
		await bot.get_channel(channel_id).send(embed=embed)


# Mensaje cuando el bot está en linea
@bot.event
async def on_ready():
	embed = discord.Embed(
		colour=discord.Colour.purple(),
		title="El Bot está en linea!",
		description="Estos son sus comandos:"
	)
	embed.add_field(name=prefix + "servidores", value="Muestra la lista de servidores", inline=False)
	embed.add_field(name=prefix + "info [n° de servidor]", value="Muestra la información del servidor seleccionado",
	                inline=False)
	embed.add_field(name=prefix + "estatus [n° de servidor]", value="Muestra el estatus del servidor seleccionado ",
	                inline=False)
	embed.add_field(name=prefix + "inicio [n° de servidor]", value="Inicia el servidor seleccionado (tendras que "
	                                                               "esperar a que arranque. cuando se inicie por "
	                                                               "completo te avisará) ", inline=False)
	embed.add_field(name=prefix + "jugadores [n° de servidor]", value="Muestra a los jugadores registrados del servidor", inline=False)
	await bot.get_channel(channel_id).send(embed=embed)


# corre el bot con la llave de discord
bot.run(secret_key)
