import re, json, uuid, unicodedata, os, sys, codecs

#used for parsing spell data that is gotten from http://www.13thagesrd.com
#usage: 
#import parse_spell as p
#p.create_spell_list()
#this will create a file allSpells.json in folder you're currently in. This requires that you have properly
#formatted text files (look at file names in create_spell_list() under data/ folder of your current location.
#you can create only a single spell list by calling
# p.convert("source text file.txt", "name of power list", "target file name"
#this will create a new file using the third argument as name for the file to where you're currently in, and
#create allSpells.json to folder you're currently in. It will only append to both files if they already exist.

'''
The source data needs to be in following format:

name of power is on the second row of the power

rows with separate data, such has hit, effect, adventurer feat etc need to be on their own rows

powers need to be separated by $, and after this there needs to be one row (can have text or not), see above

'''

def create_spell_list():
	spell_lists = [("bard.txt", "Bard's Spells"),
				   ("cleric.txt", "Cleric's Spells"),
				   ("fighter.txt", "Fighter's Maneuvers"),
				   ("rogue.txt", "Rogue's Powers"),
				   ("sorcerer.txt", "Sorcerer's Spells"),
				   ("wizard.txt", "Wizard's Spells"),
				   ("commander.txt", "Commander's Powers"),
				   ("monk.txt", "Monk's Forms"),
				   ("druid_terrainCaster.txt", "Druid's Terrain Caster Spells"),
				   ("druid_elementalCaster.txt", "Druid's Elemental Caster Spells"),
				   ("animalCompanionSpells.txt", "Animal Companion Spells"),
				   ("occultist.txt", "Occultist's Spells"),
				   ("necromancer.txt", "Necromancer's Spells"),
				   ("chaosMage.txt", "Chaos Mage's Spells")]

	for list_tuple in spell_lists:
		convert(list_tuple[0], list_tuple[1])

