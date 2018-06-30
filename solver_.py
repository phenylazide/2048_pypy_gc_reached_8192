import engine, random, curses

COLORS = {0:0,2:1,4:2,8:3,16:4,32:5,64:6,128:7,256:8,512:9,1024:10,2048:11,4096:12,8192:13,16384:13,32768:12,65536:12}

global field
#field = [[int(180/((3-x)**2*1.5+(3-y)**2))+1 if (x!=3 or y!=3) else 720 for y in range(4)] for x in range(4)]
#field = [[9, 11, 13, 14], [13, 19, 26, 31], [18, 33, 73, 121], [21, 46, 181, 720]]
field = [[0, 0, 1, 1], [0, 1, 2, 4], [2, 4, 8, 12], [15, 20, 25, 50]]   
## best score field, together with repeat punish

global b_fld_  ## blank field 
b_fld_ = [[2,2,1,1],
					[2,1,1,1],
					[1,1,1,-1],
					[1,1,-1,-2]]
global runs_power_dict  ## according to blank spot, if blank spot less, runs heavily increased.
#runs_power = [10+2**(10-n) if n<10 else 10 for n in range(16)]
runs_power_dict=[1034, 522, 266, 138, 
									74, 42, 26, 18, 
									14, 12, 10, 10, 
									10, 10, 10, 10]

average_dict = {0:1,1:1,2:5,4:5,8:5,16:10,32:10,64:10,128:20,256:50,512:60,1024:100,2048:200,4096:280,8192:300,16384:300,32768:300,65536:300,131072:300,
        }

global max_depth_dict  ## according to len(spots)
max_depth_dict = {0:7,1:7,2:6,3:6,
									4:6,5:5,6:5,7:4,
									8:3,9:3,10:3,11:3,
								12:3,13:3,14:3,15:3,16:3}
global get_zhishu_dict
get_zhishu_dict = {0:0,2:1,4:2,8:3,16:4,32:5,64:6,128:7,256:8,512:9,1024:10,2048:11,4096:12,8192:13,16384:14,32768:15,65536:16,131072:17,
        }

def makeGame():
	"""
	Creates a new instance of a game
	"""
	game = engine.Engine()
	return game

def drawBoard(board, screen):
	"""
	Draws a given board on a given curses screen
	"""
	for row in enumerate(board):
		for item in enumerate(row[1]):
			screen.addstr(8+3*row[0], 40+6*item[0], str(item[1]), curses.color_pair(COLORS[item[1]]))
	screen.refresh()

def write_record(board,gc_eva_score,gameScore):
	f=open('record.txt','a')
	for row in enumerate(board):
		f.write('{} \n'.format(str(row[1])))
	f.write('gc_eva_score = {}, gameScore = {} \n'.format(gc_eva_score,gameScore))
	f.close()

def gc_draw_record_Board(board,screen,gc_ev_a_score,gameScore):
	write_record(board,gc_eva_score,gameScore)
	for row in enumerate(board):
		for item in enumerate(row[1]):
			screen.addstr(8+3*row[0], 40+6*item[0], str(item[1]), curses.color_pair(COLORS[item[1]]))
	screen.refresh()

def copyBoard(board):
	newBoard = makeGame().board
	for row in enumerate(board):
		for item in enumerate(row[1]):
			newBoard[row[0]][item[0]] = item[1]
	return newBoard

def runRandom(board, firstMove):   
## old stratedy is: first setted, try continue steps many times to determine which first is better
	"""
	Returns the end score of a given board played randomly after moving in a given direction.
	"""
	randomGame = makeGame()					#make a new game
	moveList = randomGame.moveList
	randomGame.board = copyBoard(board) 	#copy the given board to the new game
	randomGame.makeMove(firstMove) 			#send the initial move

	while True:								#keep sending random moves until game is over
		if randomGame.gameOver():
			break
		randMove = random.choice(moveList)
		randomGame.makeMove(randMove)

	return randomGame.score

def gc_runRandom(board, firstMove):
	"""
	Returns the end score of a given board played randomly after moving in a given direction.
	"""
	randomGame = makeGame()					#make a new game
	moveList = randomGame.moveList
	randomGame.board = copyBoard(board) 	#copy the given board to the new game
	randomGame.makeMove(firstMove) 			#send the initial move

	while True:								#keep sending random moves until game is over
		if randomGame.gameOver():
			break
		randMove = random.choice(['d','r','d','r','d','r','l','d','r','d','r','d','r','l','u'])  ## odds is 3:3:2:1

		randomGame.makeMove(randMove)   
	write_record(randomGame.board,gc_eva_score(randomGame.board),randomGame.Score)

	return (randomGame.score,gc_eva_score(randomGame.board))   ## two score returns

