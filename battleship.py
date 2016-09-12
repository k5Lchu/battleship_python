import pygame
import random
import sys
import socket
import time
from ship import Ship

#initialize pygame
pygame.init()

#window resolution
display_width = 950
display_height = 500

#both height and width of board blocks 10x10 board
board_dim = 10
#square tile dimension in pixels
tile_dim = 40

#current player's turn flag
curr_turn = False

#hit limits for ships
carrier_max = 5
battleship_max = 4
sub_max = cruiser_max = 3
destroyer_max = 2

#Target FPS
GAME_FPS = 30
REG_FPS = 15

#position vectors of ships [0] and [1] are x and y coordinates in pixels
#[2] and [3] are board coordinates (0 through 9)
carrier_pos = (5,455,-1,-1)
battleship_pos = (210,455,-1,-1)
submarine_pos = (500,455,-1,-1)
cruiser_pos = (375,455,-1,-1)
destroyer_pos = (625,455,-1,-1)

#various color definitions
white = (255,255,255)
dark_white = (220,220,220)
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)
ready_but_color = (204,204,0)
ready_but_active_color = (255,255,0)

#setup display window and game clock
gameDisplay = pygame.display.set_mode((display_width,display_height))
clock = pygame.time.Clock()

#get image textures for use
battle_waterIMG = pygame.image.load('battle_water.png').convert_alpha()
bckgrnd_waterIMG = pygame.image.load('dark_water.png').convert_alpha()

carrierIMG = pygame.image.load('carrier.png').convert_alpha()
battleshipIMG = pygame.image.load('battleship.png').convert_alpha()
cruiserIMG = pygame.image.load('cruiser.png').convert_alpha()
submarineIMG = pygame.image.load('submarine.png').convert_alpha()
destroyerIMG = pygame.image.load('destroyer.png').convert_alpha()

#create ship objects
carrier = Ship(carrier_pos,carrierIMG,carrier_max,1,'car')
battleship = Ship(battleship_pos,battleshipIMG,battleship_max,2,'bat')
submarine = Ship(submarine_pos,submarineIMG,sub_max,3,'sub')
cruiser = Ship(cruiser_pos,cruiserIMG,cruiser_max,4,'cru')
destroyer = Ship(destroyer_pos,destroyerIMG,destroyer_max,5,'des')

#consolidtae all ships into an array
all_ships = [carrier,battleship,submarine,cruiser,destroyer]