'''
	The main method used for converting spells from text file to json.
	Method reads existing data and appends to file allSpells.json
	First argument is a text file in /data folder under where this program is run.
	Second argument is the name of the power list that will be written to the DB
	Third argument is optional file name, if this is supplied the spells are also written to the file
'''
def convert(fileName, powerListName, targetFileName=None):

	fileName = os.path.join("data", fileName)
	print(fileName)
	#with open(fileName, encoding="utf8") as f:
	lines = [line.rstrip('\n') for line in open(fileName, encoding="utf8")]
	
	allSpells = []

	powerListId = str(uuid.uuid4())
	
	#find a single spell, the spells should be separated by $ symbol
	spell = []
	for line in lines:
		#spells are separated with $
		if '$' in line:
			#print("$ found, spell ended")
			spell.append("spellLevel: " + str(spellLevel))
			allSpells.append(spell)
			spell = []
		#lines can have "1st Level Spells", that means spells below this line belong to 1st level
		elif "Level Spells" in line  or "Invocations" in line  or "Level Battle Cries" in line \
				or "Level Songs" in line or "Maneuvers" in line or "Powers" in line\
				or "Level Tactics" in line or "Level Commands" in line\
				or "Adventurer Tier" in line or "Champion Tier" in line or "Epic Tier" in line\
				or "Cave, Dungeon, Underworld" in line or "Forest, Woods" in line \
				or line.startswith("Ice, Tundra", 0, 11) or line.startswith("Migration Route", 0, 15)\
				or line.startswith("Mountains", 0, 10) or line.startswith("Plains", 0, 6)\
				or line.startswith("Ruins", 0, 5) or line.startswith("Swamp, Lake", 0, 11)\
				or line.startswith("Elemental Mastery Spells", 0, 24)\
				or line.startswith("Attack Spells", 0, 13) or line.startswith("Defense Spells", 0, 14)\
				or line.startswith("Blood of Warriors", 0, 17) or line.startswith("Light of the High Ones", 0, 22)\
				or line.startswith("Twisted Path", 0, 12):
			spellLevel = cleanUnicodeFromString(line)
			print(spellLevel)
			#print("Spell level found!" + spellLevel)
			#add an extra empty line, we depend on line number to get spell name (since the line has no other identifier), hopefully it works.
			spell.append("")
		#otherwise just add a new line to the array containing spell's rows
		else:
			spell.append(line)
	
	#add the last spell as well
	spell.append("spellLevel: " + str(spellLevel))
	allSpells.append(spell)

	if os.stat("allSpells.json").st_size > 0:
		#read the existing data
		with open("allSpells.json") as data_file:
			database = json.load(data_file)
	else:
		database = {}

	# table for saving single spells
	if "spells" in database:
		spellsTable = database["spells"]
	else:
		spellsTable = {}

	if "spell_lists" not in database:
		database["spell_lists"] = {}
	# table for saving power IDs in a spell book (such as all wizard or sorcerer spells)
	spellBooksTable = {}

	if "spell_groups" not in database:
		database["spell_groups"] = {}
	#table for saving the groups in helper table, save power names and IDs inside groups
	#powerGroupsTable = database["spell_groups"][powerListId]
	powerGroupsTable = {}

	#first write the opening bracket to the file
	#file = open(targetFileName, "a")
	#file.write("{")
	#write the spells we parsed earlier
	#for spell in allSpells[:-1]:
	for spell in allSpells:
		spellId = str(uuid.uuid4())
		#file.write("\"" + str(spellId) + "\":")
		#file.write(json.dumps(parse_spell(spell)))
		#file.write(",")
		parsedSpell = parse_spell(spell, powerListId)
		spellsTable[spellId] = parsedSpell
		spellBooksTable[spellId] = True
		groupName = parsedSpell["groupName"]
		powerName = parsedSpell["name"]
		if groupName not in powerGroupsTable:
			powerGroupsTable[groupName] = {}
		powerGroupsTable[groupName][spellId] = {}
		powerGroupsTable[groupName][spellId][powerName] = True
		#powerGroupsTable[groupName][spellId][powerName] = "true"

	database["spells"] = spellsTable

	database["spell_lists"][powerListId] = {}
	database["spell_lists"][powerListId]["name"] = powerListName
	database["spell_lists"][powerListId]["spells"] = spellBooksTable

	database["spell_groups"][powerListId] = powerGroupsTable
	#write the new database to json file
	with open("allSpells.json", "w") as data_file:
		json.dump(database, data_file, indent=2)

	if targetFileName is not None:
		with open(targetFileName, "w") as file:
			json.dump(spellsTable, file, indent=2)

	#write last element without a ,
	#spellId = uuid.uuid4()
	#file.write("\"" + str(spellId) + "\":")
	#file.write(json.dumps(parse_spell(allSpells[-1])))
	#add closing bracket
	#file.write("}")
		
		
	#print("\n\n")
	#print(lines)
	#with open("spells.txt", "a") as file:
	#	file.write(json.dumps(dict))
	data_file.close()

