import numpy as npy
import copy as cpy
import itertools as itert
import re


def True_to_Binary(s):
    if s == "+":
        return 1
    else:
        return 0


def Binary_to_True(s):
    if s == 1:
        return "+"
    else:
        return "-"

def Parse_Experission(query):
    type = query[0]
    query_variables =[[],[]]
    query_values ={}

    if type == "P":
        query = query[1:]
    elif type == "E":
        query = query[2:]
    else:
        query = query[3:]


    line = re.sub('[ ()]', '', query)
    if "|" in line:
        [query_vars, observation_var] = line.split("|")
        query_vars = query_vars.split(",")
        observation_var = observation_var.split(",")
    else:
        query_vars = line.split(",")
        observation_var =[]


    temp_query_variables =[]
    for term in query_vars:
        temp_query_variables.append(term.split("="))

    temp_observation_variables =[]
    for term in observation_var:
        temp_observation_variables.append(term.split("="))

    for symbol in temp_query_variables:
        if symbol[0] not in query_variables[0]:
            query_variables[0].append(symbol[0])
        if symbol[0] not in query_values.keys() and len(symbol)>1:
            query_values[symbol[0]] = True_to_Binary(symbol[1])

    for symbol in temp_observation_variables:
        if symbol[0] not in query_variables[1]:
            query_variables[1].append(symbol[0])
        if symbol[0] not in query_values.keys():
            query_values[symbol[0]] = True_to_Binary(symbol[1])

    return [type,query_variables,query_values]


def Pointwise_Multiplication (factor_1,factor_2):

    f1_Variables = factor_1[0]
    f1_Probabilities = factor_1[1]

    f2_Variables = factor_2[0]
    f2_Probabilities = factor_2[1]

    Vars_list = [] # Union of f1_Variables and f2_Variables
    Vars_Position ={}

    index = 0
    for var in f1_Variables + f2_Variables:
        if var not in Vars_list:
            Vars_list.append(var)
            Vars_Position[var] = index

            index +=1

    size_maker = [2] * len(Vars_list)

    resultant_distribution = npy.zeros(shape=size_maker)


    iterations = [list(p) for p in itert.product(range(2),repeat= len(Vars_list))]

    for realization in iterations:

        f1_realization =[]
        f2_realization =[]

        for var_1 in f1_Variables:
            f1_realization.append(realization[Vars_Position[var_1]])

        for var_2 in f2_Variables:
            f2_realization.append(realization[Vars_Position[var_2]])


        resultant_distribution[tuple(realization)] = f1_Probabilities[tuple(f1_realization)] * f2_Probabilities[tuple(f2_realization)]


    resultant_factor = [Vars_list,resultant_distribution]

    return resultant_factor


def Factors_Multiplication(factors):

    iteration = 0

    result_factor = factors[0]

    if len(factors) == 1:
        return result_factor
    else:
        while iteration < len(factors[1:]):
            result_factor = Pointwise_Multiplication(result_factor,factors[iteration +1])

            iteration +=1

        return result_factor

def Remove_from_list (my_list, var):

    output_list =[]

    for variable in my_list:
        if variable != var:
            output_list.append(variable)

    return output_list

def Put_at_list (my_list,item,index):

    output_list = my_list[0:index]
    output_list.append(item)
    output_list = output_list + my_list[index:]

    return output_list


def Sum_Out(var, factors):


    relevant_factors =[]

    resultant_factors = cpy.deepcopy(factors)

    for factor in resultant_factors:
        if var in factor[0]:
            relevant_factors.append(factor)



    for any_factor in relevant_factors:
        resultant_factors.remove(any_factor)


    multuplied_factor = Factors_Multiplication(relevant_factors)

    summed_factor = [[],[]]

    summed_factor[0] = Remove_from_list(multuplied_factor[0], var)

    size_maker = [2] * len(summed_factor[0])

    summed_factor[1] = npy.zeros(shape=size_maker)

    iterations = [list(p) for p in itert.product(range(2), repeat=len(summed_factor[0]))]

    index_of_removed_var = multuplied_factor[0].index(var)

    for iter in iterations:

        new_iter_0 = Put_at_list(iter, 0, index_of_removed_var)
        new_iter_1 = Put_at_list(iter, 1, index_of_removed_var)

        summed_factor[1][tuple(iter)] = multuplied_factor[1][tuple(new_iter_0)] + multuplied_factor[1][tuple(new_iter_1)]


    resultant_factors.append(summed_factor)

    return resultant_factors


