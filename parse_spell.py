import re, json

#used for parsing spell data that is gotten from http://www.13thagesrd.com
#usage: 
#import parse_spell as p
#p.parse_spell("color_spray.txt")

def parse_spell(fileName):
	with open(fileName) as f:
		lines = [line.rstrip('\n') for line in open(fileName)]
		
	print(lines)
	
	dict = {}
	#set name first
	dict["name"] = lines[0]
	
	i = 1
	for line in lines:
		#if spell is close-quarters, the recharge time is on the next row.
		#if it is ranged spell, the recharge time is on same row after symbol ;
		if "Close-quarters spell" in line:
			print ("close-quarters spell")
			dict["attackType"] = "Close-quarters"
			dict["rechargeTime"] = lines[4]
		elif "Ranged spell" in line:
			print("ranged spell")
			dict["attackType"] = "Ranged"
			dict["rechargeTime"] = re.sub(r'.*;', '', lines[2])
			
			
		if "Target" in line:
			dict["target"] = removeMetaText(line)
			
		if line.startswith("Attack", 0, 6):
			dict["attackRoll"] = removeMetaText(line)
			
		if line.startswith("Hit", 0, 3) or line.startswith("Effect", 0, 6):
			dict["hitDamageOrEffect"] = removeMetaText(line)
			
		if line.startswith("Miss", 0, 4):
			print("line starts with Miss: " + line)
			dict["missDamage"] = removeMetaText(line)
		
		if line.startswith("3rd", 0, 3) or line.startswith("5th", 0, 3) or line.startswith("7th", 0, 3) or line.startswith("9th", 0, 3):
			dict["hitDamageOrEffect"] = dict["hitDamageOrEffect"] + "\n" + line
			
		if "Special" in line or "Chain" in line or "Limited casting" in line:
			if "notes" in dict:
				dict["notes"] = dict["notes"] + "\n" + line
			else:
				dict["notes"] = line
		i += 1
		
		
	print ("OUTPUT: \n")
	print(dict)
	with open("spells.txt", "a") as file:
		file.write(json.dumps(dict))
	
def removeMetaText(text):
	lineText = re.sub(r'.*:', '', text)
	#remove first character since regex above leaves an empty space
	return lineText[1:]