#used for parsing a single spells
#takes in an array with the lines of the spell in it
#returns a dictionary with the proper json field names as keys and values parsed from rows of the list
def parse_spell(lines, powerListId):
	#with open(fileName) as f:
	#	lines = [line.rstrip('\n') for line in open(fileName)]
		
	#print(lines)
	
	powerDictionary = {}
	#set name first
	powerDictionary["name"] = cleanUnicodeFromString(lines[1])
	uprint(powerDictionary['name'])
	
	i = 1
	for line in lines:
		#for sorcerer, wizard, bard and cleric spells
		#if spell is close-quarters, the recharge time is on another row
		#if it is ranged spell, the recharge time is on same row after symbol ;
		if "Close-quarters spell" in line:
			#print ("close-quarters spell")
			powerDictionary["attackType"] = line
			#dict["rechargeTime"] = lines[5]
		elif "Ranged spell" in line:
			print("ranged spell")
			powerDictionary["attackType"] = "Ranged spell"
			powerDictionary["rechargeTime"] = re.sub(r'.*;', '', lines[3])
		#add momentum to rechargetime so later we will know to add momentum to the rechargetime row
		#if line.startswith("Momentum", 0, 8):
		#	powerDictionary["rechargeTime"] = "momentum"
		
		#Set the recharge time. It might also have been set above, since for ranged spells recharge time is written on the same row.
		if line.startswith("Daily", 0, 5) or line.startswith("Recharge", 0, 8) \
				or line.startswith("At-Will", 0, 7) or line.startswith("Once per battle", 0, 15)\
				or line.startswith("Cyclic", 0, 6) or line.startswith("Variable"):
			line = cleanUnicodeFromString(line)
			#add requires momentum to rechargetime, in rules momentum is in its' own line but makes sense to have it here
			#if "rechargeTime" in powerDictionary and "momentum" in powerDictionary["rechargeTime"]:
			#	powerDictionary["rechargeTime"] = line + " (requires momentum)"
			#else:
			powerDictionary["rechargeTime"] = line

		#flexible (fighter, bard), ranged or melee attack powers (rogue)
		if line.startswith("Flexible", 0, 8) or line.startswith("Melee attack", 0, 12) or line.startswith("Ranged attack", 0, 13):
			line = cleanUnicodeFromString(line)
			powerDictionary["attackType"] = line
			
		#targets, such as Target: One nearby enemy. Channel Life has "Attack Target" as the target text.
		if line.startswith("Target", 0, 6) or line.startswith("Attack Target", 0, 13) or line.startswith("Healing Target", 0, 14):
			#for attack target / healing target we need to add the whole line, removing the "healing target" or "attack target"
			#text would make the spell description confusing
			if line.startswith("Attack Target", 0, 13) or line.startswith("Healing Target", 0, 14):
				if "target" in powerDictionary:
					powerDictionary["target"] = powerDictionary["target"] + "\n\n" + line
				else:
					powerDictionary["target"] = line
			else:
				line = cleanUnicodeFromString(line)
				powerDictionary["target"] = removeMetaText(line)

		#handle Slick Feint from rogue, since it has to be special. Of course.
		if line.startswith("First Target", 0, 12) or line.startswith("Second Target", 0, 13):
			if "target" not in powerDictionary:
				powerDictionary["target"] = line
			else:
				powerDictionary["target"] = powerDictionary["target"] + "\n\n" + line
		
		#attack roll, such as Attack: Wisdom + Level vs. PD
		if line.startswith("Attack", 0, 6):
			line = cleanUnicodeFromString(line)
			if "attackRoll" not in powerDictionary:
				powerDictionary["attackRoll"] = removeMetaText(line)
			else:
				powerDictionary["attackRoll"] = powerDictionary["attackRoll"] + "\n\n" + line
		
		#handle hit or effect portion, they go to same field. Clerics can have Cast for Power or Cast for Broad Effect, those in here too.
		#Bards have Opening & Sustained effect and Final Verse, add them as well
		if line.startswith("Hit:", 0, 4) or line.startswith("Natural Even Hit:", 0, 17) or line.startswith("Natural Odd Hit:", 0, 16)\
				or line.startswith("Effect", 0, 6) or line.startswith("Cast for", 0, 8) \
				or line.startswith("Opening & Sustained", 0, 19) or line.startswith("Final Verse", 0, 11)\
				or line.startswith("Hit vs.", 0, 7):
			line = cleanUnicodeFromString(line)
			print("\n\n" + "###########\n" + line + "\n\n")
			
			#handle "hit vs. ally/enemy/staggered target/xxx" and "natural even/odd" lines differently,
			#those whole lines should be added, removing text before the : symbol makes the text confusing
			if "Hit vs" in line or line.startswith("Natural Even Hit:", 0, 17) or line.startswith("Natural Odd Hit:", 0, 16):
				if "hitDamageOrEffect" in powerDictionary:
					powerDictionary["hitDamageOrEffect"] = powerDictionary["hitDamageOrEffect"] + "\n\n" + line
				else:
					powerDictionary["hitDamageOrEffect"] = line
			#handle "vampiric form" & "coronation" a bit differently,
			#they grant an attack that should be printed to the effect block
			elif "name" in powerDictionary and ("Vampiric Form" or "Coronation" in powerDictionary["name"]):
				if "hitDamageOrEffect" in powerDictionary:
					if "Attack" in line:
						powerDictionary["hitDamageOrEffect"] = powerDictionary["hitDamageOrEffect"] + "\n\n" + line.replace("Effect: ", "")
					else:
						powerDictionary["hitDamageOrEffect"] = powerDictionary["hitDamageOrEffect"] + "\n\n" + line
				else:
					powerDictionary["hitDamageOrEffect"] = removeMetaText(line)
			# check if we already have the entry in dictionary, if so just append more text to it
			elif "hitDamageOrEffect" in powerDictionary:
				powerDictionary["hitDamageOrEffect"] = powerDictionary["hitDamageOrEffect"] + "\n\n" + line
			#otherwise create a new entry to the dictionary and add the line (without the info text, such as effect:)
			else:
				powerDictionary["hitDamageOrEffect"] = removeMetaText(line)
				
		#add higher level effects to the effect field as well
		if line.startswith("3rd", 0, 3) or line.startswith("5th", 0, 3) or line.startswith("7th", 0, 3) or line.startswith("9th", 0, 3):
			line = cleanUnicodeFromString(line)
			#print("\n" + line)
			powerDictionary["hitDamageOrEffect"] = powerDictionary["hitDamageOrEffect"] + "\n\n" + line

		if "Miss" in line:
			if line.startswith("Miss", 0, 4):
				line = cleanUnicodeFromString(line)
				#uprint("line starts with Miss: " + line)
				# Slick feint from rogues can have multiple miss effects. Since it's special.
				if "missDamage" not in powerDictionary:
					line = removeMetaText(line)
					powerDictionary["missDamage"] = cleanUnicodeFromString(line)
				else:
					powerDictionary["missDamage"] = powerDictionary["missDamage"] + "\n\n" + cleanUnicodeFromString(line)
			#handle monk oddities, they have natural even and odd miss effects.
			#we need to write the whole lines to the miss field so user will know if effect is for natural even or odd.
			#the above writing will remove the "Natural Even Miss:" text from the first entry (removeMetaText does it).
			#Also Necromancer's Unholy Blasts needs this (first and second miss)
			elif line.startswith("Natural Even Miss:", 0, 18) or line.startswith("Natural Odd Miss:", 0, 17)\
				or line.startswith("First Miss", 0, 10) or line.startswith("Second Miss", 0, 11):
				if "missDamage" not in powerDictionary:
					powerDictionary["missDamage"] = cleanUnicodeFromString(line)
				else:
					powerDictionary["missDamage"] = powerDictionary["missDamage"] + "\n\n" + cleanUnicodeFromString(line)


		
		# lines that are only in few places, such as with
		# chain spells, Teleport Shield, Tumbling strike or Resurrect
		# Also add commander command cost
		if line.startswith("Chain", 0, 5) or line.startswith("Limited", 0, 7) \
				or line.startswith("Always", 0, 6) or line.startswith("Note", 0, 4)\
				or line.startswith("Cost", 0, 4)\
				or line.startswith("Limited Casting", 0, 15) or line.startswith("Limited Resurrection", 0, 21)\
				or line.startswith("Skill Check", 0, 11) or line.startswith("Retain Focus", 0, 12):
			line = cleanUnicodeFromString(line)
			if "playerNotes" in powerDictionary:
				powerDictionary["playerNotes"] = powerDictionary["playerNotes"] + "\n\n" + line
			else:
				powerDictionary["playerNotes"] = line
		#handle Resurrection a bit differently
		elif line.startswith("resurrection_note", 0, 17):
			powerDictionary["playerNotes"] = \
				powerDictionary["playerNotes"] + "\n\n" + removeMetaText(cleanUnicodeFromString(line))
		#handle spells that have tables in spell description (example Touch of Evil) a bit differently
		elif line.startswith("table_note", 0, 10):
			if "playerNotes" in powerDictionary:
				powerDictionary["playerNotes"] = \
					powerDictionary["playerNotes"] + "\n\n" + cleanUnicodeFromString(removeTableNoteText(line))
			else:
				powerDictionary["playerNotes"] = cleanUnicodeFromString(removeTableNoteText(line))

		#many spells and big portion of fighter maneuvers have Special field
		if line.startswith("Special", 0, 7):
			line = cleanUnicodeFromString(line)
			if "special" not in powerDictionary:
				powerDictionary["special"] = removeMetaText(line)
			else:
				powerDictionary["special"] = powerDictionary["special"] + "\n\n" + removeMetaText(line)
		
		#handle feats
		if line.startswith("Adventurer", 0, 10):
			line = cleanUnicodeFromString(line)
			#remove the text "Adventurer Feat " from the string
			line = re.sub(r'.*Adventurer Feat ', '', line)
			powerDictionary["adventurerFeat"] = line
			
		if line.startswith("Champion", 0, 8):
			line = cleanUnicodeFromString(line)
			line = re.sub(r'.*Champion Feat ', '', line)
			powerDictionary["championFeat"] = line
			
		if line.startswith("Epic", 0, 5):
			line = cleanUnicodeFromString(line)
			line = re.sub(r'.*Epic Feat ', '', line)
			powerDictionary["epicFeat"] = line
		
		#for example bard spells have standard action written as casting time, line also tells sustain roll needed
		if line.startswith("Standard action", 0, 15):
			line = cleanUnicodeFromString(line)
			powerDictionary["castingTime"] = line
		
		if line.startswith("Quick action", 0, 12):
			line = cleanUnicodeFromString(line)
			powerDictionary["castingTime"] = line
			
		if line.startswith("Move action", 0, 11):
			line = cleanUnicodeFromString(line)
			powerDictionary["castingTime"] = line
			
		if line.startswith("Free action", 0, 11):
			line = cleanUnicodeFromString(line)
			powerDictionary["castingTime"] = line

		if line.startswith("Interrupt", 0, 9):
			line = cleanUnicodeFromString(line)
			powerDictionary["castingTime"] = line

		#add spell group (level) that should be added at convert_spells_to_json
		if line.startswith("spellLevel", 0, 10):
			powerDictionary["groupName"] = removeMetaText(line)
		i += 1

		#rogues have trigger, flexible attacks have triggering in the line
		if line.startswith("Triggering", 0, 10) or line.startswith("Trigger", 0, 7):
			line = cleanUnicodeFromString(line)
			powerDictionary["trigger"] = removeMetaText(line)
	
	#most spells have no casting time written, at that case it's standard action.
	#Flexible attacks are not included, naturally.
	if "castingTime" not in powerDictionary:
		#print(powerDictionary["attackType"])
		if "attackType" in powerDictionary and ("Flexible" not in powerDictionary["attackType"] and "Melee attack" not in powerDictionary["attackType"] and "Ranged attack" not in powerDictionary["attackType"]):
			powerDictionary["castingTime"] = "Standard action to cast"

	#add power list id if it is supplied
	if powerListId is not None:
		powerDictionary["powerListId"] = powerListId

	return powerDictionary
	
