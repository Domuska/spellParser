import re, json, uuid, unicodedata

#used for parsing spell data that is gotten from http://www.13thagesrd.com
#usage: 
#import parse_spell as p
#p.parse_spell("color_spray.txt")

def convert_spells_to_json(fileName, targetFileName):
	with open(fileName) as f:
		lines = [line.rstrip('\n') for line in open(fileName)]
	
	allSpells = []
	
	#find a single spell, the spells should be separated by $ symbol
	spell = []
	for line in lines:
		if '$' in line:
			print("$ found, spell ended")
			spell.append("spellLevel: " + str(spellLevel))
			allSpells.append(spell)
			spell = []
		elif "Level Spells" in line:
			spellLevel = line
			#add an extra empty line, we depend on line number to get spell name (since the line has no other identifier), hopefully it works.
			spell.append("")
		else:
			spell.append(line)
	
	#add the last spell as well
	allSpells.append(spell)
	
	#first write the opening bracket to the file
	file = open(targetFileName, "a")
	file.write("{")
	#write the spells we parsed earlier
	for spell in allSpells[:-1]:
		identifier = uuid.uuid4()
		file.write("\"" + str(identifier) + "\":")
		file.write(json.dumps(parse_spell(spell)))
		file.write(",")
	#write last element without a ,
	identifier = uuid.uuid4()
	file.write("\"" + str(identifier) + "\":")
	file.write(json.dumps(parse_spell(allSpells[-1])))
	#add closing bracket
	file.write("}")
		
		
	#print("\n\n")
	#print(lines)
	#with open("spells.txt", "a") as file:
	#	file.write(json.dumps(dict))
	

#used for parsing a single spells
#takes in an array with the lines of the spell in it
#returns a dictionary with the proper json field names as keys and values parsed from rows of the list
def parse_spell(lines):
	#with open(fileName) as f:
	#	lines = [line.rstrip('\n') for line in open(fileName)]
		
	#print(lines)
	
	dict = {}
	#set name first
	dict["name"] = lines[1]
	
	i = 1
	for line in lines:
	
		#if spell is close-quarters, the recharge time is on the next row.
		#if it is ranged spell, the recharge time is on same row after symbol ;
		if "Close-quarters spell" in line:
			print ("close-quarters spell")
			dict["attackType"] = "Close-quarters"
			dict["rechargeTime"] = lines[5]
		elif "Ranged spell" in line:
			print("ranged spell")
			dict["attackType"] = "Ranged spell"
			dict["rechargeTime"] = re.sub(r'.*;', '', lines[3])
			
		#targets, such as Target: One nearby enemy
		if line.startswith("Target", 0, 6):
			line = cleanUnicodeFromString(line)
			dict["target"] = removeMetaText(line)
		
		#attack roll, such as Attack: Wisdom + Level vs. PD
		if line.startswith("Attack", 0, 6):
			line = cleanUnicodeFromString(line)
			dict["attackRoll"] = removeMetaText(line)
		
		#handle hit or effect portion, they go to same field. Clerics can have Cast for Power or Cast for Broad Effect, those in here too
		if line.startswith("Hit", 0, 3) or line.startswith("Effect", 0, 6) or line.startswith("Cast for", 0, 8):
			print(line)
			line = cleanUnicodeFromString(line)
			if "hitDamageOrEffect" in dict:
				dict["hitDamageOrEffect"] = dict["hitDamageOrEffect"] + "\n" + line
			else:
				dict["hitDamageOrEffect"] = removeMetaText(line)
				
		#add higher level effects to the effect field as well
		if line.startswith("3rd", 0, 3) or line.startswith("5th", 0, 3) or line.startswith("7th", 0, 3) or line.startswith("9th", 0, 3):
			line = cleanUnicodeFromString(line)
			dict["hitDamageOrEffect"] = dict["hitDamageOrEffect"] + "\n" + line
		
		if line.startswith("Miss", 0, 4):
			line = cleanUnicodeFromString(line)
			print("line starts with Miss: " + line)
			dict["missDamage"] = removeMetaText(line)
		
		#lines that are only in few places, such as with chain spells or charm person.
		if line.startswith("Special", 0, 7) or line.startswith("Chain", 0, 5) or line.startswith("Limited", 0, 7): 
			line = cleanUnicodeFromString(line)
			if "notes" in dict:
				dict["notes"] = dict["notes"] + "\n" + line
			else:
				dict["notes"] = line
		
		#handle feats
		if line.startswith("Adventurer", 0, 10):
			line = cleanUnicodeFromString(line)
			#remove the text "Adventurer Feat" from the string
			line = re.sub(r'.*Adventurer Feat ', '', line)
			#don't add the first symbol, which will be whitespace since above regex only removes the text
			dict["adventurerFeat"] = line
			
		if line.startswith("Champion", 0, 8):
			line = cleanUnicodeFromString(line)
			line = re.sub(r'.*Champion Feat ', '', line)
			dict["championFeat"] = line
			
		if line.startswith("Epic", 0, 5):
			line = cleanUnicodeFromString(line)
			line = re.sub(r'.*Epic Feat ', '', line)
			dict["epicFeat"] = line
				
		#add spell group (level) that should be added at convert_spells_to_json
		if line.startswith("spellLevel", 0, 10):
			dict["groupName"] = removeMetaText(line)
		i += 1
		
	return dict
	
def removeMetaText(text):
	lineText = re.sub(r'.*:', '', text)
	#remove first character since regex above leaves an empty space
	return lineText[1:]

#method for removing \u unicode string elements from text. Most likely not the best solution but eh, it works.
def cleanUnicodeFromString(text):
	#text.replace("\u00e2\u20ac\u2122", "AAAAAAA")
	#text.decode('unicode_escape').encode('ascii', 'ignore')
	print (text)
	if "\u00e2\u20ac\u02dc" in text:
		text = text.replace("\u00e2\u20ac\u02dc", "'")
	if "\u00e2\u20ac\u2122" in text:
		text = text.replace("\u00e2\u20ac\u2122", "'")
	if "\u00e2\u20ac\u201c" in text:
		text = text.replace("\u00e2\u20ac\u201c", "-")
	return text
