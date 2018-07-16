import replit
from math import *
from termcolor import *
from random import *
import time
import sys
#Next 2 imports are for handling XIVDB and FFLOGS APIs.
import json, request
projectName = "Syd's Battle Sim 0.1 (Alpha)"

#Note: Currently this will be built as a proof of concept only.
#Hopefully by the end, can dynamically adjust rotations and even allow players to create own rotations
#To Simulate with a somewhat reasonable accuracy what they can expect DPS-Wise

"""This is a damage simulator for FFXIV. The program is meant to accomplish 3 primary goals, and 2 stretch goals:

First Primary Goal: Allow user to dynamically adjust gearsets and get average expected damage for one hit. Similar to spreadsheets that exist now, but without the latency inherent in large Google Sheets. This is accomplished by allowing the user to specify the number of trials to run (n = 10 to 10,000). The program would output the mean, median, and mode. It would calculate highest and lowest hit, and calculate the standard deviation. Would also calculate Crit, DH and CDH percentages..
Second Primary Goal: Allow the user to actually simulate a rotation (1/3/5/8/10/12 minutes as those are common values seen in phases or fights) and generate the expected DPS (In a dummy situation). These would be based on pre-built, generally-accepted "official" openers
	Sub-Goal: Graph out the DPS chart for this? Should be feasible with Flask/Ruby on the Rails/JavaScript
Third Primary Goal: Allow side-by-side comparisons between 2 gearsets and/or different rotations (ie: DRG early life or late life).
	Sub-Goal: As above. Allow graphing

First Stretch Goal: Allow the user to actually generate their own rotation (Setup would be similar to ffxivrotations mixed with ffxivcraftsimulator in concept, allowing user to drag-and-drop) -- Would output into a graph + text summary.
Second Stretch Goal: Allow for creating a full party and importing, AND/OR allow user to input when certain buffs would be available (Ie: Balance) to help create hypothetical scenarios
Third Stretch Goal: Calculate expectation of clipping. The primary challenge here is that it is unknown how to determine the animation lock, especially given recent evidence that this can be affected by framerate. """

## Feature Check-List ##
## 1) Import Damage Formulas -- DONE
##	1b) Clean out old damage formulas -- DONE
##	1c) Re-Write the Debug section. Add a menu option for debug mode to allow it to loop, and generate less "junk" data. -- DONE
## 2) Set up player Classes -- IN PROGRESS
##	** Should different jobs get different classes? Or have a class method that sets job stats based on the job input????**
##	** In both cases, how would rotations be handled? A separate function, or a separate class? Perhaps a dictionary, and can set pre-existing rotations??**
##	2a) Set up damage methods -- DONE
##	2b) Set up gearset/character sheet method --- IN PLANNING
##  2c) Create method to adjust stats --- DONE** (**: May need adjusting later on)
## 3) Develop console menu -- DONE (*Not all menus completed, but the menu design is completed)
##	3a) Develop main program loop -- DONE
##  3b) Update: Loop will work for class and job selections, but not sure how to handle the return. Boolean or function? Currently, added an optional argument for the job menu, where jobSel is initially None, unless it is set to something else. Could do the same with other variables
## 4) Set up Functions for the rotations themselves --- NOT STARTED
## 5) Set up GUI/Deploy as webapp --- NOT STARTED
## 6) Custom rotations --- CONCEPT ONLY - NOT STARTED
## END CHECKLIST      ##

##------ Debug Stuff -------##
debug_mode = False
debug_buffs={"B4B":1.3,"Balance":1.2,"Dragon Sight":1.1} #Might be easier to roll all buffs into a dictionary and reference them on the fly? Other option is to set them as a class that when called returns a list of the buffs, but that may be more complicated than worthwhile
debug_b4b = 1.3
debug_balance = round(1.1 + .05, 2)
debug_ds = 1.1
debug_list = []
##------ END Debug Stuff -------##

## Global Variables. Includes debug variables and test
job_list = {"Tank":["Dark Knight","Paladin","Warrior"],"Healer":["Astrologian","Scholar","White Mage"],"Melee DPS":["Dragoon","Monk","Ninja","Samurai"],"Ranged DPS":["Bard","Machinist"],"Ranged Magic DPS":["Black Mage","Red Mage","Summoner"],"Debug Mode":["Full Debug","Display Stats"]}
#All the menu stuff is defined and called below#
levelmain = 292  #These are static values at level 70
levelsub = 364  #So set them here rather than in the object.
leveldiv = 2170  #When level goes to 80, can re-adjust
level_hp_mod = 3600
level_mp_mod = 12000
level_pie_mod = 890
sub_base = 292
main_base = 364

