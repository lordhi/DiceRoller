import discord
import diceparser

client = discord.Client()

helpMessage = '''Here you go, {0}
		To roll a d20, just say 'roll'
		If you want to roll with advantage, just add a + ('roll +')
		If you need disadvantage, use a - ('roll -')\r\n
		To roll a statblock, just say 'roll stats'. (This rolls 4d6 and drops the lowest)
		To roll a statblock weirdly, say 'roll stats odd' (This rolls 5d4s)
		If you'd like a combination, 'roll stats x' will roll 6 stats, with x rolled using 4d6 drop the lowest\r\n
		If you need to use fancier dice, just state what you want ('roll 10d10')
		When rolling like this, you can add rolls together ('roll 1d20 + 1d4 + 1')
		Spaces are ignored, some other basic maths is supported, and dice rolls can be chained!\r\n
		For example, if you're unsure what die you want to roll, you can roll a die for that.
		To roll a die between 4 and 10 sides, you can just say 'roll 1d(3+1d7)'
		Try it out, and let me know if there are any features you'd like added.'''

@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
	global GMsopen
	if message.author == client.user:
		return
		
	elif message.content.startswith("roll"):
		await handleRoll(message.content[4:].replace(" ", ""), message)

	elif isGM(message.author):
		if message.content.startswith("fudge"):
			await handleFudge(message.content[6:], message)
		if message.content.startswith("Open GM"):
			print("GMs open")
			GMsopen = True
		if message.content.startswith("Close GM"):
			print("GMs closed")
			GMsopen = False

	elif GMsopen:
		if message.content.startswith("GM me"):
			if not isGM(message.author):
				GMs.append((str(message.author), message.author.id))
				writeGMs()
		

async def handleFudge(tmp, message):
	if tmp.startswith("high"):
		if len(tmp) > 4:
			val = int(tmp[5:])
		else:
			val = 1

		diceparser.fudgehigh = val
		diceparser.fudgemiddle = 0
		diceparser.fudgelow = 0

	if tmp.startswith("low"):
		if len(tmp) > 3:
			val = int(tmp[4:])
		else:
			val = 1

		diceparser.fudgehigh = 0
		diceparser.fudgemiddle = 0
		diceparser.fudgelow = val

	if tmp.startswith("middle"):
		if len(tmp) > 6:
			val = int(tmp[7:])
		else:
			val = 1

		diceparser.fudgehigh = 0
		diceparser.fudgemiddle = val
		diceparser.fudgelow = 0

async def handleRoll(tmp, message):
	if tmp == "help":
		await message.channel.send(helpMessage.format(str(message.author).split("#")[0]))
		await deleteMessage(message)
	elif tmp.startswith("stats"):
		await handleStats(tmp[5::], message)
	elif tmp == "":
		await sendMessage(message, str(diceparser.rollDie(20)), False)
	elif tmp == "+" or tmp == "-":
		await handleAdDis(tmp, message)
	else:
		await handleArbitraryRoll(tmp, message)

async def handleArbitraryRoll(tmp, message):
	try:
		for comp in ["<=", ">=", "!=", "==", "=", "<", ">", "beats", "beat", "<>"]:
			if comp in tmp:
				await handleComparison(tmp, comp, message)
				return None

		x = diceparser.parse(tmp)

		if len(str(x)) >= 2000:
			await sendMessage(message, "The history was too long to display.\r\nYour result is {0}.".format(x.val))
		else:
			await sendMessage(message, str(x))
	except Exception as e:
		await sendMessage(message, str(e))

async def handleComparison(tmp, comp, message):
	comparison = compStringToFunction(comp)
	tmp = tmp.split(comp)
	if tmp[1][-1] == ")":		#If the message ends with a bracket, then we try do multiple things
		tmp[1] = tmp[1][0:-1]	#Removes the bracket

		seperateQuantity = tmp[0].split("(", 1)
		tmp[0] = seperateQuantity[1]
		
		quantity = diceparser.parse(seperateQuantity[0])
		x = []
		msg = quantity.str_not_end()
		for i in range(quantity.val):
			x.append(comparison(diceparser.parse(tmp[0]), diceparser.parse(tmp[1])))
			msg += x[-1].str_not_end()

		successes = sum(y.val for y in x)
		if successes == 1:
			ans = "\r\nOne success!"
		elif successes > 1:
			ans = "\r\n{0} successes!".format(successes)
		else:
			ans = "\r\nNo successes. :("

		msg += ans + "\r\n----------------------"

		if len(str(x)) >= 2000:
			await sendMessage(message, "The history was too long to display.\r\nYour result is {0}.".format(x.val))
		else:
			await sendMessage(message, msg)

	else:
		x = comparison(diceparser.parse(tmp[0]), diceparser.parse(tmp[1]))
		if len(str(x)) >= 2000:
			await sendMessage(message, "The history was too long to display.\r\nYour result is {0}.".format(x.val))
		else:
			await sendMessage(message, str(x))

