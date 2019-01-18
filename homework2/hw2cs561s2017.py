
import random as rnd
import copy as cpy

############################################################################################
###  DPLL Algorithm  #######################################################################
############################################################################################

def Add_set_to_list_of_sets (list_of_sets,set):

    if set not in list_of_sets:
        list_of_sets.append(set)


def Constraints_as_clause(X,Y, M, N, relationships):

    sentences_list =[]

    for m in xrange(M):
        temp_clause = []
        for n in xrange(N):
            temp_clause.append(X[m][n])
            for k in range(n + 1, N):
                Add_set_to_list_of_sets(sentences_list, set([Y[m][n], Y[m][k]]))

        Add_set_to_list_of_sets(sentences_list, set(temp_clause))

    for i in xrange(len(relationships)):
        temp_relation = relationships[i]
        user_index_1 = temp_relation[0] - 1
        user_index_2 = temp_relation[1] - 1
        if temp_relation[2] == "F":
            for n in xrange(N):
                Add_set_to_list_of_sets(sentences_list, set([Y[user_index_1][n], X[user_index_2][n]]))

                Add_set_to_list_of_sets(sentences_list, set([X[user_index_1][n], Y[user_index_2][n]]))
        else:
            for n in xrange(N):
                Add_set_to_list_of_sets(sentences_list, set([Y[user_index_1][n], Y[user_index_2][n]]))

    return sentences_list


def Negate_of_symbol (symbol):

    temp_literal = symbol.split("_")

    if temp_literal[0] == "X":
        temp_literal[0] = "Y"
    else:
        temp_literal[0] = "X"

    negate_literal = "_".join(temp_literal)
    return negate_literal


def All_clauses_are_true (clauses):

    if len(clauses) == 0:
        return True
    else:
        return False

def Any_clause_is_false (clauses):

    if set([]) in clauses:
        return True
    else:
        return False

def Remove_list_of_clauses_from_list (clauses,removable_list):

    for removable in removable_list:
        if removable in clauses:
            clauses.remove(removable)


def Add_list_of_clauses_to_list(clauses, new_clauses):

    for new_clause in new_clauses:
        if new_clause not in clauses:
            clauses.append(new_clause)

def Apply_model_to_clauses (clauses,symbols,model):

    new_clauses = cpy.deepcopy(clauses)

    for symbol in model:
        clauses_to_be_removed =[]
        clauses_to_be_added =[]
        for clause in new_clauses:
            if symbol in clause:
                clauses_to_be_removed.append(clause)

            elif Negate_of_symbol(symbol) in clause:
                clauses_to_be_removed.append(clause)
                clause.remove(Negate_of_symbol(symbol))
                clauses_to_be_added.append(clause)

        Remove_list_of_clauses_from_list(new_clauses,clauses_to_be_removed)
        Add_list_of_clauses_to_list(new_clauses,clauses_to_be_added)

    return new_clauses


def Find_pure_symbol (clauses,symbols):

    for symbol in symbols:
        flag = 1

        for clause in clauses:
            if Negate_of_symbol(symbol) in clause:
                flag = 0
                break

        if flag == 1:
            return symbol
    return False


def Find_unit_clause (clauses,symbols):

    for clause in clauses:
        if len(clause) ==1:
            temp_list = list(clause)
            if temp_list[0] in symbols:
                return temp_list[0]

    return False



def DPLL(clauses,symbols,model):

    resultant_clauses = Apply_model_to_clauses(clauses,symbols,model)

    if All_clauses_are_true(resultant_clauses) == True:
        return True

    if Any_clause_is_false(resultant_clauses) == True:
        return False

    P = Find_pure_symbol(resultant_clauses,symbols)
    if P != False:
        new_symbols = cpy.deepcopy(symbols)
        Remove_list_of_clauses_from_list(new_symbols,[P,Negate_of_symbol(P)])
        model.append(P)
        return DPLL(resultant_clauses,new_symbols,model)

    P = Find_unit_clause(resultant_clauses,symbols)
    if P != False:
        new_symbols = cpy.deepcopy(symbols)
        Remove_list_of_clauses_from_list(new_symbols, [P, Negate_of_symbol(P)])
        model.append(P)
        return DPLL(resultant_clauses, new_symbols, model)

    P = symbols[0]
    rest = cpy.deepcopy(symbols)
    Remove_list_of_clauses_from_list(rest, [P, Negate_of_symbol(P)])

    model_1 = cpy.deepcopy(model)
    model_0 = cpy.deepcopy(model)

    model_1.append(P)
    model_0.append(Negate_of_symbol(P))
    return DPLL(resultant_clauses, rest, model_1) or DPLL(resultant_clauses, rest, model_0)