char_complete = False
player_character = None
create_job = None
create_clan = None
create_name = None


## Global Functions ##
def error_msg(msg,*the_errors):
	"""This function will take a message and an error list (as a tuple), format, and output it to console

	msg = Message (Could be either a success or error message)
	the_errors = the list of errors. Could be any number of errors"""
	separator = "\n"
	if not the_errors:
		print (msg)
	else:
		print (msg)
		for x in the_errors:
			for y in x:
				print ("- "+y)
	print ("\n")

def wait(duration):
	"""pause program for 'duration' seconds"""
	time.sleep(duration)

def rand(x, y):  #Just a simplification of the randint function to save keystrokes
	"""Returns a random value between x and y
	
	Used in damage calculation to generate the random damage modifier between 0.95x and 1.05x"""
	return (randint(x, y) / 100)

def isanint (num):
	"""Determine if 'num' is an integer or not"""
	try:
		val = int(num)
		return True
	except ValueError:
		#Instead of printing an error to console, just returns False instead.
		return False

def printTheLists(listname):
	"""Return a numbered list of all items in listname

	Useful for generating submenus """
	count = 0
	for x in listname:
		count += 1
		print("\n" + str(count) + ". " + x)
	print("\n" + str(count + 1) + ". Quit\n")


def checkUserInput(inputKey, inputList):
	"""Check to see if the value of inputKey exists in inputList (Checks phrase + index)"""
	if inputKey.lower() in map(str.lower,inputList): 
		#Checks if either the text matches a valid entry, or the number is within range. Match any case by converting all to lower in both input string and the list object.
		return True
	elif isanint(inputKey):
		#If our word is not in the list, we'll instead check to see if it's a number instead
		if int(inputKey) <= len(inputList)+1:
			#If number, check if it's in a valid range, otherwise return False
			return True
		else:
			return False
	else:
		#Need to adjust. Giving int size error when a string passes, but isn't in the list. 
		return False


"""The current setup is to use a class for the player object. This class uses "default" values. 
The current setup is that the NewPlayer class is a superclass, and each job would have a subclass which sets individual job mod values, as well as having its own rotation function. This should work just fine, however,
it might actually be easier to only use one class, with a function that sets the job-specific values. This function would be called when the class is invoked. As for rotations, could create each rotation as a separate function or class, and store those references in a list, and then when you set the job, it adjusts those stats and also imports the rotation list. Not sure which would be most viable in this case so will need to investigate.

*** It MIGHT actually be viable to use a dynamic rotation. It would work with these steps:
1) Define a class called 'Rotation' that takes the job and/or the rotation name. This could use a list or a dictionary that contains the rotation in order. For double-weaving, have a command 'pause' built in.
2) In the player class, a function called combat (or something similar)
3) Every second, would step into the next step with something like 'Rotation.next()'
4) That function should look to see what the next step in the rotation is. If it's 'pause', skip to next step. If it's oGCD, execute. If it's a GCD move, check to see if the GCD spin has reset. If it has, execute. If not, 'pause'.
This may function better for future ability to add in custom rotation execution."""

