import numpy as np


def FindTurn(player):
    if player =="X":
        return 1
    else:
        return -1

def MapToInfinity(number):
    if number == float("inf"):
        return "Infinity"
    elif number == -float("inf"):
        return "-Infinity"
    else:
        return number

def BoardToNumbers(board):
    state = np.array([[0]*8]*8)
    for i in xrange(8):
        for j in xrange(8):
            if board[i][j] =="*":
                state[i][j]= 0
            elif board[i][j] =="X":
                state[i][j] = 1
            else:
                state[i][j] = -1
    return state

def NumbersToBoard(state):
    board =""
    for i in xrange(8):
        for j in xrange(8):
            if state[i,j]== 1:
                board += "X"
            elif state[i,j] ==0:
                board += "*"
            else:
                board += "O"
        if i != 7:
            board += "\n"
    return board

def PositionNumToName(index):
    columns = ["a","b","c","d","e","f","g","h"]
    rows = ["1","2","3","4","5","6","7","8"]

    name = "".join([columns[index[1]],rows[index[0]]])
    return name

def FindNeighbours(index):
    r_index = index[0]
    c_index = index[1]

    neighbours = [[r_index-1,c_index -1], [r_index-1,c_index], [r_index-1,c_index+1],[r_index,c_index-1],[r_index,c_index+1],
                  [r_index + 1, c_index - 1], [r_index + 1, c_index], [r_index + 1, c_index + 1]]

    valid_neighbours =[]
    for n in neighbours:
        if n[0] in range(0,8) and n[1] in range(0,8):
            valid_neighbours.append(n)
    return valid_neighbours

def IsValidMove(state, index_1, index_2,turn): # this function checks whether index_2 position is valid for player turn

    [i,j] = index_1
    [m,n] = index_2

    if state[i,j] ==turn:
        return False

    if state[m,n] ==1 or state[m,n] ==-1:
        return False
    else:
        l = i + (i-m)
        k = j + (j-n)
        if l not in xrange(8) or k not in xrange(8):
            return False
        elif state[l,k]==0:
            return False
        elif state[l,k] == turn:
            return True
        else:
            while l in xrange(8) and k in xrange(8):
                [m, n] = [i, j]
                [i,j] =[l,k]

                l = i + (i - m)
                k = j + (j - n)

                if l not in xrange(8) or k not in xrange(8):
                    return False
                if state[l, k] == turn:
                    return True
            return False




def BoardUpdate (state,action, turn):


    updated_state = np.copy(state)

    if action=="pass":
        return updated_state
    else:

        [m, n] = action
        updated_state[m, n] = turn

        for neighbour in FindNeighbours([m, n]):

            m_temp = m
            n_temp = n

            reversible = []
            [l, k] = neighbour

            while state[l, k] == -turn:
                reversible.append([l, k])
                i = l + (l - m_temp)
                j = k + (k - n_temp)

                [m_temp, n_temp] = [l, k]
                [l, k] = [i, j]


                if l not in xrange(8) or k not in xrange(8):
                    break

            if l in xrange(8) and k in xrange(8):
                if state[l, k] == turn:
                    for index in reversible:
                        updated_state[index[0], index[1]] = turn

        return updated_state


def FindWeight(position):
    weights_2d = []
    weights_2d.append([99, -8, 8, 6, 6, 8, -8, 99])
    weights_2d.append([-8, -24, -4, -3, -3, -4, -24, -8])
    weights_2d.append([8, -4, 7, 4, 4, 7, -4, 8])
    weights_2d.append([6, -3, 4, 0, 0, 4, -3, 6])
    weights_2d.append([6, -3, 4, 0, 0, 4, -3, 6])
    weights_2d.append([8, -4, 7, 4, 4, 7, -4, 8])
    weights_2d.append([-8, -24, -4, -3, -3, -4, -24, -8])
    weights_2d.append([99, -8, 8, 6, 6, 8, -8, 99])

    weights = np.array(weights_2d)

    return weights[position[0],position[1]]

def FindUtility(state,turn):
    utility = 0 # utility of X player with index 1

    for i in xrange(8):
        for j in xrange(8):
            utility += state[i,j]*FindWeight([i,j])

    return utility*turn



def FindValidMoves(state, turn):
    valid_moves = []

    for i in xrange(8):
        for j in xrange(8):
            if state[i, j] == -turn:
                neighbours = FindNeighbours([i, j])
                for neighbour in neighbours:
                    if IsValidMove(state, [i, j], [neighbour[0], neighbour[1]], turn) == True:
                        if neighbour not in valid_moves:
                            valid_moves.append(neighbour)
    valid_moves = sorted(valid_moves, key=lambda x: (x[0], x[1]))
    return valid_moves