############################################################################################
###  WalkSAT Algorithm  ####################################################################
############################################################################################


def Random_model(M,N):
    x = [[0] * N    for i in xrange(M)]
    for m in xrange(M):
        for n in xrange(N):
            x[m][n]= rnd.randint(0,1)

    return x

def Select_random_clause (clauses):

    index = rnd.randint(0,len(clauses)-1)
    return clauses[index]

def Select_random_literal (clause):

    clause_list = list(clause)
    index = rnd.randint(0,len(clause_list)-1)
    return clause_list[index]

def Flip_value (x,literal):


    temp_literal = literal.split("_")

    [m, n] = map(lambda a: int(a), temp_literal[1:3])

    x[m][n] = 1- x[m][n]



def Find_unsatisfied_clauses(clauses,x):

    unsatisfied_clauses =[]

    for clause in clauses:
        flag = 0

        for literal in clause:

            temp_literal = literal.split("_")

            [m,n] = map(lambda a: int(a),temp_literal[1:3])

            if temp_literal[0] == "X":
                if x[m][n] == 1:
                    flag = 1
                    break
            else:
                if x[m][n] == 0:
                    flag = 1
                    break


        if flag == 0:
            unsatisfied_clauses.append(clause)

    return unsatisfied_clauses


def Find_min_index_of_list (my_list):
    index =0
    value = my_list[0]
    for i in range(1,len(my_list)):
        if my_list[i] < value:
            value =my_list[i]
            index =i

    return index



def Find_maximizer (clause,x,all_clauses):
    clause_list = list(clause)
    values_list = [0]*len(clause_list)

    for i in xrange(len(clause_list)):
        temp_x = cpy.deepcopy(x)
        Flip_value(temp_x, clause_list[i])

        values_list[i] = len(Find_unsatisfied_clauses(all_clauses,temp_x))

    maximizer_index = Find_min_index_of_list(values_list)

    return clause_list[maximizer_index]





def WalkSAT(clauses,p,max_flips,M,N):

    model = Random_model(M,N)

    while True:

        unsatisfied_clauses = Find_unsatisfied_clauses(clauses,model)

        if unsatisfied_clauses ==[]:
            return model

        clause = Select_random_clause(unsatisfied_clauses)

        my_random = rnd.random()

        if my_random <= p:
            literal = Select_random_literal(clause)
            Flip_value(model,literal)

        else:
            literal = Find_maximizer (clause,model,clauses)
            Flip_value(model, literal)

    return model


def Find_a_solution(model,M,N):

    assignments =[0]*M

    for m in xrange(M):
        for n in xrange(N):
            if model[m][n] ==1:
                assignments[m] = n+1

    return assignments


def Printable_output(solution, str):

    for i in xrange(len(solution)):
        str.append("{g} {t}".format(g= i+1,t = solution[i]))


############################################################################################
############################################################################################
############################################################################################


f_input = open("input3.txt")

#M =  number of guests,  N = number of tables
[M,N] = map(lambda i: int(i), f_input.readline().strip().split())

relationships =[]
while True:
    line = f_input.readline().strip()
    if len(line) > 0:
        relationships.append(list(line.split(" ")))
    else:
        break

for i in xrange(len(relationships)):
    relationships[i][0] = int(relationships[i][0])
    relationships[i][1] = int(relationships[i][1])

#Boolean variables Xmn represents whether each guest m will be seated at a specific table n.
#The negation of Xmn is defined as Ymn


X = []
Y = []
symbols = []

for m in xrange(M):
    temp_list_X = []
    temp_list_Y = []
    for n in xrange(N):
        temp_list_X.append("X_{g}_{t}".format(g=m,t=n))
        temp_list_Y.append("Y_{g}_{t}".format(g=m,t=n))

        symbols.append("X_{g}_{t}".format(g=m,t=n))
        symbols.append("Y_{g}_{t}".format(g=m,t=n))

    X.append(temp_list_X)
    Y.append(temp_list_Y)

#Writes constraints as list of clauses
list_of_clauses = Constraints_as_clause(X,Y, M, N, relationships)

print len(list_of_clauses)

if DPLL (list_of_clauses,symbols,[]) == True:
    satisfiable = "yes"
else:
    satisfiable = "no"

file = open("output.txt","w")

if satisfiable == "no":
    file.write(satisfiable)
else:
    x = WalkSAT(list_of_clauses, 0.5, 1, M, N)
    y = Find_a_solution(x,M,N)

    output_string = []
    Printable_output(y,output_string)

    log_output = "\n".join(output_string)

    file.write(satisfiable + "\n" + log_output)