###THIS IS THE SUPERCLASS FOR PLAYER CHARACTER. DON'T MODIFY THESE PARTS WITHOUT READING WHAT THEY DO###
class NewPlayer(object):
	"""Superclass for the player character. Would expect to have 2 of these for comparison purposes, but potentially
	could allow for a full-party, although that would be pretty high-level and far into the future
	
	This is a huge class with a lot of methods running. Potentially may need to globalize some functions but I think better this way for now."""
	#Will add a function to calculate base stat bonuses based on clan. Can do that later.
	def __init__(self,name,level,clan,maintype):
		self.name = name
		self.level = level
		self.clan = clan
		self.jobmod = 100
		self.job_hp_mod = 100
		self.job_mp_mod = 100
		self.maintype = maintype
		self.mainStat = 364
		self.DET = 292
		self.CRIT = 292
		self.DH = 292
		self.TNC = 292
		self.SS = 292
		self.VIT = 364
		self.PIE = 364
		self.stats = {
			self.maintype: 364,
			"Determination": 364,
			"Critical Hit": 364,
			"Direct Hit": 364,
			"Tenacity": 364,
			"Skillspeed": 364,
			"Vitality": 364,
			"Piety": 364,
		}
	
	def equip_gear(self,gearname = None):
		pass

	def character_sheet(self):
		"""Print the character sheet including stat headings, stat values, and gear

		May need additional arguments.
		"""
	
	def adjust_stats(self,job,hp,mp,MS,det,crt,dh,tnc,ss,vit,pie):
		"""When passed stats, this method tries to update the NewPlayer classes stats. It will check to see if they are within
		a valid range and if so, will over-write them. If not, make no changes and add to error_list, which is output later.
		
		The function will take the job, hp and mp mods, though, which may not actually be necessary since they should be static values. These modifications should be set in the subclass so they are unique to that object only and are not inherited down, which could cause headaches trying to debug."""
		self.jobmod = job
		self.job_hp_mod = hp
		self.job_mp_mod = mp
		self.mainStat = MS
		self.DET = det

	def get_stats(self,main,det,crit,dh,tnc,ss,vit,pie): #Used to set stats from external source
		out_errors = []
		if main >= main_base:
			self.mainStat = main
			self.stats[self.maintype] = main
		else:
			out_errors.append("Error: Main stat cannot be lower than {0}".format(str(main_base)))
		if det>= sub_base:
			self.DET= det
			self.stats["Determination"] = det
		else:
			out_errors.append("Error: Determination cannot be lower than {0}".format(str(sub_base)))
		if crit>= sub_base:
			self.CRIT = crit
			self.stats["Critical Hit"] = crit
		else:
			out_errors.append("Error: Crit cannot be lower than {0}".format(str(sub_base)))
		if dh >= sub_base:
			self.DH = dh
			self.stats["Direct Hit"] = dh
		else:
			out_errors.append("Error: Direct Hit cannot be lower than {0}".format(str(sub_base)))
		if tnc >= sub_base:
			self.TNC = tnc
			self.stats["Tenacity"] = tnc
		else:
			out_errors.append("Error: Tenacity cannot be lower than {0}".format(str(sub_base)))
		if ss>= sub_base:
			self.SS = ss
			self.stats["Skill Speed"] = ss
		else:
			out_errors.append("Error: Skill Speed cannot be lower than {0}".format(str(sub_base)))
		if vit >= main_base:
			self.VIT = vit
			self.stats["Vitality"] = vit
		else:
			out_errors.append("Error: Vitality cannot be lower than {0}".format(str(main_base)))
		if pie >= main_base:
			self.PIE = pie
			self.stats["Piety"] = pie
		else:
			out_errors.append("Error: Piety cannot be lower than {0}".format(str(sub_base)))
		if out_errors: #If we encountered any errors, display them all in order of appearance
			error_msg("Oops! Some changes were not completed! Please review the follow {0} errors:\n".format(str(len(out_errors))),out_errors)
		else: #Otherwise, give the all clear!
			error_msg("All changes complete. No errors encounterd.")
	
	#This returns the value of the traited main stat (Max 30%) -- ie: level 70 characters have +30% of Main stat
	def get_traits(self,mainstat,val):  #Returns the value of the traited main stat (Max 30%)
		return mainstat * (val / 10)
	
	def get_attributes(self,mainstat, levelmain, jobmod, clanmod,traits):  ## Gets base main stat
		traits = mainstat * (traits / 10)
		return floor(levelmain * (jobmod / 100)) + clanmod + (traits)

	
	#Return sum potency of damage buffs. Need to adjust to return a list of (dmg,crit,dh) buffs that can be accessed later.
	def get_dmg_buffs(self,bloodforblood, dragonsight,balance):
		return bloodforblood * dragonsight * balance

	#This gets the player's max HP based on job, level and VIT stat.
	def get_HP(self,levelmain, level_hp_mod, job_hpmod, vit):
		return (floor(level_hp_mod * (job_hpmod / 100)) + floor((vit - levelmain) * 21.5))

	#This gets the player's max MP based on Job, level and PIE stat.
	def get_MP(self,levelmain, leveldiv, level_mp_mod, job_mpmod,pie): 
		return (floor((job_mpmod / 100) * ((6000 * (pie - 292) / leveldiv) + 12000)))
	
	#This returns the probability of a direct hit, based on level and DH stat, where DHR
	#Worth noting: Buffs that affect direct hit don't change the stat, but add to the percentage AFTER the fact,
	#So the buff calculation would need to be applied differently.
	def get_directprob(self,levelsub, leveldiv, dhr):  #Direct Hit Probability, where DHR = DH stat
		return floor(550 * (dhr - levelsub) / leveldiv) / 10

	#This returns the probability that a hit will be a critical
	#This IS affected by buffs to stats rather than end buff to rate
	#However, Sch crit buff is a flat increase to the rate at which a boss receives critical hits.
	#Not sure how that would be calculated (before or after this function runs). Will need to check.
	def get_critrate(self,levelsub, leveldiv, chr, critbuff):  #Critical Hit Probability, where chr = crit stat
		return floor(200 * ((chr * critbuff) - levelsub) / leveldiv + 50) / 10

	#This returns the decimal potency of an attack (as a % of 100 potency). Only needed because of how
	#It is factored into the damage formula since it saves a step, although could possibly just be amalgamated
	#Into the formula.
	def get_potency(self,potency):  # Returns the decimal value of potency (as a %)
		return potency / 100

	#Returns the Weapon Damage Modifier (The effect of weapon damage on total damage output)
	def get_wepdmg(self,levelmod, jobmod, wd):  # Returns the weapon damage modifier, where wd = Weapon Damage
		return floor((levelmod * jobmod / 1000) + wd)

	#This returns the effect of attack power on the final damage.
	#Technically the damage sheet has 2 formulas but they're the same so it shouldn't matter
	#Since the subclass will feed its own info into this function anyway
	def get_attackpwr(self,power):  ##attack/magic power function
		return floor((125 * (power - 292) / 292) + 100) / 100

	#This returns the determination multiplier on damage (rounded to thousandth)
	def get_detMod(self,det, levelmain,leveldiv):  #Where det = player.DET
		return floor(130 * (det - levelmain) / leveldiv + 1000) / 1000

	#This returns the skillspeed modifier on DoT damage
	def get_ssMod(self,ss, levelsub,leveldiv):  #where ss = player.SS (Skill speed)
		return floor(130 * (ss - levelsub) / leveldiv + 1000) / 1000

	#Even though this only applies to tanks, the result is still used in the damage formula. It just results
	#in a return value of 1
	def get_tncMod(self,tnc, levelsub,leveldiv):  #Returns the tenacity multiplier (only used for healing)
		return floor(100 * (tnc - levelsub) / leveldiv + 1000) / 1000

	#This function returns the GCD timer. This is a larger function that actually rounds down a couple times
	#GCDm first floors the result after accounting for skillspeed and specific action delay (some are on the GCD)
	# but some may be longer (spells) or shorter (Mudras)
	#GDCA Factors in hastes (arrow, haste buffs like Halicarnassus normal) and type1 buffs (ie: Bloodweapon, Ley Lines, Shifu, Presence of Mind)
	#GCDB Factors in Type2 buffs (Huton, Greased Lightning, Army's Paeon)
	#GCDc returns the product for GCDA*B*C and includes the Riddle of Fire (as it's a dmg+/Speed- buff) and Astral Ice/Umbral Fire speed buffs (ie: When Fire3 from Umbral Ice 3 is a 50% GCD reduction)
	def get_GCD(self,ss, leveldiv, levelsub, actiondelay, arrow, type1, type2, haste,feywind, rof, ast_umb):
		GCDm = floor((1000 - floor(130 * (ss - levelsub) / leveldiv)) * actiondelay / 1000)
		GCDA = floor(floor(floor((100 - arrow) * (100 - type1) / 100) *(100 - haste) / 100) - feywind)
		GCDB = (type2 - 100) / -100
		GCDc = floor(floor(floor(ceil(GCDA * GCDB) * GCDm / 100) * rof / 1000) * ast_umb /100)
		return GCDc / 100

	#This returns the damage modifier of the Critical Hit stat
	def get_critMod(self,chr, levelsub, leveldiv, critbuff):  #where chr = player.crit and critbuff is sum of all buffs to crit (ie: Spear, Battle Litany)
		return floor(200 * ((chr * critbuff) - levelsub) / leveldiv + 1400) / 1000

	#Return Auto-Attack Damage per tick
	def get_autoAtk(self,levelmain, jobmod, wd, aadelay):  ##Auto-attacks
		return floor((floor(levelmain * jobmod / 1000) + wd) * (aadelay / 30))

	#The Bread and butter. Returns the damage dealt based on all previous functions.
	#The requirement is that each function runs first.
	#The best way is to run the function that stores each item (ptc, wd, etc) as a temporary variable
	#and then throws that to the function
	#B4b,Balance and DS are all specific DRG buffs. However would also need to account for things like
	#Fists of Fire, etc.
	#May have to move the floor(buff* (flor(buff)) chain and toss that to a separate function to clean up the code.
	#Each buff should be 1 if no effect, and >1 for a buff, <1 for a nerf (ie: Dmg down)
	#Just need to write that function separately. Will be on to-do list.
	def damage_dealt(self,ptc, wd, ap, det, tnc, traits, chr, dhr, b4b, balance, ds):
		"""The final damage output formula. This is a product of all other damage modifier formulas above (Can this be made simpler? All in one function, perhaps?).

		Should set up buffs as **kwargs and keyword them. That way they can be fed dynamically from one function."""
		randomod = round(uniform(0.949, 1.051), 2) #To keep variable damage, modifies output by between 0.95->1.05
		if debug_mode == True: #When debugging, output the value of the random roll.
			print("Random Mod: " + str(randomod)) 
		return floor(floor(floor(floor(floor(floor(floor(ptc * wd * ap * det * tnc * 1.3) * chr) * dhr) * randomod) * b4b) * ds) * balance)