def Find_Relevant_Vars (query_variables, observations_variables,variables_parent_dict,nodes):

    relevant_variables = cpy.deepcopy(query_variables)

    for var in observations_variables:
        if var not in relevant_variables and var in nodes:
            relevant_variables.append(var)

    temp_list =cpy.deepcopy(observations_variables)

    for var in query_variables:
        if var not in temp_list:
            temp_list.append(var)

    added_ancestors = []

    while temp_list != []:

        temp_node = temp_list[0]
        temp_list.remove(temp_node)


        for ancestor in variables_parent_dict[temp_node]:
            if ancestor not in relevant_variables and ancestor in nodes:
                relevant_variables.append(ancestor)
            if ancestor not in added_ancestors:
                added_ancestors.append(ancestor)
                temp_list.append(ancestor)

    relevant_variables.sort(key=nodes.index)

    return relevant_variables


def Make_factor(var,parents,prob_matrix, observations):

    factor_variables = []
    observed_parents =[]


    if var not in observations:
        factor_variables.append(var)
        flag = 1
    else:
        flag = 0
        var_realized = observations[var]


    for parent in parents:
        if parent not in observations:
            factor_variables.append(parent)
        else:
            observed_parents.append(parent)


    size_maker = [2] * len(factor_variables)

    factor_distribution = npy.zeros(shape=size_maker)

    iterations = [list(p) for p in itert.product(range(2), repeat=len(factor_variables))]


    if parents ==[]:

        if flag ==0:
            return []
        else:
            factor_distribution = npy.asarray([1-prob_matrix,prob_matrix])

            return [factor_variables,factor_distribution]


    if flag == 0:

        for iteration in iterations:

            new_iteration = iteration
            for parent in observed_parents:
                new_iteration = Put_at_list(new_iteration, observations[parent], parents.index(parent))

            factor_distribution[tuple(iteration)] = var_realized*prob_matrix[tuple(new_iteration)] + (1-var_realized)*(1- prob_matrix[tuple(new_iteration)])

    if flag ==1:

        for iteration in iterations:

            new_iteration = iteration[1:]
            for parent in observed_parents:
                new_iteration = Put_at_list(new_iteration, observations[parent], parents.index(parent))

            factor_distribution[tuple(iteration)] = iteration[0]* prob_matrix[tuple(new_iteration)] + (
                                                                                                       1 - iteration[0]) * (
                                                                                                       1 - prob_matrix[
                                                                                                           tuple(
                                                                                                               new_iteration)])

    return [factor_variables,factor_distribution]


def Normalize(factor):

    sum = factor[1].sum()

    return [factor[0],factor[1]/float(sum)]


def Elimination_Ask(query_variables,observations,variables_parent_dict, variables_prob_dict,nodes):

    relevant_vars = Find_Relevant_Vars (query_variables,observations.keys(),variables_parent_dict,nodes)

    ordered_vars = relevant_vars[::-1]

    factors =[]

    for var in ordered_vars:

        new_factor = Make_factor(var,variables_parent_dict[var],variables_prob_dict[var],observations)

        if new_factor !=[]:
            factors.append(new_factor)

        if var not in observations and var not in query_variables:
            factors = Sum_Out(var,factors)


    return Normalize(Factors_Multiplication(factors))



def Delete_list_from_dic(my_dict, mylist):

    output_dict = cpy.deepcopy(my_dict)

    for item in mylist:
        del output_dict[item]

    return output_dict

def Calculate_Expected_Value(observations,variables_parent_dict, variables_prob_dict,nodes,utility_mat):

    utility_node = "utility"
    utility_matrix = utility_mat
    utility_node_parents = variables_parent_dict[utility_node]

    observed_values = cpy.deepcopy(observations)

    variable_parents =[]
    observed_parents =[]
    for var in utility_node_parents:
        if var in nodes and var not in observed_values.keys():
            variable_parents.append(var)
        else:
            observed_parents.append(var)


    iterations = [list(p) for p in itert.product(range(2), repeat=len(variable_parents))]

    expected_value = 0
    for realization in iterations:

        query_distribution = Elimination_Ask(variable_parents, observed_values, nodes_parent_dict, nodes_prob_dict, nodes)

        my_realization = []

        for var in query_distribution[0]:
            var_index = variable_parents.index(var)
            my_realization.append(realization[var_index])

        new_realization = []

        for parent in utility_node_parents:
            if parent in variable_parents:
                parent_index = variable_parents.index(parent)
                new_realization.append(realization[parent_index])
            else:
                new_realization.append(observed_values[parent])

        expected_value += query_distribution[1][tuple(my_realization)]*utility_matrix[tuple(new_realization)]

    return expected_value

