import replit
from math import *
from termcolor import *
from random import *
projectName = "Syd's Battle Sim 0.1"

## Damage simulator for FFXIV. Intended to use actual FFXIV formulas to determine eDPS   ##
## Will start with drg, then ninja, to determine, based on rotation over 1/3/5/6 minutes ##
## What the expected DPS should be.                                                      ##
## At the end, should output dps, total damage, crit %, dh %, DHCrit %                   ##
""" Stats that will be used are:
Main stat (STR/DEX/VIT/MND/INT)
Secondary Stats (DET/CRIT/DH/TNC/SS)
Gear Stats (WD, AA Delay, DEF, MDEF)
Dirivitive Stats (Attack Power, GCD)
Table Stats (job Mod, Level Mod, Job Sub, etc.... modifiers based on set levels/stats)
"""
## Global Variables. Includes debug variables and test
debug_mode = True
debug_b4b = 1.3
debug_balance = round(1.1 + .05, 2)
debug_ds = 1.1
levelmain = 292  #These are static values at level 70
levelsub = 364  #So set them here rather than in the object.
leveldiv = 2170  #When level goes to 80, can re-adjust
level_hp_mod = 3600
level_mp_mod = 12000
level_pie_mod = 890

## Class Definitions. Each Job gets its own Subclass that branches off the main.
## This allows each subclass to have different definitions for each rotation, although
## The challenge will be to find a naming convention that is fluid to reduce code lines
## However, this should work in the interim as it will take time to develop other rotations


class Tank(object):
	def __init__(self, name, level, clan, mainStat, det, crit, dh, tnc, ss,
	             vit, pie):
		self.name = name
		self.level = level
		self.clan = clan
		self.mainStat = mainStat
		self.DET = det
		self.CRIT = crit
		self.DH = dh
		self.TNC = tnc
		self.ss = SS
		self.VIT = vit
		self.PIE = pie


class Ninja(NewPlayer):
	def __init__(self)
	jobmod = 110
	job_hp_mod = 108
	job_mp_mod = 48
	primstat = "DEX"
	rotationList = [
	    "5th GCD TCJ", "5th GCD Bhava", "6th GCD TCJ", "6th GCD Bhava"
	]


class Samurai(NewPlayer):
	jobmod = 112
	job_hp_mod = 109
	job_mp_mod = 40
	primstat = "STR"
	rotationList = ["1 Sen", "2 Sen", "3 Sen"]


class Monk(NewPlayer):
	jobmod = 110
	job_hp_mod = 110
	job_mp_mod = 43
	primstat = "STR"
	rotationList = ["Standard", "Tornado Kick"]


class Paladin(NewPlayer):
	jobmod = 100
	job_hp_mod = 120
	job_mp_mod = 59
	primstat = "STR"
	rotationList = ["Holy Spirit", "Rage of Halone"]


class DarkKnight(NewPlayer):
	jobmod = 105
	job_hp_mod = 120
	job_mp_mod = 79
	primstat = "STR"
	rotationList = ["Power Slash", "Syphon Strike"]