###END NEW PLAYER SUPERCLASS###


"""Some other bullshit here. These are the current placeholders for the other subclasses"""
class tank(NewPlayer):
	def __init__(self,name):
		self.name = name


class Ninja(NewPlayer):
	def __init__(self):
		jobmod = 110
		job_hp_mod = 108
		job_mp_mod = 48
		primstat = "DEX"
		rotationList = [
	    "5th GCD TCJ", "5th GCD Bhava", "6th GCD TCJ", "6th GCD Bhava"]


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


class Dragoon(NewPlayer):
	rotationList = ["Early Life", "Late Life"]
	job = "DRG"
	job_hp_mod = 115
	job_mp_mod = 49
	jobmod = 115
	clanmod = 2
	primstat = "STR"

##Was testing with this one##
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

class MainMenu(object):
	def __init__(self,optionlist,b):
		self.optionlist = optionlist
		self.b = b

##### MENU CLASSES ######
"""Define the base classes used in the menu system here"""
class menu(object):
	""" Base class for a menu object """
	def __init__(self,name,buttons,parent=None):
		"""name = window name, commands is a list/dict of commands, and parent is the parent menu (if menu is a submenu)"""
		self.name = name
		#The Menu name, for display
		if type(buttons) is list:
			#As of python 3.6, dictionaries are ordered, so determine if we have a dict or a list
			#If a list, convert to a dict. Otherwise if it is a dict, keep it as-is.
			for x in buttons:
				self.buttons[x.nav] = x
		else:
			self.buttons = buttons
		self.parent = parent
		#Determine if the menu is a submenu or a top-level menu.

	def display(self):
		"""Display menu with navigation"""
		response = None
		while response is None:
			if self.parent is None:
				print (self.name)
				for button in self.buttons:
					print ("  {0}. {1}".format(self.buttons[button].nav,self.buttons[button].name))
			else:
				print ("{0}\n {1}".format(self.parent,self.name))
				for button in self.buttons:
					print ("   {0}. {1}".format(self.buttons[button].nav,self.buttons[button].name))
			response = self.userInput()
	
	def userInput(self):
		"""Check the user's decision, and act on it (if valid)"""
		inputSel = input("Enter Choice >>") 
		try:
			#Try to locate the user's choice in our menu dictionary
			button = self.buttons[int(inputSel)]
		except keyError:
			# if it's not there (dictionary returns KeyError), return None, and the menu will keep displaying
			# Print to the console to tell the user that there has been an error.
			print ("Error - Selection is not valid")
			return None

		button.action()
		return inputSel