def IsTerminal (state, node_action, max_depth,current_depth,flag):
    if max_depth == current_depth or flag==1:
        return True
    else:
        return False


def MaxValueAction (state, node_action, max_depth,current_depth, alpha, beta,str,flag,player_turn):

    if IsTerminal (state, node_action,max_depth,current_depth,flag) == True:


        utility = FindUtility(state,player_turn)
        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action,
                                                             Depth=current_depth, Value=MapToInfinity(utility), Alpha=MapToInfinity(alpha),
                                                             Beta=MapToInfinity(beta))
                   )


        return [utility,0]

    a = 0
    v = -float("inf")

    str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                         Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                             Beta=MapToInfinity(beta))
               )

    for action in FindValidMoves(state,player_turn):
        [v_temp, a_temp] = MinValueAction (BoardUpdate(state,action,player_turn),PositionNumToName(action), max_depth,current_depth+1,alpha,beta,str,0,player_turn)

        if v_temp > v:
            v = max(v,v_temp)
            a = action
        if v >= beta:

            str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                 Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                                 Beta=MapToInfinity(beta))
                       )

            return [v,0]
        alpha = max(v,alpha)

        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                             Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                             Beta=MapToInfinity(beta))
                   )

    if FindValidMoves(state,player_turn)==[]:

        a = "pass"

        if node_action =="pass":
            [v_temp, a_temp] = MinValueAction(state, "pass", max_depth,
                                              current_depth + 1, alpha, beta, str,1,player_turn)
        else:
            [v_temp, a_temp] = MinValueAction(state, "pass", max_depth,
                                          current_depth + 1, alpha, beta, str,0,player_turn)
        if v_temp > v:
            v = max(v, v_temp)

        if v >= beta:
            str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                      Value=MapToInfinity(v),
                                                                      Alpha=MapToInfinity(alpha),
                                                                      Beta=MapToInfinity(beta))
                       )

            return [v, 0]

        alpha = max(v, alpha)
        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                  Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                                  Beta=MapToInfinity(beta))
                   )


    return [v,a]

def MinValueAction (state, node_action, max_depth,current_depth, alpha, beta,str,flag,player_turn):
    if IsTerminal(state, node_action, max_depth, current_depth,flag) == True:

        utility = FindUtility(state,player_turn)
        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action,
                                                             Depth=current_depth, Value=MapToInfinity(utility), Alpha=MapToInfinity(alpha),
                                                             Beta=MapToInfinity(beta))
                   )


        return [utility, 0]

    a= 0
    v = float("inf")

    str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                         Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                         Beta=MapToInfinity(beta))
               )



    for action in FindValidMoves(state,-player_turn):

        [v_temp, a_temp] = MaxValueAction (BoardUpdate(state,action,-player_turn),PositionNumToName(action), max_depth,current_depth+1,alpha,beta,str,0,player_turn)

        if v_temp < v:
            v = min(v, v_temp)
            a = action

        if v <= alpha:
            str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                 Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                                 Beta=MapToInfinity(beta))
                       )


            return [v,0]
        beta = min(v,beta)

        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                             Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                             Beta=MapToInfinity(beta))
                  )


    if FindValidMoves(state, -player_turn) == []:

        a = "pass"

        if node_action == "pass":
            [v_temp, a_temp] = MaxValueAction(state, "pass", max_depth,
                                              current_depth + 1, alpha, beta, str, 1,player_turn)
        else:
            [v_temp, a_temp] = MaxValueAction(state, "pass", max_depth,
                                              current_depth + 1, alpha, beta, str, 0,player_turn)
        if v_temp < v:
            v = min(v, v_temp)

        if v <= alpha:
            str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                      Value=MapToInfinity(v),
                                                                      Alpha=MapToInfinity(alpha),
                                                                      Beta=MapToInfinity(beta))
                       )

            return [v, a]

        beta = min(v, beta)

        str.append("{Node},{Depth},{Value},{Alpha},{Beta}".format(Node=node_action, Depth=current_depth,
                                                                  Value=MapToInfinity(v), Alpha=MapToInfinity(alpha),
                                                                  Beta=MapToInfinity(beta))
                   )

    return [v,a]



f_input = open("input1.txt")

player = f_input.readline().strip()
max_depth = int(f_input.readline().strip())

board =[]
for i in range(0,8):
    board.append(list(f_input.readline().strip()))


player_turn = FindTurn(player)

state = BoardToNumbers(board)

output_string =[]
output_string.append("Node,Depth,Value,Alpha,Beta")

[u,action] = MaxValueAction(state,"root",max_depth,0, -float("inf"),float("inf"),output_string,0,player_turn)


board_output = NumbersToBoard(BoardUpdate(state,action,player_turn))

log_output = "\n".join(output_string)

file = open("output.txt","w")

file.write(board_output + "\n" + log_output)