class Bard(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 79
	primstat = "DEX"
	rotationList = ["Standard"]


class Machinist(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 79
	primstat = "DEX"
	rotationList = ["1 Ammo", "3 Ammo"]


class BlackMage(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 129
	primstat = "INT"
	rotationList = ["Fire", "Blizzard"]


class Summoner(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 111
	primstat = "INT"
	rotationList = ["1", "2", "3", "4"]


class RedMage(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 120
	primstat = "INT"
	rotationList = ["Standard"]


class WhiteMage(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 124
	primstat = "MND"
	rotationList = ["Standard"]


class Scholar(NewPlayer):
	jobmod = 115
	job_hp_mod = 105
	job_mp_mod = 119
	primstat = "MND"
	rotationList = ["Standard"]


class Astrologian(NewPlayer):
	jobmod = 1105
	job_hp_mod = 105
	job_mp_mod = 124
	primstat = "MND"
	rotationList = ["Standard"]


class Dragoon(object):
	rotationList = ["Early Life", "Late Life"]
	job = "DRG"
	job_hp_mod = 115
	job_mp_mod = 49
	jobmod = 115
	clanmod = 2
	primstat = "STR"


class Ninja(object):
	def __init__(self, name, level, clan, mainStat, det, crit, dh, tnc, ss,
	             vit, pie):
		self.name = name
		self.level = level
		self.clan = clan
		self.mainStat = mainStat
		self.DET = det
		self.CRIT = crit
		self.DH = dh
		self.TNC = tnc
		self.SS = ss
		self.VIT = vit
		self.PIE = pie

	rotationList = ["Early Life", "Late Life"]
	job = "DRG"
	job_hp_mod = 115
	job_mp_mod = 49
	jobmod = 115
	clanmod = 2
	primstat = "STR"


class Warrior(object):
	def __init__(self, name, level, clan):
		self.name = name
		self.level = level
		self.clan = clan

	job = "WAR"
	mainStat = 2383
	DET = 1768
	CRIT = 2128
	DH = 364
	TNC = 1111
	SS = 963
	jobmod = 105
	clanmod = 2
	primstat = "STR"


#Dictionaries
## Should pull these from the text files, although maybe could just reference the tables dynamically? ##

job_list = {
    "Tanks": ["Dark Knight", "Paladin", "Warrior"],
    "Healers": ["Astrologian", "Scholar", "White Mage"],
    "Melee DPS": ["Dragoon", "Monk", "Ninja", "Samurai"],
    "Ranged Physical DPS": ["Bard", "Machinist"],
    "Ranged Magical DPS": ["Black Mage", "Red Mage", "Summoner"]
}


## Formula Functions
### Calculate different values/probabilities using known damage formulae
# Calculates the base main stat (not really useful except to)
def Attribute(mainstat, levelmain, jobmod, clanmod,
              traits):  ## Gets base main stat
	traits = mainstat * (traits / 10)
	return floor(levelmain * (jobmod / 100)) + clanmod + (traits)


def fTraits(mainstat,
            val):  #Returns the value of the traited main stat (Max 30%)
	return mainstat * (val / 10)


def damagebuffs(bloodforblood, dragonsight,
                balance):  #Calculates the product of all damage buffs.
	return bloodforblood * dragonsight * balance


def critbuffs(battlelit, spear):  #Calculate value of all critical hit buffs
	return battlelit * spear


def player_H_P(levelmain, level_hp_mod, job_hpmod, vit):  # Return total HP
	return (floor(level_hp_mod * (job_hpmod / 100)) + floor(
	    (vit - levelmain) * 21.5))


def player_M_P(levelmain, leveldiv, level_mp_mod, job_mpmod,
               pie):  # Return total MP
	return (floor(
	    (job_mpmod / 100) * ((6000 * (pie - 292) / leveldiv) + 12000)))


def dhp(levelsub, leveldiv, dhr):  #Direct Hit Probability
	return floor(550 * (dhr - levelsub) / leveldiv) / 10


def chp(levelsub, leveldiv, chr, critbuff):  #Critical Hit Probability
	return floor(200 * ((chr * critbuff) - levelsub) / leveldiv + 50) / 10


def fptc(potency):  # Returns the decimal value of potency (as a %)
	return potency / 100


def fwd(levelmod, jobmod, wd):  # Returns the weapon damage modifier
	return floor((levelmod * jobmod / 1000) + wd)


def fap(power):  ##attack/magic power function
	return floor((125 * (power - 292) / 292) + 100) / 100


def fdet(det, levelmain,
         leveldiv):  #Returns the determination multiplier on damage
	return floor(130 * (det - levelmain) / leveldiv + 1000) / 1000


def ftnc(tnc, levelsub,
         leveldiv):  #Returns the tenacity multiplier (only used for healing)
	return floor(100 * (tnc - levelsub) / leveldiv + 1000) / 1000


def fss(ss, levelsub,
        leveldiv):  #Returns the skillspeed modifier (effect on DoT damage)
	return floor(130 * (ss - levelsub) / leveldiv + 1000) / 1000


#This returns the GCD after buffs (Things like arrow, astral fire/umbral ice, etc.)
def fgcd(ss, leveldiv, levelsub, actiondelay, arrow, type1, type2, haste,
         feywind, rof, ast_umb):
	GCDm = floor(
	    (1000 - floor(130 * (ss - levelsub) / leveldiv)) * actiondelay / 1000)
	GCDA = floor(
	    floor(
	        floor((100 - arrow) * (100 - type1) / 100) *
	        (100 - haste) / 100) - feywind)
	GCDB = (type2 - 100) / -100
	GCDc = floor(
	    floor(floor(ceil(GCDA * GCDB) * GCDm / 100) * rof / 1000) * ast_umb /
	    100)
	return GCDc / 100


def fchr(chr, levelsub, leveldiv, critbuff):  #Damage Modifier of Critical Hit
	return floor(200 * ((chr * critbuff) - levelsub) / leveldiv + 1400) / 1000


def faa(levelmain, jobmod, wd, aadelay):  ##Auto-attacks
	return floor((floor(levelmain * jobmod / 1000) + wd) * (aadelay / 30))


#The final damage formula. The input values are all output values of the previous functions. Crit/DH probability are calculated before the damage formula runs
def damage_dealt(ptc, wd, ap, det, tnc, traits, chr, dhr, b4b, balance, ds):
	randomod = round(uniform(0.949, 1.051), 2)
	print("Random Mod: " + str(randomod))
	return floor(
	    floor(
	        floor(
	            floor(
	                floor(
	                    floor(floor(ptc * wd * ap * det * tnc * 1.3) * chr
	                          ) * dhr) * randomod) * b4b) * ds) * balance)


## Other Functions ##


def rand(x,
         y):  #Just a simplification of the randint function to save keystrokes
	return (randint(x, y) / 100)


def printTheLists(listname):
	count = 0
	for x in listname:
		count += 1
		print("\n" + str(count) + ". " + x)
	print("\n" + str(count + 1) + ". Quit\n")


def checkUserInput(inputKey, inputList):
	if str(inputKey).lower() in inputList or int(inputKey) <= len(inputList):
		return True
	else:
		return False

def getSubCategory(category,sub):
	pass



##### MAIN PROGRAM ######
while True:
	replit.clear()
	print(
	    "Hello and welcome to " + projectName + "...\n\nPlease begin by selecting a job from the following list (number or typed response both valid):")
	printTheLists(job_list)
	user_selection = input("Pick a Role:")
	if checkUserInput(user_selection, job_list):
		replit.clear()
		print("Great! Please select a job from the following list:")
	elif int(user_selection) == len(job_list)+1 or user_selection.lower() == "quit":
		print ("Take care!")
		break
	else:
		print("Sorry, that's not a valid choice")

##DEBUGGGING##
if debug_mode:
	debugPlayer = Dragoon("Syd", 70, "Sunseeker", 2380, 1178, 2324, 1936, 364,
	                      2283, 2910, 1463)
	debugPlayer.DET = 1178
	debugPlayer.CRIT = 2324
	debugPlayer.DH = 1936
	debugPlayer.TNC = 364
	debugPlayer.SS = 2283
	debugPlayer.VIT = 2910
	debugPlayer.PIE = 1463
	debugPlayer.job_hp_mod = 120  #DRK HP MOD
	debugPlayer.job_mp_mod = 119  #SCH MP MOD
	debugPlayer.jobmod = 115
	debugPlayer.clanmod = 2
	debug_run_sim_count = 5
	os.system('clear')
	temp_mainstat = Attribute(debugPlayer.mainStat, levelmain,
	                          debugPlayer.jobmod, debugPlayer.clanmod, 3)
	debug_dhHitProb = dhp(levelsub, leveldiv, debugPlayer.DH)
	debug_critHitProb = chp(levelsub, leveldiv, debugPlayer.CRIT, 1.15)
	debug_potency = fptc(450)
	debug_wdMod = fwd(levelmain, debugPlayer.jobmod, 105)
	debug_atkPwr = fap(debugPlayer.mainStat)
	debug_detMod = fdet(debugPlayer.DET, levelmain, leveldiv)
	debug_tncMod = ftnc(debugPlayer.TNC, levelsub, leveldiv)
	debug_ssMod = fss(debugPlayer.SS, levelsub, leveldiv)
	debug_globalCD = fgcd(debugPlayer.SS, leveldiv, levelsub, 2500, 0, 0, 0, 0,
	                      0, 100, 100)
	debug_critMod = fchr(debugPlayer.CRIT, levelsub, leveldiv, 1.15)
	debug_aaMod = faa(levelmain, debugPlayer.jobmod, 105, 2.8)
	debug_playerMP = player_M_P(levelmain, leveldiv, level_mp_mod,
	                            debugPlayer.job_mp_mod, debugPlayer.PIE)
	debug_playerHP = player_H_P(levelmain, level_hp_mod,
	                            debugPlayer.job_hp_mod, debugPlayer.VIT)
	####This is the output section.####
	print(
	    "Base Main Stat (" + debugPlayer.primstat + "): " + str(temp_mainstat))
	print("Trait Value: " + str(fTraits(debugPlayer.mainStat, 3)))
	print("Direct Hit Probability: " + str(debug_dhHitProb) + "%")
	print("Critical Hit Probability: " + str(debug_critHitProb) + "%")
	print("Potency of 100pot Attack: " + str(debug_potency))
	print("Weapon Damage Mod (105dmg item) :" + str(debug_wdMod))
	print("Attack Power Modifier: " + str(debug_atkPwr))
	print("Determination Modifier: " + str(debug_detMod))
	print("Tenacity Modifier: " + str(debug_tncMod))
	print("Skill Speed Modifier: " + str(debug_ssMod))
	print("GCD: " + str(debug_globalCD) + " (With No Buffs)")
	print("Max MP: " + str(debug_playerMP))
	print("Max HP: " + str(debug_playerHP) + "\n\n")
	print("Crit Modifier: " + str(debug_critMod))
	print("DH Modifier: 1.25")
	print("Auto Attack Damage Modifier: " + str(debug_aaMod))

	debug_iscrit = uniform(0.01, 100.01)
	for i in range(0, debug_run_sim_count):

		print("Crit roll: " + str(round(debug_iscrit, 2)))
		if debug_iscrit < debug_critHitProb:
			debug_iscrit = debug_critMod
		else:
			debug_iscrit = 1
		debug_isdh = uniform(0.01, 100.01)
		print("DH Roll: " + str(round(debug_isdh, 2)))
		if debug_isdh <= debug_dhHitProb:
			debug_isdh = 1.25
		else:
			debug_isdh = 1
		if debug_iscrit > 1 and debug_isdh > 1:
			print(
			    colored(
			        "DIRECT CRITICAL HIT!!", "red", attrs=['bold', 'blink']))
		elif debug_iscrit > 1 and debug_isdh == 1:
			print(colored("Critical Hit!", "red", attrs=['bold']))
		elif debug_iscrit == 1 and debug_isdh > 1:
			print(colored("Direct Hit!", "yellow", attrs=['dark']))
		else:
			print(colored("Regular Hit", "cyan", attrs=['dark']))
		print("Balance: " + str(debug_balance))
		print("B4B: " + str(debug_b4b))
		print("Dragon Sight: " + str(debug_ds))
		#damage_dealt(ptc,wd,ap,det,tnc,traits,chr,dhr,b4b,balance,ds)
		print("Direct Damage Dealt by " + debugPlayer.name + ": " + str(
		    damage_dealt(debug_potency, debug_wdMod, debug_atkPwr,
		                 debug_detMod, debug_tncMod, 1.3, debug_iscrit,
		                 debug_isdh, debug_b4b, debug_ds, debug_balance)))