class menubutton(object):
	"""Creates a menu button object"""
	def __init__(self,name,nav,func,dest=None):
		self.name = name
		self.nav = nav
		self.func = func
		self.dest = dest
	
	def action(self):
		"""Perform button function"""
		if self.dest is None:
			self.func()
		else:
			self.func(self.dest)

class menuControl(object):
	def __init__(self,menu):
		self.menus = menu
		self.start()

	def start(self):
		while 0 == 0:
			replit.clear()
			self.menus.display()
			wait(1)

## MENU FUNCTIONS ##
"""Every menu function contained here.

Each menu function contains a few items:
1) Button definitions. Each menu item needs a button, which is an instance of menubutton object that contains menubutton.nav (the number that executes the function), a name, and a function.
2) A dictionary with format menubutton.nav:menubutton object. This is used to display the buttons, and then when user selects an input, runs menubutton.action
3) Initialize the menu (creates an object 'menuname' which is an instance of the menu class)
4) Redefine 'controller' to be an instance of menuControl for the current menu
5) Runs controller.cycle(), which basically starts that menu.

"""
def quit():
	"""Quits the program"""
	replit.clear()
	sys.exit("Goodbye!")

def go_back(dest):
	"""Goes back to 'dest' menu"""
	dest()

def menu_job(role):
	"""Dynamic Job Selection list"""
	button_go_back = menubutton("End Character Creation",0,go_back,character_options_menu)
	if role == "Tank":
		button_drk = menubutton("Dark Knight",1,create_character_menu,"Dark Knight")
		button_pld = menubutton("Paladin",2,create_character_menu,"Paladin")
		button_war = menubutton("Warrior",3,create_character_menu,"Warrior")
		role_buttons = {
			button_drk.nav:button_drk,
			button_pld.nav:button_pld,
			button_war.nav:button_war,
			button_go_back.nav:button_go_back			
		}
	elif  role == "Healer":
		button_ast = menubutton("Astrologian",1,create_character_menu,"Astrologian")
		button_sch = menubutton("Scholar",2,create_character_menu,"Scholar")
		button_whm = menubutton("White Mage",3,create_character_menu,"White Mage")
		role_buttons = {
			button_ast.nav:button_ast,
			button_sch.nav:button_sch,
			button_whm.nav:button_whm,
			button_go_back.nav:button_go_back
		}	
	elif role == "Melee DPS":
		button_drg = menubutton("Dragoon",1,create_character_menu,"Dragoon")
		button_mnk = menubutton("Monk",2,create_character_menu,"Monk")
		button_nin = menubutton("Ninja",3,create_character_menu,"Ninja")
		button_sam = menubutton("Samurai",4,create_character_menu,"Samurai")
		role_buttons = {
			button_drg.nav:button_drg,
			button_mnk.nav:button_mnk,
			button_nin.nav:button_nin,
			button_sam.nav:button_sam,
			button_go_back.nav:button_go_back
		}
	elif role == "Ranged DPS/Caster":
		button_brd = menubutton("Bard",1,create_character_menu,"Bard")
		button_mch = menubutton("Machinist",2,create_character_menu,"Machinist")
		button_blm = menubutton("Black Mage",3,create_character_menu,"Black Mage")
		button_rdm = menubutton("Red Mage",4,create_character_menu,"Red Mage")
		button_smn = menubutton("Summoner",5,create_character_menu,"Summoner")
		role_buttons = {
			button_brd.nav:button_brd,
			button_mch.nav:button_mch,
			button_blm.nav:button_blm,
			button_rdm.nav:button_rdm,
			button_smn.nav:button_smn,
			button_go_back.nav:button_go_back
		}
	job_select_menu = menu("Which Job would you like to play?",role_buttons,"Create Character")
	controller = menuControl(job_select_menu)
	controller.start()