def gc_score_direct_run(board, firstMove, maxDepth):   
	dGame = makeGame()					#make a new game
	moveList = ['d','r','l']
	best_gc_score = -99
	new_score = 0
	dGame.board = copyBoard(board) 	
	old_gc_score = gc_eva_score(board)
	dGame.makeMove(firstMove)
	#merged_score = 0
	#if dGame.mergedList:
		#for (i,j) in dGame.mergedList:
			#merged_score += dGame.board[i][j]*(i*i + j*j)
	first_board = dGame.board
	if dGame.gameOver() or first_board == board:
		return (-1,-100)
	#for _a in moveList:
	#for _a in up_movable(first_board)[1]:
	for _a in ['d','r','l','u']:
		dGame.board = first_board
		dGame.makeMove(_a)
		after_a_board = dGame.board
		if dGame.gameOver() or (after_a_board == first_board):
			continue
		for _b in moveList:
			dGame.board = after_a_board 
			dGame.makeMove(_b)
			after_b_board = dGame.board
			if dGame.gameOver() or (after_b_board == after_a_board):
				continue
			for _c in moveList:
				dGame.board = after_b_board 
				dGame.makeMove(_c)
				after_c_board = dGame.board
				if dGame.gameOver() or (after_c_board == after_b_board):
					continue
				for _d in moveList:
					dGame.board = after_c_board 
					dGame.makeMove(_d)
					after_d_board = dGame.board
					if dGame.gameOver() or (after_d_board == after_c_board):
						continue
					#else:
						#new_score = gc_eva_score(dGame.board)
						#best_gc_score += new_score
					for _e in moveList:
						dGame.board = after_d_board 
						dGame.makeMove(_e)
						after_e_board = dGame.board
						if dGame.gameOver() or (after_e_board == after_d_board):
							continue
						#else:
							#new_score = int(gc_eva_score(dGame.board)/100)
							#best_gc_score += new_score
						for _f in moveList:
							dGame.board = after_e_board 
							dGame.makeMove(_f)
							after_f_board = dGame.board
							if dGame.gameOver() or (after_e_board == after_d_board):
								continue
							#else:
								#new_score = gc_eva_score(dGame.board)
								#if new_score > best_gc_score:
									#best_gc_score = new_score
							for _g in moveList:
								dGame.board = after_f_board 
								dGame.makeMove(_g)
								after_g_board = dGame.board
								if dGame.gameOver() or (after_g_board == after_f_board):
									continue
								else:
									new_score = gc_eva_score(dGame.board)
									if new_score > best_gc_score:
										best_gc_score = new_score
								"""
								for _h in moveList:
									dGame.board = after_g_board 
									dGame.makeMove(_h)
									after_h_board = dGame.board
									if dGame.gameOver() or (after_h_board == after_g_board):
										continue
									else:
										new_score = gc_eva_score(dGame.board)
										if new_score > best_gc_score:
											best_gc_score = new_score
								"""								
				
	return (0,best_gc_score)   ## two score returns


def up_movable(x):  #x is board, if fist line last two member exist, then up_movable is set True.
	#movable = False
	for i in range(3):
		if x[i][1]==0 or x[i][2]==0 or x[i][3]==0 or x[i][1]==x[i+1][1] or x[i][2]==x[i+1][2] or x[i][3]==x[i+1][3]:
			return (False,['d','r','l'])
	return (True,['d','r','l','u'])


def gc_eva_score(x):  #x is board ## right,down move is same, no difference. should apply this symmetry in scoring.
	order_scores = 0
	repeat_scores = 0
	blank_scores = 0
	combined_scores = 0
	average_board_score = 0
	repair_right_score = 0
	if x[3][1] >= 512 and x[2][0] < x[3][0]:  ## change field  ## left corn in right order:
		field = [[1, 1, 0, 0], [9, 4, 1, 0], [12, 7, 5, 3], [60, 70, 80, 100]] 
		b_fld_ = [[1,1,2,2],[1,1,1,2],[-1,1,1,1],[1,1,-1,-2]]
		#if x[3][0]>= x[2][0] + x[2][1] + x[2][2] + x[2][3]
		if x[2][1] > x[2][0]: # and x[1][0] > x[2][0]:
			repair_right_score += (get_zhishu_dict[x[2][1]] - get_zhishu_dict[x[2][0]])*10*x[2][1]
	else:
		field = [[0, 0, 1, 1], [0, 1, 4, 9], [3, 5, 7, 12], [60, 70, 80, 100]] 
		b_fld_ = [[2,2,1,1],[2,1,1,1],[1,1,1,-1],[1,1,-1,-2]]
		if x[2][2] > x[2][3] and x[1][3] > x[2][3]:
			repair_right_score += (get_zhishu_dict[x[2][3]] + get_zhishu_dict[x[1][3]] - get_zhishu_dict[x[2][2]])*4*x[2][2]

	#for i in range(3,-1,-1):  # value is: 3,2,1
		#for j in range(3,-1,-1):
			#average_board_score += x[i][j]
	#average_board_score = int(average_board_score/16)
	average_board_score = average_dict[x[3][3]]
	for i in range(3,-1,-1):  # value is: 3,2,1
		for j in range(3,-1,-1):
			order_scores += x[i][j]*field[i][j]
                                 
			if x[i][j] == 0:                    ## replation forces  
				blank_scores += int(average_board_score)*2*b_fld_[i][j]
		if i>2 and x[i][j] != 0:
			for j1 in range(4):
				if x[i][j] == x[i-1][j1]:    
	## i.e.  compare above row
					#repeat_scores += x[i][j]*(field[i-1][j1])*abs(j-j1)     ## apply heavy punished
					if j != j1:
						repeat_scores += x[i][j]*20 
	"""
	if x[3][1]>=512 and x[3][0] <= 128 and x[3][0] > x[3][1]:
		
			repeat_scores += (150-x[3][0])*20   ## add 150, and substract x[3][0] which added before, so total is 150
		                                      ## that is mean FIX x[3][0], use 150 power to drag down same number.
			order_scores = (64 + 10*get_zhishu_dict[x[3][0]])*60 - x[3][0]*60
	"""		

		#if x[1][2] > x[1][3]:
			#repair_right_score += int((get_zhishu_dict[x[1][2]]-get_zhishu_dict[x[1][3]])*average_board_score/4)
		#else:   ## i.e.  x[1][2] <= x[1][3]:
			#repair_right_score += int((get_zhishu_dict[x[2][2]]-get_zhishu_dict[x[1][3]])*average_board_score/4) 
	#if x[3][2] > x[3][3]:
		#repair_right_score += int((get_zhishu_dict[x[3][2]]-get_zhishu_dict[x[3][3]])*average_board_score/4)

	combined_scores = order_scores - repeat_scores + blank_scores - repair_right_score
	return combined_scores


