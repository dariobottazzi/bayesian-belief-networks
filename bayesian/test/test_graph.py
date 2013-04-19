import pytest
from bayesian.factor_graph import *


def fA(x1):
    if x1.value == True:
        return 0.1
    elif x1.value == False:
        return 0.9

fA.domains = dict(x1=[True, False])

def fB(x2):
    if x2.value == True:
        return 0.3
    elif x2.value == False:
        return 0.7

fB.domains = dict(x2=[True, False])


def fC(x1, x2, x3):
    ''' 
    This needs to be a joint probability distribution
    over the inputs and the node itself
    '''
    table = dict()
    table['ttt'] = 0.05
    table['ttf'] = 0.95
    table['tft'] = 0.02
    table['tff'] = 0.98
    table['ftt'] = 0.03
    table['ftf'] = 0.97
    table['fft'] = 0.001
    table['fff'] = 0.999
    key = ''
    key = key + 't' if x1.value else key + 'f'
    key = key + 't' if x2.value else key + 'f'
    key = key + 't' if x3.value  else key + 'f'
    return table[key]

fC.domains = dict(
    x1=[True, False],
    x2=[True, False],
    x3=[True, False])

def fD(x3, x4):
    table = dict()
    table['tt'] = 0.9
    table['tf'] = 0.1
    table['ft'] = 0.2
    table['ff'] = 0.8
    key = ''
    key = key + 't' if x3.value else key + 'f'
    key = key + 't' if x4.value else key + 'f'
    return table[key]

fD.domains = dict(
    x3=[True, False],
    x4=[True, False])


def fE(x3, x5):
    table = dict()
    table['tt'] = 0.65
    table['tf'] = 0.35
    table['ft'] = 0.3
    table['ff'] = 0.7
    key = ''
    key = key + 't' if x3.value else key + 'f'
    key = key + 't' if x5.value else key + 'f'
    return table[key]

fE.domains = dict(
    x3=[True, False],
    x5=[True, False])


# Build the network

fA_node = FactorNode('fA', fA)
fB_node = FactorNode('fB', fB)
fC_node = FactorNode('fC', fC)
fD_node = FactorNode('fD', fD)
fE_node = FactorNode('fE', fE)

x1 = VariableNode('x1', parents=[fA_node])
x2 = VariableNode('x2', parents=[fB_node])
x3 = VariableNode('x3', parents=[fC_node])
x4 = VariableNode('x4', parents=[fD_node])
x5 = VariableNode('x5', parents=[fE_node])

# Now set the parents for the factor nodes...
fA_node.parents = []
fB_node.parents = []
fC_node.parents = [x1, x2]
fD_node.parents = [x3]
fE_node.parents = [x3]

# Now set children for Variable Nodes...
x1.children = [fC_node]
x2.children = [fC_node]
x3.children = [fD_node, fE_node]
x4.children = []
x5.children = []

# Now set the children for the factor nodes...
fA_node.children = [x1]
fB_node.children = [x2]
fC_node.children = [x3]
fD_node.children = [x4]
fE_node.children = [x5]

graph = FactorGraph([x1, x2, x3, x4, x5, fA_node, fB_node, fC_node, fD_node, fE_node])

def test_variable_node_is_leaf():
    assert not x1.is_leaf()
    assert not x2.is_leaf()
    assert not x3.is_leaf()
    assert x4.is_leaf()
    assert x5.is_leaf()


def test_factor_node_is_leaf():
    assert fA_node.is_leaf()
    assert fB_node.is_leaf()
    assert not fC_node.is_leaf()
    assert not fD_node.is_leaf()
    assert not fE_node.is_leaf()


def test_graph_get_leaves():
    assert graph.get_leaves() == [x4, x5, fA_node, fB_node]

# Tests at step 1
def test_graph_get_step_1_eligible_senders():
    eligible_senders = graph.get_eligible_senders()
    assert eligible_senders == [x4, x5, fA_node, fB_node]


def test_node_get_step_1_target():
    assert x1.get_target() is None
    assert x2.get_target() is None
    assert x3.get_target() is None
    assert x4.get_target() == fD_node
    assert x5.get_target() == fE_node
    assert fA_node.get_target() == x1
    assert fB_node.get_target() == x2
    assert fC_node.get_target() is None
    assert fD_node.get_target() is None
    assert fE_node.get_target() is None