def change_race(race = None):
	"""Change player Race"""
	if race is None:
		

def change_gear():
	"""Change Gear"""
	replit.clear()
	print ("Change Gear")
	wait(2)


def create_character_menu(jobSel = None):
	"""Menu for Character Creation
	
	jobSel is passed when sending back to this menu from a job creation menu"""
	if jobSel is None:
		print ("Please select a job from the list")
		button_tank = menubutton ("Tank",1,menu_job,"Tank")
		button_healer = menubutton ("Healer",2,menu_job,"Healer")
		button_melee = menubutton ("Melee DPS",3,menu_job,"Melee DPS")
		button_ranged = menubutton ("Ranged DPS/Caster",4,menu_job,"Ranged DPS/Caster")
		button_back = menubutton ("Go Back",0,go_back,character_options_menu)
		create_character_buttons = {
			button_tank.nav:button_tank,
			button_healer.nav:button_healer,
			button_melee.nav:button_melee,
			button_ranged.nav:button_ranged,
			button_back.nav:button_back
		}
	else:
		print("Current job: {0}".format(jobSel))
		button_chg_race = menubutton ("Change Race",1,change_race)
		button_chg_gear = menubutton ("Change Gear",2,change_gear)
		button_go_back = menubutton("Go Back",0,go_back,main_menu)
		create_character_buttons = {
			button_chg_race.nav:button_chg_race,
			button_chg_gear.nav:button_chg_gear,
			button_go_back.nav:button_go_back
		}
	create_character_menu= menu("Select a Job Role",create_character_buttons,"Create a Character")
	controller=menuControl(create_character_menu)
	controller.start()
	
	wait(5)

def view_stats():
	"""View stats"""
	print ("View Character Stats:")
	wait(2)

