import re

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
			
		i += 1
		
		
		
	print(dict)