#####################
#####################

f_input = open("input.txt")

queries =[]
while True:
    line_parsed = f_input.readline().strip()
    if line_parsed != "******" and len(line_parsed)>0:
        queries.append(line_parsed)
    else:
        break


index = 0
nodes = []
decisions =[]
utility_nodes = []
bn_Vars = []
nodes_parent_dict = {}
nodes_prob_dict ={}
utility_matrix =0

line_parsed = "******"
while True:
    line_parsed_old = line_parsed
    line_parsed = f_input.readline().strip()

    if line_parsed != "******" and len(line_parsed)>0:

        if line_parsed != "***":

            uncoded_line = line_parsed.split(" ")
            if line_parsed_old[0] == "*":


                node_name = uncoded_line[0]
                if node_name != "utility":
                    nodes.append(node_name)
                    bn_Vars.append(node_name)

                if len(uncoded_line) >1:
                    nodes_parent_dict[node_name] = uncoded_line[2:len(uncoded_line)]
                    size_maker = [2]*len(nodes_parent_dict[node_name])
                    node_list = npy.zeros(shape=size_maker)
                else:
                    nodes_parent_dict[node_name] =[]

            else:
                if len(uncoded_line) == 1:
                    if uncoded_line[0] == "decision":
                        nodes.remove(node_name)
                        decisions.append(node_name)
                    else:
                        nodes_prob_dict[node_name] = float(uncoded_line[0])
                else:
                    indexes = map(lambda i: True_to_Binary(i), uncoded_line[1:])
                    node_list[tuple(indexes)] = float(uncoded_line[0])
                    nodes_prob_dict[node_name] = node_list


    else:
        break


line_parsed = "******"
while True:
    line_parsed_old = line_parsed
    line_parsed = f_input.readline().strip()

    if len(line_parsed)>0:
        uncoded_line = line_parsed.split(" ")
        if line_parsed_old[0] == "*":

            node_name = uncoded_line[0]
            if node_name != "utility":
                nodes.append(node_name)
            else:
                utility_nodes.append(node_name)
                bn_Vars.append(node_name)

            if len(uncoded_line) > 1:
                nodes_parent_dict[node_name] = uncoded_line[2:len(uncoded_line)]
                size_maker = [2] * len(nodes_parent_dict[node_name])
                node_list = npy.zeros(shape=size_maker)
            else:
                nodes_parent_dict[node_name] = []

        else:
            if len(uncoded_line) == 1:
                utility_matrix = int(uncoded_line[0])
            else:
                indexes = map(lambda i: True_to_Binary(i), uncoded_line[1:])
                node_list[tuple(indexes)] = int(uncoded_line[0])
                utility_matrix = node_list

    else:
        break


file = open("output.txt","w")

for query in queries:

    [parsed_type, parsed_query_variables, parsed_query_values] = Parse_Experission(query)

    if parsed_type == "P":

        observed_values = Delete_list_from_dic(parsed_query_values, parsed_query_variables[0])

        query_distribution = Elimination_Ask(parsed_query_variables[0], observed_values, nodes_parent_dict,
                                             nodes_prob_dict, nodes)


        query_realization =[]
        for var in query_distribution[0]:
            query_realization.append(parsed_query_values[var])

        query_response = query_distribution[1][tuple(query_realization)]

        file.write("{:.2f}".format(round(query_response, 2))+ "\n")

    elif parsed_type == "E":

        query_response = Calculate_Expected_Value(parsed_query_values, nodes_parent_dict, nodes_prob_dict, nodes, utility_matrix)

        file.write(str(int(round(query_response))) + "\n")

    else:

        size_maker = [2] * len(parsed_query_variables[0])

        EU_matrix = npy.zeros(shape=size_maker)

        iterations = [list(p) for p in itert.product(range(2), repeat=len(parsed_query_variables[0]))]

        for iter in iterations:

            observed_values = cpy.deepcopy(parsed_query_values)

            for i in xrange(len(parsed_query_variables[0])):
                observed_values[parsed_query_variables[0][i]] = iter[i]

            EU_matrix[tuple(iter)] = Calculate_Expected_Value(observed_values, nodes_parent_dict, nodes_prob_dict, nodes,
                                                      utility_matrix)


        maximum_position = list(npy.unravel_index(EU_matrix.argmax(), EU_matrix.shape))

        query_response = []
        for position in maximum_position:
            query_response.append(Binary_to_True(position))

        query_response.append(str(int(round(EU_matrix.max()))))


        file.write(" ".join(query_response)+ "\n")