def run_sim():
	"""Run the sim"""
	replit.clear()
	print ("Let's run the sim now! (Reset in 2 seconds)")
	wait(2)
	main_menu()
	

def debug_hit():
	replit.clear()
	debug_hitTypes =[0,0,0] # Used for tracking. Format is [critical, direct, direct critical]
	test2 = NewPlayer("Debug Fighter",70,"Sunseeker","Strength")
	test2.get_stats(200,400,200,400,400,400,400,400)
	print (test2.name + " stats are:\nStrength: " + str(test2.mainStat) +"\nVit: " + str(test2.VIT) +"\nCRIT: " +str(test2.CRIT) +"\nDET: " +str(test2.DET) +"\nDH: " +str(test2.DH) +"\nSkillSpeed: " +str(test2.SS) +"\nTENACITY: "+str(test2.TNC)+"\n")
	print ("First Diagnosis Completed \n\n\n")
	debugPlayer = Ninja("Syd", 70, "Sunseeker", 2380, 1178, 2324, 1936, 364,2283, 2910, 1463)
	debugPlayer.job_hp_mod = 120  #DRK HP MOD
	debugPlayer.job_mp_mod = 119  #SCH MP MOD
	debugPlayer.jobmod = 115
	debugPlayer.clanmod = 2
	debug_run_sim_count = 5
	temp_mainstat = test2.get_attributes(debugPlayer.mainStat, levelmain,debugPlayer.jobmod, debugPlayer.clanmod, 3)
	debug_dhHitProb = test2.get_directprob(levelsub, leveldiv, debugPlayer.DH)
	debug_critHitProb = test2.get_critrate(levelsub, leveldiv, debugPlayer.CRIT, 1.15)
	debug_potency = test2.get_potency(450)
	debug_wdMod = test2.get_wepdmg(levelmain, debugPlayer.jobmod, 105)
	debug_atkPwr = test2.get_attackpwr(debugPlayer.mainStat)
	debug_detMod = test2.get_detMod(debugPlayer.DET, levelmain, leveldiv)
	debug_tncMod = test2.get_tncMod(debugPlayer.TNC, levelsub, leveldiv)
	debug_ssMod = test2.get_ssMod(debugPlayer.SS, levelsub, leveldiv)
	debug_globalCD = test2.get_GCD(debugPlayer.SS, leveldiv, levelsub, 2500, 0, 0, 0, 0,0, 100, 100)
	debug_critMod = test2.get_critMod(debugPlayer.CRIT, levelsub, leveldiv, 1.15)
	debug_aaMod = test2.get_autoAtk(levelmain, debugPlayer.jobmod, 105, 2.8)
	debug_playerMP = test2.get_MP(levelmain, leveldiv, level_mp_mod, debugPlayer.job_mp_mod, debugPlayer.PIE)
	debug_playerHP = test2.get_HP(levelmain, level_hp_mod, debugPlayer.job_hp_mod, debugPlayer.VIT)
	####This is the output section.####
	print(
	    "Base Main Stat (" + debugPlayer.primstat + "): " + str(temp_mainstat))
	print("Trait Value: " + str(test2.get_traits(debugPlayer.mainStat, 3)))
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

	debug_iscrit = randint(0,100)
	for i in range(0, debug_run_sim_count):
		debug_iscrit = randint(0,100)
		print("Crit roll: " + str(debug_iscrit))
		if debug_iscrit < debug_critHitProb:
			debug_iscrit = debug_critMod
		else:
			debug_iscrit = 1
		debug_isdh = randint(0,100)
		print("DH Roll: " + str(debug_isdh))
		if debug_isdh <= debug_dhHitProb:
			debug_isdh = 1.25
		else:
			debug_isdh = 1
		if debug_iscrit > 1 and debug_isdh > 1:
			print(colored("DIRECT CRITICAL HIT!!", "red", attrs=['bold', 'blink']))
			debug_hitTypes[2] += 1
		elif debug_iscrit > 1 and debug_isdh == 1:
			print(colored("Critical Hit!", "red", attrs=['bold']))
			debug_hitTypes[0] += 1
		elif debug_iscrit == 1 and debug_isdh > 1:
			print(colored("Direct Hit!", "yellow", attrs=['dark']))
			debug_hitTypes[1] += 1
		else:
			print(colored("Regular Hit", "cyan", attrs=['dark']))
		print("Balance: " + str(debug_balance))
		print("B4B: " + str(debug_b4b))
		print("Dragon Sight: " + str(debug_ds))
		debug_list.append(test2.damage_dealt(debug_potency, debug_wdMod, debug_atkPwr,debug_detMod, debug_tncMod, 1.3, debug_iscrit,debug_isdh, debug_b4b, debug_ds, debug_balance))
		print ("Direct Damage Dealt by {0}: {1}".format(debugPlayer.name,str(debug_list[i])))
	debug_avg = 0
	for x in debug_list:
		debug_avg += x
	debug_avg = debug_avg/len(debug_list)
	debug_mode = 0
	if len(debug_list) % 2 == 0: #Display the MODE of all hits
		debug_mode = debug_list[int(len(debug_list)/2)]
	else:
		y = debug_list[int(len(debug_list)/2 + 1)]
		x = debug_list[int(len(debug_list)/2 - 1)]
		debug_mode = int((x+y)/2)
	print ("\nHighest Hit was: {0}\nLowest Hit was: {1}\nAverage Hit was: {2}\nMiddle Hit was: {3}".format(str(max(debug_list)),str(min(debug_list)),str(debug_avg),str(debug_mode)))
	print ("Total Critical Hits: {0}({3}%)\nTotal Direct Hits: {1}({4}%)\nTotal Direct Critical Hits: {2}({5}%)".format(str(debug_hitTypes[0]),str(debug_hitTypes[1]),str(debug_hitTypes[2]),str(debug_hitTypes[0]/debug_run_sim_count*100),str(debug_hitTypes[1]/debug_run_sim_count*100),str(debug_hitTypes[2]/debug_run_sim_count*100)))
	next_step = input("Press any Key to return>>")
	if next_step is not None:
		debug_menu("1234")

