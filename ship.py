import pygame

#class to represent the ships
class Ship:

	#constructor and attribute declaration
	def __init__(self,pos_vector,ship_img,max_life,num,name):
		self.pos = [pos_vector[0],pos_vector[1],pos_vector[2],pos_vector[3]]
		self.img = ship_img
		self.life_limit = max_life
		self.curr_life = max_life
		#flag for if ship is rotated and placed down
		self.rot = False
		self.placed = False
		#identifictaion units
		self.num_identity = num
		self.name = name

	#return position of ship in pixels
	def get_pixel_pos(self):
		return (self.pos[0],self.pos[1])

	#not used
	def get_board_pos(self):
		return (self.pos[2],self.pos[3])

	#setter to update pixel position of ship
	def update_pix_pos(self,new_pix_x,new_pix_y):
		self.pos[0] = new_pix_x
		self.pos[1] = new_pix_y

	#setter to update board position of ship
	def update_board_pos(self,new_board_x,new_board_y):
		self.pos[2] = new_board_x
		self.pos[3] = new_board_y

	#called when a ship is hit and loses a health point
	def ship_hit(self):
		self.curr_life -= 1

	#used to determine if a ship has completely sunk
	def ship_dead(self):
		if self.curr_life < 1:
			return True
		return False

	#determines if a user selects the ship using mouse position input
	def selected(self,mouse_x,mouse_y):
		pos_rect = self.img.get_rect(topleft=(self.pos[0],self.pos[1]))
		if pos_rect.collidepoint(mouse_x,mouse_y):
			return True
		return False

	#main function to draw the ship onto the board
	def draw_ship(self,displayer,mouse_x,mouse_y,moving):
		#mouse offset so mouse is not at top left corner of the ship texture
		mouse_offset = 20
		#choose to draw the ship moving with the mouse or at last know location
		if moving:
			displayer.blit(self.img,(mouse_x-mouse_offset,mouse_y-mouse_offset))
		else:
			displayer.blit(self.img,(self.pos[0],self.pos[1]))

	#used to rotate the ship tecture and set rotation flag
	def rotate_ship(self,displayer):
		self.img = pygame.transform.rotate(self.img,90)
		self.rot = not self.rot

	#used to place the ship down during prep phase. returns error int of -1 when invalid placement
	def place_ship(self,mouse_x,mouse_y,ship_list):
		#variables to keep track of position checking
		new_x = new_y = 50
		board_indx_x = board_indx_y = 0
		#constants for max board indx, min pixel position, and tile size
		max_board_pos = 9
		min_pixel_pos = 50
		delta_tile_pix = 40

		#if invalid placement, outside board
		if mouse_x < min_pixel_pos or mouse_y < min_pixel_pos:
			return -1

		#get board indx using mouse position
		while new_x < mouse_x:
			if (new_x + delta_tile_pix) > mouse_x:
				break
			board_indx_x += 1
			new_x += delta_tile_pix
		while new_y < mouse_y:
			if (new_y + delta_tile_pix) > mouse_y:
				break
			board_indx_y += 1
			new_y += delta_tile_pix

		#if invalid placement, outside board
		if board_indx_x > max_board_pos or board_indx_y > max_board_pos:
			return -1
		elif ((board_indx_x + self.life_limit - 1) > max_board_pos and not self.rot):
			return -1
		elif ((board_indx_y + self.life_limit - 1) > max_board_pos and self.rot):
			return -1

		#invalid placement, another ship already placed in the position
		if self.ship_collision(board_indx_x,board_indx_y,ship_list):
			return -1

		#with successful placement, update position of ship
		self.update_pix_pos(new_x,new_y)
		self.update_board_pos(board_indx_x,board_indx_y)
		return 0

	#check if there is a ship placement collision
	def ship_collision(self,board_x,board_y,ship_list):
		#compare current ship's position to every other ship's positions
		#until a conflict is found or none is found
		for i in range(0,len(ship_list)):
			tmp_ship = ship_list[i]
			self_x,self_y = board_x,board_y
			if tmp_ship.name is self.name:
				continue
			for point in range(0,self.life_limit):
				other_x,other_y = tmp_ship.pos[2],tmp_ship.pos[3]
				if other_x == -1:
					break
				for other_point in range(0,tmp_ship.life_limit):
					if self_x == other_x and self_y == other_y:
						return True
					if tmp_ship.rot:
						other_y += 1
					else:
						other_x += 1
				if self.rot:
					self_y += 1
				else:
					self_x += 1
		return False