def bestMove(game, runs):
	"""
	Returns the best move for a given board.
	Plays "runs" number of games for each possible move and calculates which move had best avg end score.
	"""
	average = 0
	bestScore = 0
	moveList = game.moveList

	for moveDir in moveList:
		average = 0
		for x in range(runs):   ## runs many times, get average
			result = runRandom(game.board, moveDir)
			average += result
		average = average/runs
		if average >= bestScore:
			bestScore = average
			move = moveDir
	return move

def gc_bestMove(game, runs): ## this is virtully running for searching
	"""
	Returns the best move for a given board.
	Plays "runs" number of games for each possible move and calculates which move had best avg end score.
	"""
	gc_average = 0
	old_gc_eva_score = gc_eva_score(game.board)
	gc_bestScore = -99
	#moveList = ['d','r','l']
	moveList = ['d','r','l','u']
	#moveList = up_movable(game.board)[1]
	wrong_move_sign = 1
	move ='u'
	
	for moveDir in moveList:
		gc_average = 0
		maxDepth = 7
		for x in range(runs):
			result = gc_score_direct_run(game.board, moveDir, maxDepth)
			#average += result[0]
			gc_average += result[1]
			"""
			if result[1] <= 0:
				wrong_move_sign += 1
			if wrong_move_sign >10 and x>30 and (x/wrong_move_sign) < 2.5:  
			## control un-necessary runs, to break it early if found at 12 times
				break
			"""
		#average = average/(x+1)             ## here not runs,but x+1 because of break
		gc_average = gc_average/(x+1)
		if gc_average > gc_bestScore:  ### gc_average dominate the scoring funcation
			#bestScore = average
			gc_bestScore = gc_average
			move = moveDir
	return move

def solveGame(runs, screen):
	"""
	AI that plays a game till the end given a number of runs to make per move

	"""
	mainGame = makeGame()
	moveList = mainGame.moveList
	isDynamic = False

	#If runs is set to dynamic, increase the number of runs as score increases
	if runs == 'Dynamic':
		isDynamic = True

	while True:
		if mainGame.gameOver():
			break

		if isDynamic:
			#runs = int(1 + (0.01)*mainGame.score)
			runs = runs_power_dict[len(mainGame.spots)]
		if runs > 0:
			move = bestMove(mainGame, runs)
		else:
			move = random.choice(moveList)
			
		mainGame.makeMove(move)
		screen.clear()
		drawBoard(mainGame.board, screen)

	return(mainGame)


def gc_solveGame(runs, screen):
	"""
	improved scoring function not as total scores,but according the ordering and number repeaty

	"""
	mainGame = makeGame()
	mainGame.board = [[0,0,0,2,],[0,0,0,2,],[0,0,0,0,],[2,8,2048,4096]]
	moveList = mainGame.moveList
	isDynamic = False

	#If runs is set to dynamic, increase the number of runs as score increases
	if runs == 'Dynamic':
		isDynamic = True

	while True:
		if mainGame.gameOver():
			break

		if isDynamic:
			#runs = 1+int(0.003*mainGame.score)
			runs = runs_power_dict[len(mainGame.spots)]+int(0.002*mainGame.score)+10
		if runs > 0:
			move = gc_bestMove(mainGame,runs)
		else:
			move = gc_random.choice(moveList)
			
		mainGame.must_makeMove(move)
		screen.clear()
		gc_draw_record_Board(mainGame.board, screen,gc_eva_score(mainGame.board),mainGame.score)
	return(mainGame)