def main_menu():
	"""Setup the main menu options here"""
	button_run_simulation = menubutton("Run Simulation",1,run_sim)
	button_character_menu = menubutton("Character Options",2,character_options_menu)
	button_combat_options_menu = menubutton ("Combat Options",3,combat_options_menu)
	button_debug_menu = menubutton("Debug Options",4,debug_menu)
	button_quit = menubutton ("Quit Program",0,quit)
	main_menu_buttons = {
		button_run_simulation.nav:button_run_simulation,
		button_character_menu.nav:button_character_menu,
		button_combat_options_menu.nav:button_combat_options_menu,
		button_debug_menu.nav:button_debug_menu,
		button_quit.nav:button_quit
	}
	main_menu = menu("Main Menu",main_menu_buttons)
	controller = menuControl(main_menu)
	controller.start()

def character_options_menu():
	"""The character Menu"""
	replit.clear()
	button_create_character = menubutton("Create Character",1,create_character_menu)
	button_view_stats = menubutton("View Stats",2,view_stats)
	button_go_back = menubutton("Go Back",0,go_back,main_menu)
	character_menu_buttons = {
		button_create_character.nav:button_create_character,
		button_view_stats.nav:button_view_stats,
		button_go_back.nav:button_go_back
	}
	character_options_menu = menu("Character Options",character_menu_buttons,"Main Menu") 
	controller = menuControl(character_options_menu)
	controller.start()

def combat_options_menu():
	"""The menu for combat options"""
	replit.clear()
	button_create_character = menubutton("Create Character",1,create_character_menu)
	button_view_stats = menubutton("View Stats",2,view_stats)
	button_back = menubutton("Go Back",0,go_back,main_menu)
	combat_menu_buttons = {
		button_create_character.nav:button_create_character,
		button_view_stats.nav:button_view_stats,
		button_back.nav:button_back
	}
	combat_options_menu = menu("Combat Menu",combat_menu_buttons,"Main Menu")
	controller = menuControl(combat_options_menu)
	controller.start()

def debug_menu(pass_check = None):
	"""Menu for all debug options"""
	replit.clear()
	debug_password = 1234
	if pass_check is None:
		pass_check = input ("Enter password to begin debug>>")
	if pass_check == str(debug_password):
		wait (1)
		replit.clear()
		button_run_debug = menubutton("Run One-Hit Debug",1,debug_hit)
		button_go_back = menubutton("Go Back",0,go_back,main_menu)
		debug_buttons = {
			button_run_debug.nav:button_run_debug,
			button_go_back.nav: button_go_back
		}
		debug_menu_mode = menu("Debug Mode",debug_buttons,"Main Menu")
		controller = menuControl(debug_menu_mode)
		controller.start()
	else:
		print ("Sorry, that password is not correct. Returning to Main Menu...")
		wait(1)
		main_menu()

## Actual Program Start ##

main_menu()