def test_construct_message():
    message = x4.construct_message()
    assert message.source.name == 'x4'
    assert message.destination.name == 'fD'
    assert message.argspec == []
    assert message.factors == [1]
    message = x5.construct_message()
    assert message.source.name == 'x5'
    assert message.destination.name == 'fE'
    assert message.argspec == []
    assert message.factors == [1]
    message = fA_node.construct_message()
    assert message.source.name == 'fA'
    assert message.destination.name == 'x1'
    assert message.argspec == ['x1']
    assert message.factors == [fA_node.func]
    message = fB_node.construct_message()
    assert message.source.name == 'fB'
    assert message.destination.name == 'x2'
    assert message.argspec == ['x2']
    assert message.factors == [fB_node.func]


def test_send_message():
    message = x4.construct_message()
    x4.send(message)
    assert message.destination.received_messages['x4'] == message
    message = x5.construct_message()
    x5.send(message)
    assert message.destination.received_messages['x5'] == message
    message = fA_node.construct_message()
    fA_node.send(message)
    assert message.destination.received_messages['fA'] == message
    message = fB_node.construct_message()
    fB_node.send(message)
    assert message.destination.received_messages['fB'] == message


def test_sent_messages():
    sent = x4.get_sent_messages()
    assert sent['fD'] == fD_node.received_messages['x4']
    sent = x5.get_sent_messages()
    assert sent['fE'] == fE_node.received_messages['x5']
    sent = fA_node.get_sent_messages()
    assert sent['x1'] == x1.received_messages['fA']
    sent = fB_node.get_sent_messages()
    assert sent['x2'] == x2.received_messages['fB']

# Step 2
def test_node_get_step_2_target():
    assert x1.get_target() == fC_node
    assert x2.get_target() == fC_node


def test_graph_reset():
    graph.reset()
    for node in graph.nodes:
        assert node.received_messages == {}

def test_propagate():
    graph.reset()
    graph.propagate()
    for node in graph.nodes:
        node.message_report()

def marg(x, val, normalizer=1.0):
    return round(x.marginal(val, normalizer), 3)


def test_marginals():
    m = marg(x1, True)
    assert m == 0.1
    m = marg(x1, False)
    assert m == 0.9
    m = marg(x2, True)
    assert m == 0.3
    m = marg(x2, False)
    assert m == 0.7
    m = marg(x3, True)
    assert m == 0.012  # Note slight rounding difference to BAI
    m = marg(x3, False)
    assert m == 0.988
    m = marg(x4, True)
    assert m == 0.208
    m = marg(x4, False)
    assert m == 0.792
    m = marg(x5, True)
    assert m == 0.304
    m = marg(x5, False)
    assert m == 0.696

def test_add_evidence():
    ''' 
    We will set x5=True, this
    corresponds to variable D in BAI
    '''
    graph.reset()
    add_evidence(x5, True)
    graph.propagate()
    normalizer = marg(x5, True)
    assert normalizer == 0.304
    m = marg(x1, True, normalizer)
    assert m == 0.102
    m = marg(x1, False, normalizer)
    assert m == 0.898
    m = marg(x2, True, normalizer)
    assert m == 0.307
    m = marg(x2, False, normalizer)
    assert m == 0.693
    m = marg(x3, True, normalizer)
    assert m == 0.025
    m = marg(x3, False, normalizer)
    assert m == 0.975
    m = marg(x4, True, normalizer)
    assert m == 0.217
    m = marg(x4, False, normalizer)
    assert m == 0.783
    m = marg(x5, True, normalizer)
    assert m == 1.0
    m = marg(x5, False, normalizer)
    assert m == 0.0
    
def test_add_evidence_x2_true():
    '''
    x2 = S in BAI
    '''
    graph.reset()
    add_evidence(x2, True)
    graph.propagate()
    normalizer = marg(x2, True)
    m = marg(x1, True, normalizer)
    assert m == 0.1
    m = marg(x1, False, normalizer)
    assert m == 0.9
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 0.032
    m = marg(x3, False, normalizer)
    assert m == 0.968
    m = marg(x4, True, normalizer)
    assert m == 0.222
    m = marg(x4, False, normalizer)
    assert m == 0.778
    m = marg(x5, True, normalizer)
    assert m == 0.311
    m = marg(x5, False, normalizer)
    assert m == 0.689
    