def removeMetaText(text):
	lineText = re.sub(r'.*:', '', text)
	#remove first character since regex above leaves an empty space
	return lineText[1:]

def removeTableNoteText(text):
	return text.replace("table_note:", "")

#method for removing \u unicode string elements from text. Most likely not the best solution but eh, it works.
def cleanUnicodeFromString(text):
	#print (text)
	if "\u00e2\u20ac\u02dc" in text:
		text = text.replace("\u00e2\u20ac\u02dc", "'")
	if "\u00e2\u20ac\u2122" in text:
		text = text.replace("\u00e2\u20ac\u2122", "'")
	if "\u00e2\u20ac\u201c" in text:
		text = text.replace("\u00e2\u20ac\u201c", "-")
	if "\u00e2\u20ac\u201d" in text:
		text = text.replace("\u00e2\u20ac\u201d", "-")
	if "\u00e2\u20ac\u2122" in text:
		text = text.replace("\u00e2\u20ac\u2122", "\'")
	if "\u2019" in text:
		text = text.replace("\u2019", "\'")
	if "\u00e2\u20ac\u201d" in text:
		text = text.replace("\u00e2\u20ac\u201d", "-")
	if "\u2014" in text:
		text = text.replace("\u2014", "-")
	if "\u2013" in text:
		text = text.replace("\u2013", "-")
	if "\u201c" or "\u201d" in text:
		text = text.replace("\u201c", "\"")
		text = text.replace("\u201d", "\"")
	return text

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
	enc = file.encoding
	if enc == 'UTF-8':
		print(*objects, sep=sep, end=end, file=file)
	else:
		f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
		print(*map(f, objects), sep=sep, end=end, file=file)