async def handleAdDis(tmp, message):
	rolls = [diceparser.rollDie(20), diceparser.rollDie(20)]

	ans = " ({0}, {1})".format(rolls[0], rolls[1])
	if tmp == "+":
		message.content = message.content.replace("+", "with advantage")
		await sendMessage(message, str(max(rolls)) + ans)
	elif tmp == "-":
		message.content = message.content.replace("-", "with disadvantage")
		await sendMessage(message, str(min(rolls)) + ans)

async def handleStats(tmp, message):
	diceparser.killFudge()
	if tmp == "":
		await roll_4d6(message)
	elif tmp == "odd":
		await roll_6d4(message)
	else:
		try:
			d6s = int(tmp)
			await rollCombo(message, d6s)
		except Exception as e:
			await message.channel.send(e)	

async def roll_4d6(message):
	stats = []
	for i in range(6):
		stats.append(sum(sorted([diceparser.rollDie(6) for x in range(4)])[1:]))
	
	saveStats(stats, message.author, "4d6 drop lowest")
	await message.channel.send("{0}, your stats are ({1}) with d6s".format(str(message.author).split("#")[0], str(stats)[1:-1]))
	await deleteMessage(message)

async def roll_6d4(message):
	stats = []
	for i in range(6):
		stats.append(sum(sorted([diceparser.rollDie(4) for x in range(6)])[:-1]))

	saveStats(stats, message.author, "6d4 drop highest")
	await message.channel.send("{0}, your stats are ({1}) with d4s".format(str(message.author).split("#")[0], str(stats)[1:-1]))
	await deleteMessage(message)

async def rollCombo(message, d6s):
	if d6s > 6:
		await deleteMessage(message)
		raise Exception("Attempted to roll more than 6 stats with d6s. Please try select a number less than 6")
	if d6s < 0:
		raise Exception("{0}, what the fuck are you trying to do? You can't roll a negative amount of dice.".format(str(message.author).split("#")[0]))
		await deleteMessage(message)
	diceparser.killFudge()
	stats = []
	for i in range(d6s):
		stats.append(sum(sorted([diceparser.rollDie(6) for x in range(4)])[1:]))
	for i in range(6-d6s):
		stats.append(sum(sorted([diceparser.rollDie(4) for x in range(6)])[:-1]))
	saveStats(stats, message.author, "Combo: {0} with d6s".format(d6s))
	await message.channel.send("{0}, your stats are ({1}), with {2} rolled with d6s".format(str(message.author).split("#")[0], str(stats)[1:-1], d6s))
	await deleteMessage(message)


async def sendMessage(message, text, newline=True):
	preamble = str(message.author).split("#")[0] + " " + message.content.replace("roll", "rolled")
	if newline:
		preamble += "\r\n"
	else:
		preamble += " "
	await message.channel.send(preamble + text)
	await deleteMessage(message)

async def deleteMessage(message):
	try:
		message.channel.guild
		await message.delete()
	except Exception as e:
		pass

def compStringToFunction(comp):
	if comp == ">=" or comp == "beat" or comp=="beats":
		return lambda x,y: x>=y
	if comp == "<=":
		return lambda x,y: x<=y
	if comp == "<":
		return lambda x,y: x<y
	if comp == ">":
		return lambda x,y: x>y
	if comp == "=" or comp == "==":
		return lambda x,y: x==y
	if comp == "<>" or comp == "!=":
		return lambda x,y: x!=y

def saveStats(stats, author, style):
	if not author.id == 428932819021070346:
		with open(StatsFile, 'a') as file:
			file.write("{0} : {1} : {2}\r\n".format(author, style, stats))

def writeGMs():
	with open(GMfile, 'w+') as file:
		for gm in GMs:
			file.write("{0}: {1}\r\n".format(gm[0], gm[1]))

def readGMs():
	try:
		with open(GMfile, 'r') as file:
			GMs = []
			for line in file:
				line = line.strip().split(": ")
				line[1] = int(line[1])
				GMs.append(line)

		return GMs
	except Exception as e:
		return []

def isGM(author):
	for gm in GMs:
		if author.id == gm[1]:
			return True
	return False

GMfile = "GMs.txt"
StatsFile = "stathistory.txt"
GMs = readGMs()
global GMsopen
GMsopen = True

client.run("")