def test_add_evidence_x3_true():
    '''
    x3 = True in BAI this is Cancer = True
    '''
    graph.reset()
    add_evidence(x3, True)
    graph.propagate()
    normalizer = x3.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.249
    m = marg(x1, False, normalizer)
    assert m == 0.751
    m = marg(x2, True, normalizer)
    assert m == 0.825
    m = marg(x2, False, normalizer)
    assert m == 0.175
    m = marg(x3, True, normalizer)
    assert m == 1.0
    m = marg(x3, False, normalizer)
    assert m == 0.0
    m = marg(x4, True, normalizer)
    assert m == 0.9
    m = marg(x4, False, normalizer)
    assert m == 0.1
    m = marg(x5, True, normalizer)
    assert m == 0.650
    m = marg(x5, False, normalizer)
    assert m == 0.350


def test_add_evidence_x2_true_and_x3_true():
    '''
    x2 = True in BAI this is Smoker = True
    x3 = True in BAI this is Cancer = True
    '''
    graph.reset()
    add_evidence(x2, True)
    add_evidence(x3, True)
    graph.propagate()
    normalizer = x3.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.156
    m = marg(x1, False, normalizer)
    assert m == 0.844
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 1.0
    m = marg(x3, False, normalizer)
    assert m == 0.0
    m = marg(x4, True, normalizer)
    assert m == 0.9
    m = marg(x4, False, normalizer)
    assert m == 0.1
    m = marg(x5, True, normalizer)
    assert m == 0.650
    m = marg(x5, False, normalizer)
    assert m == 0.350
    
def test_add_evidence_x5_true_x2_true():
    graph.reset()
    add_evidence(x5, True)
    add_evidence(x2, True)
    graph.propagate()
    normalizer = x5.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.102
    m = marg(x1, False, normalizer)
    assert m == 0.898
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 0.067
    m = marg(x3, False, normalizer)
    assert m == 0.933
    m = marg(x4, True, normalizer)
    assert m == 0.247
    m = marg(x4, False, normalizer)
    assert m == 0.753
    m = marg(x5, True, normalizer)
    assert m == 1.0
    m = marg(x5, False, normalizer)
    assert m == 0.0
    

# Now we are going to test based on the second
# half of table 2.2 where the prior for prior
# for the Smoking parameter (x2=True) is
# set to 0.5. We start by redefining the
# PMF for fB and then rebuilding the factor
# graph