#legend for board tile locations. Made so letters/numbers are not continuously rendered.
letters = (
	pygame.font.Font('freesansbold.ttf',25).render('A', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('B', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('C', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('D', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('E', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('F', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('G', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('H', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('I', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('J', False, ready_but_color))

nums = (
	pygame.font.Font('freesansbold.ttf',25).render('1', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('2', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('3', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('4', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('5', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('6', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('7', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('8', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('9', False, ready_but_color),
	pygame.font.Font('freesansbold.ttf',25).render('10', False, ready_but_color))


# main board_drawing method
def draw_board(display_surface):

	#starting x and y coordinate
	x = 50
	y = 50

	#margin size and board legend x location for player board are both 50
	delta_margin = player_letter_ref_x = 50

	#board legend x location for enemy board is at 500
	enemy_letter_ref_x = 500

	#max y location for board legend
	y_max = 411

	#max x location for board legend of player and enemy board
	x_player_max = 411
	x_enemy_max = 861

	#draw background
	gameDisplay.fill(white)
	display_surface.blit(bckgrnd_waterIMG,(0,0))
	display_surface.blit(battle_waterIMG,(x,y))

	#draw individual tile outlies
	#410 is max y coordinate
	#410 and 860 are max x coordinates for respective boards 
	#left board (player board)
	curr_num = 0
	curr_letter = 0
	while (x < x_player_max):
		#draw number legend with slight location offsets
		display_surface.blit(nums[curr_num],(x+10,y-30))
		curr_num += 1
		while (y < y_max):
			#draw tiles and only draw letter legend only once
			pygame.draw.rect(display_surface,green,(x,y,tile_dim,tile_dim),1)
			if x == player_letter_ref_x:
				display_surface.blit(letters[curr_letter],(x-30,y+5))
				curr_letter += 1
			y += tile_dim
		x += tile_dim
		y = delta_margin

	curr_num = 0
	curr_letter = 0

	#account for middle barrier of 50 pixels
	x += delta_margin

	#draw enemy side backrgound of board
	display_surface.blit(battle_waterIMG,(x,y))

	#right board(enemy/attacking board)
	while (x < x_enemy_max):
		display_surface.blit(nums[curr_num],(x+10,y-30))
		curr_num += 1
		while (y < y_max):
			pygame.draw.rect(display_surface,green,(x,y,tile_dim,tile_dim),1)
			if x == enemy_letter_ref_x:
				display_surface.blit(letters[curr_letter],(x-30,y+5))
				curr_letter += 1
			y += tile_dim
		x += tile_dim
		y = delta_margin

#draw ships in current position. during the prep/setting up phase
#ships are drawn in default position before placement and move with mouse when selected.
#otherwise, ships are drawn in their placed positions
def draw_setup_ships(display_surface,mouse_x,mouse_y,ship,ship_list,setting_up):
	for boat in ship_list:
		if setting_up and ship is boat:
			boat.draw_ship(display_surface,mouse_x,mouse_y,True)
		else:
			pos = boat.get_pixel_pos()
			boat.draw_ship(display_surface,pos[0],pos[1],False)

#draw end game page
def draw_end_game(display_surface,game_won,fps_clock):
	#endgame resource image files
	winIMG = pygame.image.load('game_over_win.png').convert_alpha()
	loseIMG = pygame.image.load('game_over_lose.png').convert_alpha()

	#endgame loop. player must close window to exit.
	#have not implemeting "play again" and player must reconnect to play once more
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		if game_won:
			display_surface.blit(winIMG,(0,0))
		else:
			display_surface.blit(loseIMG,(0,0))
		pygame.display.update()
		fps_clock.tick(REG_FPS)

#method that contains the main loops for the intro screen and tcp
#connection screens
def intro_and_connection_loop(display_surface,conn,fps_clock):
	#pre load necessary textures and pre render all needed texts
	introIMG = pygame.image.load('intro_page.png').convert_alpha()
	connectIMG = pygame.image.load('conection_page.png').convert_alpha()
	play_msg = pygame.font.Font('freesansbold.ttf',40).render('Play', False, black)
	connect_msg = pygame.font.Font('freesansbold.ttf',30).render('Connect', False, black)
	server_msg = pygame.font.Font('freesansbold.ttf',30).render('Server', False, black)
	client_msg = pygame.font.Font('freesansbold.ttf',30).render('Client', False, black)
	ip_input_msg = pygame.font.Font('freesansbold.ttf',20).render('Please input IP address to connect:', False, black)
	port_input_msg = pygame.font.Font('freesansbold.ttf',20).render('Please input port number to connect:', False, black)

	#set dimensions of buttons
	but_dim = (160,80)
	#position vectors of various buttons
	play_but_pos = ((display_width - but_dim[0])/2,(display_height - but_dim[1])/2)
	connect_but_pos = ((display_width - but_dim[0])/2,((display_height*3)/4)-(but_dim[1]/2))
	server_but_pos = ((display_width/4)-(but_dim[0]/2),(display_height/4)+(but_dim[1]/2))
	client_but_pos = (((display_width*3)/4)-(but_dim[0]/2),(display_height/4)+(but_dim[1]/2))

	#flags to tell if at intro or connection setup screens
	intro = True
	connecting = server = client = False

	#rect of various buttons used to detect when a button is clicked
	play_rect = client_rect = server_rect = connect_rect = ip_rect = port_rect = None

	#positon vector to keep track of mouse movements
	pos = (-1,-1)

	#port and ip strings inputted from user
	port = ''
	ip = ''
	#flags for if user has focused in on ip_input or port_input
	ip_input_selected = False
	port_input_selected = False

	#beginning intro loop
	while intro:
		#check for if user input
		for event in pygame.event.get():
			#if user closes window and quits
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			#if user clicks mouse (button = 1 is leftclick)
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					#record mouse position and check if play button pressed
					pos = event.pos
					if play_rect is not None and play_rect.collidepoint(pos[0],pos[1]):
						intro = False
						connecting = True
			#if user moves mouse record mouse position
			if event.type == pygame.MOUSEMOTION:
				pos = event.pos

		#draw GUI elements (background and buttons)
		display_surface.blit(introIMG,(0,0))
		if play_rect is not None and play_rect.collidepoint(pos[0],pos[1]):
			play_rect = draw_intro_buttons(display_surface,play_msg,ready_but_active_color,play_but_pos,but_dim)
		else:
			play_rect = draw_intro_buttons(display_surface,play_msg,ready_but_color,play_but_pos,but_dim)

		#update window and miantain desired fps
		pygame.display.update()
		fps_clock.tick(REG_FPS)

	#main loop during tcp connection stage
	while connecting:
		#check for user input
		for event in pygame.event.get():
			#check if user wants to quit
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			#check if user clicks a mouse button (only left click here)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					#record mouse position
					pos = event.pos
					#check if user chooses to host or connect to a host
					if not server and not client:
						if server_rect is not None and server_rect.collidepoint(pos[0],pos[1]):
							server = True
						elif client_rect is not None and client_rect.collidepoint(pos[0],pos[1]):
							client = True
					else:
						#check if user is connecting to a host, allow ip input
						if client:
							if ip_rect is not None and ip_rect.collidepoint(pos[0],pos[1]):
								ip_input_selected = True
							else:
								ip_input_selected = False

						#focus and allow port input
						if port_rect is not None and port_rect.collidepoint(pos[0],pos[1]):
							port_input_selected = True
						else:
							port_input_selected = False

						#check if connect button clicked and end connection stage
						if connect_rect is not None and connect_rect.collidepoint(pos[0],pos[1]):
							connecting = False
							#give char to show server or client, int for port, string for ip
							if server:
								return ('s',int(port),'-1')
							elif client:
								return ('c',int(port),ip)
			#check if mouse moves, if so record position
			elif event.type == pygame.MOUSEMOTION:
				pos = event.pos
			#check if 
			elif event.type == pygame.KEYDOWN:
				#get user inputted char
				in_char = handle_key_events(event.key)
				#if valid input
				if in_char is not None:
					#if inputting ip, edit ip string
					if ip_input_selected:
						if in_char is 'b':
							ip = ip[:-1]
						elif in_char is 'd':
							ip_input_selected = False
						else:
							ip += in_char
					#if inputting port, edit port string
					elif port_input_selected:
						if in_char is 'b':
							port = port[:-1]
						elif in_char is 'd':
							port_input_selected = False
						else:
							port += in_char

		#draw background for connection page
		display_surface.blit(connectIMG,(0,0))

		#draw GUI components for when user is choosing to be a host or client
		if not server and not client:
			if server_rect is not None and server_rect.collidepoint(pos[0],pos[1]):
				server_rect = draw_intro_buttons(display_surface,server_msg,ready_but_active_color,server_but_pos,but_dim)
			else:
				server_rect = draw_intro_buttons(display_surface,server_msg,ready_but_color,server_but_pos,but_dim)
			if client_rect is not None and client_rect.collidepoint(pos[0],pos[1]):
				client_rect = draw_intro_buttons(display_surface,client_msg,ready_but_active_color,client_but_pos,but_dim)
			else:
				client_rect = draw_intro_buttons(display_surface,client_msg,ready_but_color,client_but_pos,but_dim)
		#draw GUI components for when user is a client or host
		else:
			ip_pos = (display_width/2,display_height/2)
			port_pos = (display_width/2,(display_height/4)+tile_dim)
			if client:
				if ip_rect is not None and (ip_input_selected or ip_rect.collidepoint(pos[0],pos[1])):
					ip_rect = draw_text_box(display_surface,ip_input_msg,ip,white,ip_pos)
				else:
					ip_rect = draw_text_box(display_surface,ip_input_msg,ip,dark_white,ip_pos)

			if port_rect is not None and (port_input_selected or port_rect.collidepoint(pos[0],pos[1])):
				port_rect = draw_text_box(display_surface,port_input_msg,port,white,port_pos)
			else:
				port_rect = draw_text_box(display_surface,port_input_msg,port,dark_white,port_pos)

			if connect_rect is not None and connect_rect.collidepoint(pos[0],pos[1]):
				connect_rect = draw_intro_buttons(display_surface,connect_msg,ready_but_active_color,connect_but_pos,but_dim)
			else:
				connect_rect = draw_intro_buttons(display_surface,connect_msg,ready_but_color,connect_but_pos,but_dim)

		pygame.display.update()
		fps_clock.tick(REG_FPS)

#main draw method for rendering various buttons during intro and connecting phase
def draw_intro_buttons(display_surface,msg,color,pos,dim):
	#draw button rectangle
	but_rect = pygame.draw.rect(display_surface,color,(pos[0],pos[1],dim[0],dim[1]))
	#draw button text and return button rectangle for click event purposes
	msg_rect = msg.get_rect(center=(pos[0]+(dim[0]/2),pos[1]+(dim[1]/2)))
	display_surface.blit(msg,msg_rect)
	return but_rect

#draw notification boxes onto the screen
def draw_text_box(display_surface,msg,curr_val,color,pos):
	text_box_dim = (150,30)
	#draw boxes to allow user to input text
	text_box_rect = pygame.draw.rect(display_surface,color,(pos[0]-(text_box_dim[0]/2),pos[1]-(text_box_dim[1]/2),text_box_dim[0],text_box_dim[1]))
	#render recorded user input onto the screen
	curr_val_msg = pygame.font.Font('freesansbold.ttf',15).render(curr_val, False, black)
	center_pos = text_box_rect.center
	curr_val_rect = curr_val_msg.get_rect(center=center_pos)
	display_surface.blit(curr_val_msg,curr_val_rect)
	msg_rect = msg.get_rect(center=(center_pos[0],center_pos[1]-40))
	display_surface.blit(msg,msg_rect)
	return text_box_rect
	
#return the correct char for a key input
def handle_key_events(key):
	if key == pygame.K_0:
		return '0'
	elif key == pygame.K_1:
		return '1'
	elif key == pygame.K_2:
		return '2'
	elif key == pygame.K_3:
		return '3'
	elif key == pygame.K_4:
		return '4'
	elif key == pygame.K_5:
		return '5'
	elif key == pygame.K_6:
		return '6'
	elif key == pygame.K_7:
		return '7'
	elif key == pygame.K_8:
		return '8'
	elif key == pygame.K_9:
		return '9'
	elif key == pygame.K_PERIOD:
		return '.'
	elif key == pygame.K_BACKSPACE:
		return 'b'
	elif key == pygame.K_RETURN:
		return 'd'
	else:
		return None

#method to start host session
def start_server(conn,port):
	host = ''

	#bind socket to select port
	try:
		conn.bind((host,port))
	except socket.error as e:
		print(str(e))

	#wait for a client to connect
	conn.listen(1)
	print('Waiting for connection...')

	#accept connection
	sock, addr = conn.accept()
	print('Connected to: ' + addr[0] + ': ' + str(addr[1]))

	#send success connection message
	sock.send(str.encode('connected'))
	#return new socket
	return sock

#method to connect to host session
def connect_server(conn,port,ip):
	#connect to a given ip and port
	conn.connect((ip,port))

	#get successful connection message
	conn_success = conn.recv(4096)
	if conn_success.decode() == 'connected':
		print('Connection successful!')
	else:
		print('Connection failed')
	

################################# Setup-Ships_Phase Mathods ###################################

#highlight tiles as a ship is hovering over them
def illuminate_tiles(display_surface,ship,startx,starty,collision):
	#if no ship selected, return
	if ship is None:
		return

	#highlight color variable
	draw_color = None

	#constants refering to tile positions in pixels
	min_val = 50
	max_val = 450

	#max x coordinate of valid tile
	ship_len_max = max_val-tile_dim+1
	
	#if trying to place ship where another ship is placed or outside board
	#draw in red, otherwise green
	if collision:
		draw_color = red
	elif not ship.rot and (startx < min_val or startx+(tile_dim*(ship.life_limit-1)) > max_val):
		draw_color = red
	elif ship.rot and (starty < min_val or starty+(tile_dim*(ship.life_limit-1)) > max_val):
		draw_color = red
	else:
		draw_color = green

	#variables for ship length in tiles and if ship is rotated
	num_tiles, is_rotated = ship.life_limit, ship.rot

	#-30 to account for mouse offset when dragging ships
	new_x = new_y = -30

	#get board indx using current mouse position
	while new_x < startx:
		if (new_x + tile_dim) > startx:
			break
		new_x += tile_dim
	while new_y < starty:
		if (new_y + tile_dim) > starty:
			break
		new_y += tile_dim

	#highlight tiles vertically, otherwise horizontally
	if is_rotated:
		for y in range(0,num_tiles):
			next_y = new_y + (tile_dim * y)
			if (min_val - 1) < next_y < ship_len_max and (min_val - 1) < startx < (max_val + 1):
				pygame.draw.rect(display_surface,draw_color,(new_x,next_y,tile_dim,tile_dim))
	else:
		for x in range(0,num_tiles):
			next_x = new_x + (tile_dim * x)
			if (min_val - 1) < next_x < ship_len_max and (min_val -1) < starty < (max_val + 1):
				pygame.draw.rect(display_surface,draw_color,(next_x,new_y,tile_dim,tile_dim))

#check what ship the user has chosen using mouse position
def chosen_ship(click_x,click_y,ship_list):
	#check every ship until the correct one is found or none
	for ship in ship_list:
		if ship.selected(click_x,click_y):
			ship.placed = False
			return ship
	return None

#check if ship placement choice conflicts with another placement
def check_collision(ship,pos_x,pos_y,ship_list):
		if ship is not None:
			new_x = new_y = -30
			board_indx_x = board_indx_y = -2

			#get board indx using mouse positions
			while new_x < pos_x:
				if (new_x + tile_dim) > pos_x:
					break
				new_x += tile_dim
				board_indx_x += 1
			while new_y < pos_y:
				if (new_y + tile_dim) > pos_y:
					break
				new_y += tile_dim
				board_indx_y += 1

			#return collision check result
			return ship.ship_collision(board_indx_x,board_indx_y,ship_list)

#check if all ships have been placed down
def all_ships_placed(ship_list):
	for ship in ship_list:
		if not ship.placed:
			return False
	return True

#draw the button that when clicked will set the final playing field
def draw_finish_prep_button(display_surface,but_color,text_surf):
	button_width, button_height = 80,40
	x, y = 210, 455
	rdy_button_rect = pygame.draw.rect(display_surface,but_color,(x,y,button_width,button_height))	
	ready_text_rect = text_surf.get_rect(center=(x+(button_width/2), y+(button_height/2)))
	display_surface.blit(text_surf,ready_text_rect)
	return rdy_button_rect

#create board using 2d array and return it
def set_final_field(ship_list):
	#field[x][y]
	player_field = [[0]*board_dim for i in range(board_dim)]
	for ship in ship_list:
		board_x, board_y = ship.pos[2], ship.pos[3]
		#for each ship, mark position on the board with unique identity int
		for i in range(0,ship.life_limit):
			player_field[board_x][board_y] = ship.num_identity
			if ship.rot:
				board_y += 1
			else:
				board_x += 1
	return player_field

# main loop for setting up phase of game (placing ships down into final positions)
def prep_field_loop(display_surface,ship_list,fps_clock,conn):
	placing_ships = True

	#string to hold current selected ship during prep phase
	curr_ship = None
	num_ships_placed = 0

	#upper left and upper right corner of ready button
	ready_but_min = (210,455)
	ready_but_max = (290,495)

	#varibale to hold the final player field layout
	final_player_field = None

	#position variables when drawing
	pos_x = 0
	pos_y = 0

	#flag to check if there is a placement conflict
	#rectangle to check when user clicks the reayd button
	collision = False
	ready_but_rect = None

	#pre-render button and notification texts
	ready_text_surface = pygame.font.Font('freesansbold.ttf',15).render('Ready Up!', False, black)
	enemy_prep_msg = pygame.font.Font('freesansbold.ttf',30).render('Enemy Preparing...', False, red)

	#main loop for the prep phase
	while placing_ships:
		# check for user input
		for event in pygame.event.get():
			#check if user wants to quit
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
			#check if user clicks a mouse button
			elif event.type == pygame.MOUSEBUTTONDOWN:
				#record mouse position
				pos_x, pos_y = event.pos
				#if user right clicks, rotate selected ship
				if event.button == 3:
					if curr_ship is not None:
						curr_ship.rotate_ship(display_surface)
				#if user left clicks
				elif event.button == 1:
					#check if user is ready and clicks ready button
					#if so, set final field and return that field, ending prep phase
					if ready_but_rect is not None:
						if ready_but_rect.collidepoint(pos_x,pos_y):
							final_player_field = set_final_field(ship_list)
							placing_ships = False
							return final_player_field
						ready_but_rect = None
					#select a ship for placement, otherwise place down current ship
					if curr_ship is None:
						curr_ship = chosen_ship(pos_x,pos_y,ship_list)
					else:
						error = curr_ship.place_ship(pos_x,pos_y,ship_list)
						#if successful placement, prepare for next ship selection
						if error != -1:
							curr_ship.placed = True
							curr_ship = None
			#if mouse motion detected, record position and check for placement collision
			elif event.type == pygame.MOUSEMOTION:
				pos_x, pos_y = event.pos
				collision = check_collision(curr_ship,pos_x,pos_y,ship_list)

		#draw the game board
		draw_board(display_surface)

		#draw notification on enemy board to show that enemy is preparing
		enemy_prep_surface = pygame.draw.rect(display_surface,white,(500+60,50+(40*3),280,40))
		gameDisplay.blit(enemy_prep_msg,(enemy_prep_surface.x+5,enemy_prep_surface.y+5))

		#illuminate tiles to show valid placement locations and then draw the ships
		if curr_ship is not None:
			illuminate_tiles(gameDisplay,curr_ship,pos_x,pos_y,collision)
		draw_setup_ships(display_surface,pos_x,pos_y,curr_ship,ship_list,True)

		#check if all ships are placed down, if so display the ready button
		if all_ships_placed(ship_list):
			if ready_but_min[0] < pos_x < ready_but_max[0] and ready_but_min[1] < pos_y < ready_but_max[1]:
				ready_but_rect = draw_finish_prep_button(gameDisplay,ready_but_active_color,ready_text_surface)
			else:
				ready_but_rect = draw_finish_prep_button(gameDisplay,ready_but_color,ready_text_surface)

		pygame.display.update()
		fps_clock.tick(GAME_FPS)

##################################### End of setup phase methods ###################################

##################################### Main battle phase mathods #####################################

#draw the button to confirm attack
def draw_attack_button(display_surface,color,text_surf):
	button_width, button_height = 80,40
	x, y = 710, 455
	rdy_button_rect = pygame.draw.rect(display_surface,color,(x,y,button_width,button_height))	
	ready_text_rect = text_surf.get_rect(center=(x+(button_width/2), y+(button_height/2)))
	display_surface.blit(text_surf,ready_text_rect)
	return rdy_button_rect

#check if the player has lost the game
def game_over(ship_list):
	for ship in ship_list:
		if not ship.ship_dead():
			return False
	return True

#main attack method which is called when an attack is confirmed
def attack(display_surface,attack_loc,conn):
	#loop to send attack to enemy until attack successfully recieved
	while True:
		#check for quit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
		#try sending attack and retry if attack couldn't be recieved
		try:
			conn.send(str.encode('{:d}{:d}'.format(attack_loc[0],attack_loc[1])))
			break
		except socket.error as e:
			continue

	#variable to store result of attack
	result = ''

	#loop to poll for attack result from enemy
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
		#try to get attack result, if unsuccessful try again
		try:
			result = conn.recv(4096).decode()
			break
		except socket.error as e:
			continue
	
	#formatted result to be returned
	return_result = []

	#H signals a hit
	if result[0] is 'H':
		return_result.append(True)
	else:
		return_result.append(False)

	#W signals player has destroyed enemy fleet
	if result[1] is 'W':
		return_result.append(True)
	else:
		return_result.append(False)

	#return the formatted result of the attack
	return (return_result[0],return_result[1])

#return board position of a selected tile by the player
def select_tile(pos_x,pos_y,battle_field):
	#if invalid tile, return invalid board position
	if pos_x < 500 or pos_x > 900:
		return (-1,-1)
	elif pos_y < 50 or pos_y > 450:
		return (-1,-1)

	#min tile x and y pixel coordinates
	tile_x = 500
	tile_y = 50

	#board indx variables starting at 0,0
	board_indx_x = board_indx_y = 0

	#get board position of chosen tile
	while tile_x < pos_x:
		if (tile_x + tile_dim) > pos_x:
			break
		tile_x += tile_dim
		board_indx_x += 1
	while tile_y < pos_y:
		if (tile_y + tile_dim) > pos_y:
			break
		tile_y += tile_dim
		board_indx_y += 1

	return (board_indx_x,board_indx_y)

#check if selected tile is valid
def valid_tile(board_pos,battle_field):
	x, y = board_pos
	#if board coordinate out of bounds return false
	if x < 0 or x > 9 or y < 0 or y > 9:
		return False
	#if board coordinate is tile that has not been hit, return true
	elif battle_field[x][y] == 0:
		return True
	return False

#illuminate a certain tile on the enemy board
def illuminate_tile(display_surface,curr_pos,color):
	pos_x, pos_y = 500+(tile_dim*curr_pos[0]), 50+(tile_dim*curr_pos[1])
	pygame.draw.rect(display_surface,color,(pos_x,pos_y,tile_dim,tile_dim))

#draw hit and miss markers recorded during the game
def draw_hits_misses(display_surface,player_record,enemy_record,hit_mark,miss_mark):
	#draw moves made by enemy onto the board
	for move in enemy_record:
		pos = move[0]
		draw_x, draw_y = (pos[0]*tile_dim)+50,(pos[1]*tile_dim)+50
		if move[1]:
			display_surface.blit(hit_mark,(draw_x,draw_y))
		else:
			display_surface.blit(miss_mark,(draw_x,draw_y))
	#draw moves made by the player onto the board
	for move in player_record:
		pos = move[0]
		draw_x, draw_y = (pos[0]*tile_dim)+500,(pos[1]*tile_dim)+50
		if move[1]:
			display_surface.blit(hit_mark,(draw_x,draw_y))
		else:
			display_surface.blit(miss_mark,(draw_x,draw_y))

#wait for enemy to send attack move
def wait_for_enemy_move(conn):
	enemy_move = ''
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
		try:
			enemy_move = conn.recv(4096).decode()
			break
		except socket.error as e:
			continue
	return (int(enemy_move[0]),int(enemy_move[1]))

#process enemy attack and send attack result
def process_and_send_response(conn,enemy_move,curr_player_field,ship_list):
	hit = False
	win = False
	response = []
	
	#check if enemy hit a player ship and lower ship health
	if curr_player_field[enemy_move[0]][enemy_move[1]] != 0:
		hit_tile = curr_player_field[enemy_move[0]][enemy_move[1]]

		if hit_tile == 1:
			ship_list[0].ship_hit()
		elif hit_tile == 2:
			ship_list[1].ship_hit()
		elif hit_tile == 3:
			ship_list[2].ship_hit()
		elif hit_tile == 4:
			ship_list[3].ship_hit()
		elif hit_tile == 5:
			ship_list[4].ship_hit()

		hit = True

	#check if the attack moves sinks final player ship
	if game_over(ship_list):
		win = True

	#format response to the attack
	if hit:
		response.append('H')
	else:
		response.append('M')
	if win:
		response.append('W')
	else:
		response.append('N')

	#send response to the enemy
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
		try:
			conn.send(str.encode('{:s}{:s}'.format(response[0],response[1])))
			break
		except socket.error as e:
			continue

	return hit

#draw notification message in middle of screen
def draw_center_msg(display_surface,msg,width,height):
	x, y = (display_width - width)/2, (display_height - height)/2
	pygame.draw.rect(display_surface,white,(x,y,width,height))
	msg_rect = msg.get_rect(center=(display_width/2, display_height/2))
	display_surface.blit(msg,msg_rect)

#highlight selected/hovered-over tile and draw attack button when a tile is chosen
def draw_tile_selection(display_surface,sel_tile,hover_tile,mouse_pos,attack_but_msg,enemy_board):
	button_rect = None
	if sel_tile[0] != -1:
		illuminate_tile(display_surface,sel_tile,green)
		if 710 < mouse_pos[0] < 790 and 455 < mouse_pos[1] < 495:
			button_rect = draw_attack_button(display_surface,ready_but_active_color,attack_but_msg)
		else:
			button_rect = draw_attack_button(display_surface,ready_but_color,attack_but_msg)

	if valid_tile(hover_tile,enemy_board):
		illuminate_tile(display_surface,hover_tile,green)
	else:
		if hover_tile[0] != -1:
			illuminate_tile(display_surface,hover_tile,red)

	return button_rect

#main loop for the battle phase
def battle_loop(display_surface,ship_list,player_field,fps_clock,conn):
	#variables to signify if player turn or enemy turn
	player_turn = curr_turn

	#variables to hold current mouse position and current tile chosen position
	pos = (0,0)
	curr_tile = (-1,-1)

	#arrays to hold record enemy and player moves
	enemy_moves = []
	player_moves = []

	#win flag
	win = False

	#enemy board
	enemy_field = [[0]*board_dim for i in range(board_dim)]

	#pre-rendered texts to increase performance
	#hit_msg = pygame.font.Font('freesansbold.ttf',35).render('Successful Hit!', False, red)
	#miss_msg = pygame.font.Font('freesansbold.ttf',35).render('Missed', False, red)
	curr_turn_msg = pygame.font.Font('freesansbold.ttf',35).render('Your Turn', False, red)
	enemy_turn_msg = pygame.font.Font('freesansbold.ttf',35).render('Enemy Turn', False, red)

	attack_text_surface = pygame.font.Font('freesansbold.ttf',15).render('Attack', False, black)
	#variable for attack button rectangle for click event purposes
	attack_but_rect = None

	#get image resources for hit/miss markers
	hitIMG = pygame.image.load('hit_marker.png').convert_alpha()
	missIMG = pygame.image.load('miss_marker.png').convert_alpha()

	#position of tile being hovered over
	hover_tile = (-1,-1)

	#flag for when turns are to be switched
	switch_turn = True

	#main battle loop
	while not game_over(ship_list):
		#check for user input
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				conn.close()
				pygame.quit()
				quit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				pos = event.pos
				#if player turn and left clicks
				if player_turn and event.button == 1:
					#if clicked on attack button
					if attack_but_rect is not None:
						if attack_but_rect.collidepoint(pos[0],pos[1]):
							#attack enemy and get result
							result,win = attack(display_surface,curr_tile,conn)
							#record move
							if result:
								player_moves.append((curr_tile,True))
								enemy_field[curr_tile[0]][curr_tile[1]] = 1
							else:
								player_moves.append((curr_tile,False))
								enemy_field[curr_tile[0]][curr_tile[1]] = -1
							#reset tile variables and begin switching turns
							curr_tile = (-1,-1)
							hover_tile = (-1,-1)
							switch_turn = True
							#if player sinks final enemey ship, battle loop ends
							if win:
								return win
					#select current tile to be attacked and check if tile is valid
					sel_tile = select_tile(pos[0],pos[1],enemy_field)
					if valid_tile(sel_tile,enemy_field):
						curr_tile = sel_tile
					if curr_tile[0] == -1:
						attack_but_rect = None
			#check for mouse moved, highlight tile being hovered on
			elif event.type == pygame.MOUSEMOTION:
				pos = event.pos
				if player_turn:
					hover_tile = select_tile(pos[0],pos[1],enemy_field)

		#draw the game board and player ships
		draw_board(display_surface)
		draw_setup_ships(display_surface,-1,-1,ship_list[0],ship_list,False)

		#draw the hits and misses by both player and enemey
		draw_hits_misses(display_surface,player_moves,enemy_moves,hitIMG,missIMG)
	
		#if not swicthing turn	
		if not switch_turn:
			#if player turn, display attack button, otherwise wait for enemy attack and return response
			if player_turn:
				attack_but_rect = draw_tile_selection(display_surface,curr_tile,hover_tile,pos,attack_text_surface,enemy_field)
			else:
				pygame.display.update()
				enemy_move = wait_for_enemy_move(conn)
				hit_success = process_and_send_response(conn,enemy_move,player_field,ship_list)
				enemy_moves.append((enemy_move,hit_success))
				switch_turn = True
				continue
		else:
			#draw notifictaion showing whose turn it is
			if player_turn:
				draw_center_msg(display_surface,enemy_turn_msg,200,80)
			else:
				draw_center_msg(display_surface,curr_turn_msg,200,80)
			player_turn = not player_turn
			switch_turn = False
			pygame.display.update()
			time.sleep(2)
			continue

		pygame.display.update()
		fps_clock.tick(GAME_FPS)

	return win	

##################################### End of battle phase methods ###################################

##################################### Start of game GUI #############################################

#socket used for tcp connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#get connection info from intro loop
connect_info = intro_and_connection_loop(gameDisplay,s,clock)

#setup connection
if connect_info[0] is 's':
	s = start_server(s,connect_info[1])
else:
	connect_server(s,connect_info[1],connect_info[2])
	curr_turn = True

#begin prep phase and get final ship layout
final_board_layout = prep_field_loop(gameDisplay,all_ships,clock,s)

#display wait message while connection is being established
wait_msg = pygame.font.Font('freesansbold.ttf',35).render('Please Wait', False, red)	
wait_msg_rect = wait_msg.get_rect(center=(display_width/2, display_height/2))
wait_msg_box = pygame.draw.rect(gameDisplay,white,wait_msg_rect)
gameDisplay.blit(wait_msg,wait_msg_rect)

pygame.display.update()

#confirm connection successful
s.send(str.encode('ready'))
enemy_response = s.recv(4096)

#set socket to nonblocking mode
s.setblocking(0)

pygame.display.update()

#begin battle
battle_result = battle_loop(gameDisplay,all_ships,final_board_layout,clock,s)

#close connection
s.close()

#draw endgame
draw_end_game(gameDisplay,battle_result,clock)
