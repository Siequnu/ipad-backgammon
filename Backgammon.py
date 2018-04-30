# coding: utf-8

# Import 
from scene import *
import sound, random, math, console
from numpy import*

A = Action


class BlackPip (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'emj:Black_Circle', **kwargs)


class WhitePip (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'emj:White_Circle', **kwargs)


class BackgroundImage (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'backgammonWood.PNG', **kwargs)

class Dice (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, **kwargs)


class Hitbox (Scene):
	# Returns rects with hitboxes
	def columnHitbox (self, x, y):
		if (y < self.size.h/2):	# Bottom half of board, box goes up
			return Rect(x - 20, 0, 40, self.size.h/2)	
		else:
			return Rect(x - 20, self.size.h/2, 40, self.size.h)
	
	def pipHitbox (self, x, y):
		return Rect(x - 20, y-20, 40, 40)
		
	def barHitbox (self):
		return Rect(675 - 20, 0, 40, self.size.h)
	
	def diceHitbox (self):
		return Rect(800, 400, 300, 200)

class Game (Scene):	
	def drawInitialPips (self, x, y, n, color):
		# Define the white and black pips
		blackPip = 'emj:Black_Circle'
		whitePip = 'emj:White_Circle'
		
		for i in range (n):
			
			if color == 'black':
				pip = BlackPip (parent=self.blackPips)
				self.pips.append(pip)
				self.blackPipsList.append(pip)
			else:
				pip = WhitePip (parent=self.whitePips)
				self.pips.append(pip)
				self.whitePipsList.append(pip)
			
			pip.position = (x,y)
			pip.size = pip.size * 1.3		

			if y < (self.size.h/2):
				x, y = x, y + 75
			else:
				x, y = x, y - 75
	
	def setup(self):		
		self.background_color = '#08470d' # Set background colour
		
		backgroundImage = BackgroundImage (parent=self)
		backgroundImage.position =  self.size.w/2, self.size.h/2
		backgroundImage.size = backgroundImage.size / 2
		
		# Initialise list to register pips
		self.pips = []
		self.blackPipsList = []
		self.whitePipsList = []
		
		# Initialise variable to track which pip is in motion
		self.dynamicPip = 'None'
		
		self.blackPips = Node (parent = self)
		self.whitePips = Node (parent = self)
		
		# Initialise hitboxes class
		self.hitbox = Hitbox ()
		
		#Dice
		self.dice = Node (parent = self)
		self.leftDice = Dice (parent = self.dice)
		self.leftDice.position = (936, 507)		
		self.leftDice.alpha = 0
		self.rightDice = Dice (parent = self.dice)
		self.rightDice.position = (1050, 507)
		self.rightDice.alpha = 0
		
		
		# Initialise class variables
		self.pileCenters = [
			137, 222.5, 317, 405, 497, 582, 776, 878, 975, 1050, 1134, 1222
			]
		
		# Place pips in rows 
		pipStartPositions = [
			(137, 40, 2, 'white'), 
			(582, 40, 5, 'black'), 
			(878, 40, 3, 'black'), 
			(1220, 40, 5, 'white'), 
			
			(137, (self.size.h-40), 2, 'black'), 
			(582, (self.size.h-40), 5, 'white'), 
			(878, (self.size.h-40), 3, 'white'), 
			(1220, (self.size.h-40), 5, 'black'),	
		]
		
		for i in range(len(pipStartPositions)):	
			x, y, z, color = pipStartPositions[i]
			self.drawInitialPips(x, y, z, color)
		
				
	def touch_began(self, touch):
		# Save Pip and color as class variables
		touchHitbox = self.hitbox.pipHitbox(touch.location.x, touch.location.y)
		for pip in list(self.pips):
			if pip.frame.intersects(touchHitbox):
				self.dynamicPip = (pip)
				# Save initial position if the pip needs to be reset
				pipLocationX, pipLocationY = pip.position.x, pip.position.y
				self.dynamicPipStartingPosition = (pipLocationX, pipLocationY)
				
				# Register the color of the pip that as been picked up
				if self.dynamicPip in self.blackPipsList:
					self.dynamicPipColor = 'black'	
				else:
					self.dynamicPipColor = 'white'	
		
		diceHitbox = self.hitbox.diceHitbox()
		touchHitbox = Rect(touch.location.x, touch.location.y, 1, 1)
		if touchHitbox.intersects(diceHitbox):		
			self.rollDice()				
				
	def collapseColumns (self):
		# Get hitbox for the column
		x, y = self.dynamicPipStartingPosition
		columnHitbox = self.hitbox.columnHitbox(x, y)
		
		# If we removed a pip from the top of the bar, rearrange that
		barHitbox = self.hitbox.barHitbox()
		if columnHitbox.intersects(barHitbox): 
			pipsInColumn = []	
			
			for pip in list(self.pips):
				if pip.frame.intersects(barHitbox):
					pipsInColumn.append(pip)
					
			# Rebuild column
			for columnPip in list(pipsInColumn):
				self.movePip (columnPip, self.size.w/2, y)
				y = y + 75
		else:
			# See if we have chosen the top pip
			pipsInColumn = []	
			
			for pip in list(self.pips):
				if pip.frame.intersects(columnHitbox):
					pipsInColumn.append(pip)
			
			# See if we are in top or bottom half
			if len(pipsInColumn) > 0:
				if pipsInColumn[0].position.y > self.size.h/2:
					topHalf = True
					y = self.size.h - 40
				else:
					topHalf = False
					y = 40
			
				# Rebuild column
				for columnPip in list(pipsInColumn):
					self.movePip (columnPip, columnPip.position.x, y)
					if topHalf is True:
						y = y - 75
					else:
						y = y + 75		
													
	
	def touch_moved(self, touch):
		# If a pip is being moved, update position on screen
		if self.dynamicPip != 'None':
			self.dynamicPip.position = touch.location.x, touch.location.y
							
	
	def touch_ended(self, touch):
		# If we have dropped a pip on top of another one, then move ours up or down by 75.
		if self.dynamicPip != 'None':	
			# Check if dropped illegally			
			droppedPipBox = self.hitbox.columnHitbox(touch.location.x, touch.location.y)
			oppositeColorTilesOnSquare = 0
			
			if self.dynamicPipColor == 'black':
				oppositeColorList = self.whitePipsList
			else:
				oppositeColorList = self.blackPipsList
				
			for pip in list(oppositeColorList):
				if pip.frame.intersects(droppedPipBox):
					oppositeColorTilesOnSquare = oppositeColorTilesOnSquare + 1
					if oppositeColorTilesOnSquare == 1:
						firstPip = pip
			
			# Take appropriate action
			if oppositeColorTilesOnSquare > 1:
				x, y = self.dynamicPipStartingPosition
				self.movePip(self.dynamicPip, x, y)
			elif oppositeColorTilesOnSquare == 1:			
				self.movePipToMiddle(firstPip)
				# Move the capturing piece to the place of the captured piece
				self.movePip(self.dynamicPip, self.dynamicPip.position.x, firstPip.position.y)
			elif oppositeColorTilesOnSquare == 0:
				self.moveToTopOfSameColorPile(touch)
				
			# Collapse collumn if necessary
			self.collapseColumns()
			
		self.dynamicPip = 'None'
		self.dynamicPipColor = 'None'
		
		
	
			
	def findCenteredX (self, x):	
		for i in self.pileCenters:
			distance = abs(x - i)
			try:
				closestDistance
			except NameError: # Will be caught the first time is run, assigns the 2 variables
				closestDistance = distance
				closestPile = i
			else:
				if distance < closestDistance:
					closestDistance = distance
					closestPile = i			
		return closestPile
		
				
	def movePip (self, pip, x, y):
		
		if x != self.size.w/2: # Special case to accomodate rearranging from middle bar
			x = self.findCenteredX(x)
		move_action = Action.move_to(x, y, 0.3, TIMING_SINODIAL)			
		pip.run_action(move_action)
	
	
	def moveToTopOfSameColorPile (self, touch):
		# Move to top of pile of same color pips
		droppedPipBox = self.hitbox.columnHitbox(touch.location.x, touch.location.y)
		pipsInPile = 0
		
		for i in range(0,20):
			for pip in list(self.pips):
				if pip.frame.intersects(droppedPipBox):
					if pip != self.dynamicPip:
						pipsInPile = pipsInPile + 1
						if touch.location.y < (self.size.h/2):
							y = pip.position.y+75
						else:
							y = pip.position.y-75
						self.movePip(self.dynamicPip, self.dynamicPip.position.x, y)
						# Update hitbox position
						if y < (self.size.h/2):
							y = pip.position.y+75
						else:
							y = pip.position.y-75
						droppedPipBox = Rect(pip.position.x, y, 40, 40)
					
		if pipsInPile == 0:
			if self.dynamicPip.position.y < (self.size.h/2):
				y = 40
			else:
				y = self.size.h - 40
			self.movePip(self.dynamicPip, self.dynamicPip.position.x, y)
	
					
	# Function to move a captured pip to the middle of the board	
	def movePipToMiddle (self, capturedPip):
		x, y = self.size.w/2, self.size.h/2
		
		barHitbox = self.hitbox.barHitbox()
		
		for pip in list(self.pips):
			if pip.frame.intersects(barHitbox):
				y = y + 75
		
		move_action = Action.move_to(x, y, 0.7, TIMING_SINODIAL)			
		capturedPip.run_action(move_action)
				
				
	def rollDice(self):
		self.leftDice.alpha = 1
		self.rightDice.alpha = 1
		
		symbols = ['Dice/dice1.PNG', 'Dice/dice2.PNG', 'Dice/dice3.PNG', 'Dice/dice4.PNG', 'Dice/dice5.PNG', 'Dice/dice6.PNG']
		
		leftDice = random.randint(0,5)
		rightDice = random.randint(1,6)
		
		leftPic = ui.Image.named(symbols[leftDice])
		rightPic = ui.Image.named(symbols[rightDice])
		
		leftTexture = Texture(leftPic)
		rightTexture = Texture(rightPic)
	
		self.leftDice.texture = leftTexture
		self.rightDice.texture = rightTexture
		
		self.leftDice.size = 75, 75
		self.rightDice.size = 75, 75
		
if __name__ == '__main__':
	run(Game(), LANDSCAPE, show_fps=False) 