def test_marginals_table_22_part_2_x2_prior_change():
    def fB(x2):
        if x2.value == True:
            return 0.5
        elif x2.value == False:
            return 0.5
    fB.domains = dict(x2=[True, False])

    # Build the network
    fA_node = FactorNode('fA', fA)
    fB_node = FactorNode('fB', fB)
    fC_node = FactorNode('fC', fC)
    fD_node = FactorNode('fD', fD)
    fE_node = FactorNode('fE', fE)

    x1 = VariableNode('x1', parents=[fA_node])
    x2 = VariableNode('x2', parents=[fB_node])
    x3 = VariableNode('x3', parents=[fC_node])
    x4 = VariableNode('x4', parents=[fD_node])
    x5 = VariableNode('x5', parents=[fE_node])

    # Now set the parents for the factor nodes...
    fA_node.parents = []
    fB_node.parents = []
    fC_node.parents = [x1, x2]
    fD_node.parents = [x3]
    fE_node.parents = [x3]

    # Now set children for Variable Nodes...
    x1.children = [fC_node]
    x2.children = [fC_node]
    x3.children = [fD_node, fE_node]
    x4.children = []
    x5.children = []

    # Now set the children for the factor nodes...
    fA_node.children = [x1]
    fB_node.children = [x2]
    fC_node.children = [x3]
    fD_node.children = [x4]
    fE_node.children = [x5]

    graph = FactorGraph([x1, x2, x3, x4, x5, fA_node, fB_node, fC_node, fD_node, fE_node])
    graph.propagate()
    m = marg(x1, True)
    assert m == 0.1
    m = marg(x1, False)
    assert m == 0.9
    m = marg(x2, True)
    assert m == 0.5
    m = marg(x2, False)
    assert m == 0.5
    m = marg(x3, True)
    assert m == 0.017
    m = marg(x3, False)
    assert m == 0.983
    m = marg(x4, True)
    assert m == 0.212
    m = marg(x4, False)
    assert m == 0.788
    m = marg(x5, True)
    assert m == 0.306
    m = marg(x5, False)
    assert m == 0.694
    
    # Now set D=T (x5=True)
    graph.reset()
    add_evidence(x5, True)
    graph.propagate()
    normalizer = marg(x5, True)
    assert normalizer == 0.306
    m = marg(x1, True, normalizer)
    assert m == 0.102
    m = marg(x1, False, normalizer)
    assert m == 0.898
    m = marg(x2, True, normalizer)
    assert m == 0.508
    m = marg(x2, False, normalizer)
    assert m == 0.492
    m = marg(x3, True, normalizer)
    assert m == 0.037
    m = marg(x3, False, normalizer)
    assert m == 0.963
    m = marg(x4, True, normalizer)
    assert m == 0.226
    m = marg(x4, False, normalizer)
    assert m == 0.774
    m = marg(x5, True, normalizer)
    assert m == 1.0
    m = marg(x5, False, normalizer)
    assert m == 0.0


    graph.reset()
    add_evidence(x2, True)
    graph.propagate()
    normalizer = marg(x2, True)
    m = marg(x1, True, normalizer)
    assert m == 0.1
    m = marg(x1, False, normalizer)
    assert m == 0.9
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 0.032
    m = marg(x3, False, normalizer)
    assert m == 0.968
    m = marg(x4, True, normalizer)
    assert m == 0.222 # Note that in Table 2.2 x4 and x5 marginals are reversed
    m = marg(x4, False, normalizer)
    assert m == 0.778
    m = marg(x5, True, normalizer)
    assert m == 0.311
    m = marg(x5, False, normalizer)
    assert m == 0.689

    '''
    x3 = True in BAI this is Cancer = True
    '''
    graph.reset()
    add_evidence(x3, True)
    graph.propagate()
    normalizer = x3.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.201
    m = marg(x1, False, normalizer)
    assert m == 0.799
    m = marg(x2, True, normalizer)
    assert m == 0.917
    m = marg(x2, False, normalizer)
    assert m == 0.083
    m = marg(x3, True, normalizer)
    assert m == 1.0
    m = marg(x3, False, normalizer)
    assert m == 0.0
    m = marg(x4, True, normalizer)
    assert m == 0.9
    m = marg(x4, False, normalizer)
    assert m == 0.1
    m = marg(x5, True, normalizer)
    assert m == 0.650
    m = marg(x5, False, normalizer)
    assert m == 0.350

    '''
    x2 = True in BAI this is Smoker = True
    x3 = True in BAI this is Cancer = True
    '''
    graph.reset()
    add_evidence(x2, True)
    add_evidence(x3, True)
    graph.propagate()
    normalizer = x3.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.156
    m = marg(x1, False, normalizer)
    assert m == 0.844
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 1.0
    m = marg(x3, False, normalizer)
    assert m == 0.0
    m = marg(x4, True, normalizer)
    assert m == 0.9
    m = marg(x4, False, normalizer)
    assert m == 0.1
    m = marg(x5, True, normalizer)
    assert m == 0.650
    m = marg(x5, False, normalizer)
    assert m == 0.350


    graph.reset()
    add_evidence(x5, True)
    add_evidence(x2, True)
    graph.propagate()
    normalizer = x5.marginal(True)
    m = marg(x1, True, normalizer)
    assert m == 0.102
    m = marg(x1, False, normalizer)
    assert m == 0.898
    m = marg(x2, True, normalizer)
    assert m == 1.0
    m = marg(x2, False, normalizer)
    assert m == 0.0
    m = marg(x3, True, normalizer)
    assert m == 0.067
    m = marg(x3, False, normalizer)
    assert m == 0.933
    m = marg(x4, True, normalizer)
    assert m == 0.247
    m = marg(x4, False, normalizer)
    assert m == 0.753
    m = marg(x5, True, normalizer)
    assert m == 1.0
    m = marg(x5, False, normalizer)
    assert m == 0.0

