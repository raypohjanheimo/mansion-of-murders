import sql
import move
import look
import ask

# This controls text output beyond vanilla print
def fprint (text):
	# Obviously its not implemented yet
	print (text)
	
# This is just to make debug messages stand out, in code and output
def DEBUG (message):
	print ("DEBUG: " + str(message))
	
## VOCABULARY
# Get verbs and prepositions from database
verbs = sql.get_verbs()
prepositions = sql.get_prepositions()

# Get targets as well. Also store them in invidual arrays to further parse commands. 
rooms = sql.get_rooms()

# sql.get_npcs returns a list where [0] is first names and [1] is last names
sql_npcs = sql.get_npcs_names()
first_names = sql_npcs [0]
last_names = sql_npcs [1]
npcs = sql.get_npcs()

# sql.get_directions returns list, [0] is shortcut, [1] is full name
directions = sql.get_directions()
short_directions = directions [0]
long_directions = directions [1]
directions = short_directions + long_directions

targets = rooms + npcs + directions
DEBUG ("targets: " + str(targets) + "\n")



## INITIALIZE MOVE
move.rooms = rooms
move.directions = directions
move.short_directions = short_directions
move.long_directions = long_directions


## INITIALIZE LOOK
look.rooms = rooms
look.npcs = npcs
look.first_names = first_names
look.last_names = last_names
look.directions = directions


## INITIALIZE ASK


## INITIALIZE PLAYER
class Player(object):
	location = 1

player = Player()
move.player = player
look.player = player
ask.player = player
#blame.player = player

# Start at full used actions, so that npcs will move on first turn
player_actions = 3
player_actions_used = player_actions


## GAME LOOP
playing = True
while (playing):
	
	# Check if its time for npcs to move
	if player_actions_used == player_actions:
		fprint("Npcs move")
		player_actions_used = 0
	
	
	# Receive and process input
	# Get input, lower and split it
	# Look for two part words
	# Look for synonyms, and swap
	raw_command = input (">>").lower().split()
	command = []
	word_range = len(raw_command)
	index = 0
	while index < word_range:
		word = raw_command[index]
		
		# Don't look last word, since it can't be first of two part word
		if index < word_range - 1:
			next = raw_command [index + 1]
			
			parts = sql.get_two_part_words(word)
			if parts != None and next in parts:
				command_word = "{0} {1}".format(word, next)
				index += 1
			
			else:
				command_word = word
		
		else:
			command_word = word
		

		
		# Check for synonyms
		command_word = sql.get_word_from_synonym(command_word)
		
		# Check for full name after synonyms
		if command_word in first_names or command_word in last_names:
			command_word = sql.get_full_name(command_word)
		
		command.append (command_word)
		index += 1
	# End of command process loop
	DEBUG (command)
	
	# Parse input
	verb = None
	target1 = None
	preposition = None
	target2 = None
	
	for word in command:
		
		if verb == None:
			if word in verbs:
				verb = word
				
			elif word in directions:
				target1 = word
		
		elif preposition == None:
			
			if word in targets and target1 == None:
				target1 = word
				
			elif word in prepositions:
				preposition = word
				
		elif target2 == None:
			
			if word in targets:
				target2 = word
				

	DEBUG ("{0} {1} {2} {3}".format(verb, target1, preposition, target2))
				
	# Check if player entered only direction
	if target1 in long_directions:
		target1 = sql.short_direction(target1)
	
	if verb == None and target1 in directions:
		verb = 'move'
		
	# Build SQL-query from parsed commands
	if verb:
		# verb ----------------------------------------------------------
		query = "SELECT id FROM actions WHERE verb = '{0}'".format(verb)
		
		# preposition --------------------------------------------------
		if (preposition):
			query += " AND preposition = '{0}'".format(preposition)
		else:
			query += " AND preposition IS NULL"
		
		# targets ------------------------------------------------------
		if target1:
			has_target1 = True
		else:
			has_target1 = False
		query += " AND has_target1 = {0}".format(has_target1)
			
			
		if target2:
			has_target2 = True
		else:
			has_target2 = False
		query += " AND has_target2 = {0}".format(has_target2)
		
		#---------------------------------------------------------------
		query += ";"
		

		# Get Action id
		action = sql.query_single(query)
		
		# Do action, and spend action points
		if (action):
			super = int(action / 10)
			sub = action - super * 10
			
			DEBUG("super: {0}, sub: {1}".format(super, sub))
			
			if super == 1: # MOVE
				fprint(move.move(target2))
				
				player_actions_used +=1
				
			elif super == 2: # LOOK
				if sub == 0:
					fprint(look.look(target2))
				
				elif sub == 1:
					fprint(look.look_around())
		
			elif super == 3: # ASK
				fprint(ask.ask(target1, target2))
				
				player_actions_used += 1
			
		
	else:
		fprint("There was no verb, what do you want to do?")
			


	
## END GAME LOOP	
	
sql.end()



