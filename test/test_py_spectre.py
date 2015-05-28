from py_spectre import * 
import random
import unittest

class NetlistStatementTestCase(unittest.TestCase):
    """ Tests for py_spectre NetlistStatement class. """
    def test_from_string(self):
        line = 'R1 vid 0 resistor R=1k'
        R1 = NetlistStatement.from_string(line)
        self.assertEqual(R1.master, 'resistor')
        self.assertEqual(R1.name, 'R1')
        self.assertEqual(R1.nodes[0], 'vid')
        self.assertEqual(R1.nodes[1], '0')
        self.assertEqual(R1.parameters["R"], '1k')
        self.assertTrue('R' in R1.parameters)
        self.assertTrue(R1._ns_match(name='R1'))
        self.assertTrue(R1._ns_match(name='R*'))
        self.assertFalse(R1._ns_match(name='R*', regex=True))
        self.assertTrue(R1._ns_match(name='R.*?', regex=True))
        self.assertTrue(R1._ns_match(node='vid'))
        self.assertFalse(R1._ns_match(node='vida'))
        self.assertFalse(R1._ns_match(node='vidb'))
        self.assertFalse(R1._ns_match(node='00'))
        self.assertTrue(R1._ns_match(master='resistor'))
        self.assertTrue(R1._ns_match(master='res*'))
        self.assertTrue(R1._ns_match(p_name='R'))
        self.assertFalse(R1._ns_match(p_name='1k'))
        self.assertTrue(R1._ns_match(p_val='1k'))
        self.assertFalse(R1._ns_match(p_val='R'))
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertTrue(R1._ns_match(p_name='R', p_val=constraint1))
        self.assertTrue(R1._ns_match(p_name='R', p_val=constraint2))
        self.assertFalse(R1._ns_match(p_name='R', p_val=constraint3))
        self.assertFalse(R1._ns_match(p_name='R', p_val=constraint4))

        line = ('  R2  node0    node1   resistor     '
                'R  =  R0 *   1k / 42  aTasi = 5e7')
        R2 = NetlistStatement.from_string(line)
        self.assertEqual(R2.master, 'resistor')
        self.assertEqual(R2.name, 'R2')
        self.assertEqual(R2.nodes[0], 'node0')
        self.assertEqual(R2.nodes[1], 'node1')
        self.assertTrue('R' in R2.parameters)
        self.assertEqual(R2.parameters["R"], 'R0 * 1k / 42')
        self.assertTrue('aTasi' in R2.parameters)
        self.assertEqual(R2.parameters["aTasi"], '5e7')
        self.assertTrue(R2._ns_match(name='R2'))
        self.assertTrue(R2._ns_match(name='R*'))
        self.assertFalse(R2._ns_match(name='R*', regex=True))
        self.assertTrue(R2._ns_match(name='R.*?', regex=True))
        self.assertTrue(R2._ns_match(node='node0'))
        self.assertTrue(R2._ns_match(node='node1'))
        self.assertFalse(R2._ns_match(node='node'))
        self.assertFalse(R2._ns_match(node='na*'))
        self.assertFalse(R2._ns_match(node='00'))
        self.assertTrue(R2._ns_match(master='resistor'))
        self.assertTrue(R2._ns_match(master='res*'))
        self.assertTrue(R2._ns_match(p_name='R'))
        self.assertFalse(R2._ns_match(p_name='1k'))
        self.assertTrue(R2._ns_match(p_val='R0 * 1k / 42'))
        self.assertFalse(R2._ns_match(p_val='1k'))
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertFalse(R2._ns_match(p_name='R', p_val=constraint1))
        self.assertFalse(R2._ns_match(p_name='R', p_val=constraint2))
        self.assertFalse(R2._ns_match(p_name='R', p_val=constraint3))
        self.assertFalse(R2._ns_match(p_name='R', p_val=constraint4))

        line = '   name_and_nodes   node0    node1  node2'
        name_and_nodes = NetlistStatement.from_string(line)
        self.assertEqual(name_and_nodes.master, 'node2')
        self.assertEqual(name_and_nodes.name, 'name_and_nodes')
        self.assertEqual(len(name_and_nodes.parameters), 0)
        self.assertEqual(name_and_nodes.nodes[0], 'node0')
        self.assertEqual(name_and_nodes.nodes[1], 'node1')
        self.assertEqual(name_and_nodes.nodes[2], 'node2')
        self.assertTrue(name_and_nodes._ns_match(name='name_and_nodes'))
        self.assertTrue(name_and_nodes._ns_match(name='name*'))
        self.assertFalse(name_and_nodes._ns_match(name='name*', regex=True))
        self.assertTrue(name_and_nodes._ns_match(name='name.*?', regex=True))
        self.assertTrue(name_and_nodes._ns_match(node='node0'))
        self.assertTrue(name_and_nodes._ns_match(node='node1'))
        self.assertTrue(name_and_nodes._ns_match(node='node2'))
        self.assertFalse(name_and_nodes._ns_match(node='node'))
        self.assertFalse(name_and_nodes._ns_match(node='na*'))
        self.assertFalse(name_and_nodes._ns_match(node='00'))
        self.assertTrue(name_and_nodes._ns_match(master=''))
        self.assertTrue(name_and_nodes._ns_match(master='node2'))
        self.assertFalse(name_and_nodes._ns_match(p_name='R'))
        self.assertFalse(name_and_nodes._ns_match(p_name='1k'))
        self.assertFalse(name_and_nodes._ns_match(p_name='*'))
        self.assertFalse(name_and_nodes._ns_match(p_val='R0 * 1k / 42'))
        self.assertFalse(name_and_nodes._ns_match(p_val='1k'))
        self.assertFalse(name_and_nodes._ns_match(p_val='*'))
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertFalse(name_and_nodes._ns_match(p_name='node0', p_val=constraint1))
        self.assertFalse(name_and_nodes._ns_match(p_name='node1', p_val=constraint2))
        self.assertFalse(name_and_nodes._ns_match(p_name='node2', p_val=constraint3))
        self.assertFalse(name_and_nodes._ns_match(p_name='name_and_nodes', p_val=constraint4))

        line = '  name_and_params  param1 = val1  param2    =     val2'
        name_and_params = NetlistStatement.from_string(line)
        self.assertEqual(name_and_params.master, '')
        self.assertEqual(name_and_params.name, 'name_and_params')
        self.assertEqual(len(name_and_params.parameters), 2)
        self.assertTrue('param1' in name_and_params.parameters)
        self.assertEqual(name_and_params.parameters["param1"], 'val1')
        self.assertTrue('param2' in name_and_params.parameters)
        self.assertEqual(name_and_params.parameters["param2"], 'val2')
        self.assertEqual(len(name_and_params.nodes), 0)
        self.assertTrue(name_and_params._ns_match(name='name_and_params'))
        self.assertTrue(name_and_params._ns_match(name='name*'))
        self.assertFalse(name_and_params._ns_match(name='name*', regex=True))
        self.assertTrue(name_and_params._ns_match(name='name.*?', regex=True))
        self.assertFalse(name_and_params._ns_match(node='node0'))
        self.assertFalse(name_and_params._ns_match(node='node2'))
        self.assertFalse(name_and_params._ns_match(node='node'))
        self.assertFalse(name_and_params._ns_match(node='na*'))
        self.assertFalse(name_and_params._ns_match(node='*'))
        self.assertFalse(name_and_params._ns_match(master='*'))
        self.assertFalse(name_and_params._ns_match(master='node2'))
        self.assertFalse(name_and_params._ns_match(p_name='R'))
        self.assertTrue(name_and_params._ns_match(p_name='param1'))
        self.assertTrue(name_and_params._ns_match(p_name='param2'))
        self.assertFalse(name_and_params._ns_match(p_name='1k'))
        self.assertTrue(name_and_params._ns_match(p_name='*'))
        self.assertFalse(name_and_params._ns_match(p_val='R0 * 1k / 42'))
        self.assertFalse(name_and_params._ns_match(p_val='1k'))
        self.assertTrue(name_and_params._ns_match(p_val='val1'))
        self.assertTrue(name_and_params._ns_match(p_val='val2'))
        self.assertTrue(name_and_params._ns_match(p_val='*'))
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertFalse(name_and_params._ns_match(p_name='*', p_val=constraint1))
        self.assertFalse(name_and_params._ns_match(p_name='*', p_val=constraint2))
        self.assertFalse(name_and_params._ns_match(p_name='*', p_val=constraint3))
        self.assertFalse(name_and_params._ns_match(p_name='*', p_val=constraint4))

        line = ('  name_master_and_params master_name  param1 = val1  param2'
                '    =     val2')
        name_master_and_params = NetlistStatement.from_string(line)
        self.assertEqual(name_master_and_params.master, 'master_name')
        self.assertEqual(name_master_and_params.name, 'name_master_and_params')
        self.assertEqual(len(name_master_and_params.parameters), 2)
        self.assertTrue('param1' in name_master_and_params.parameters)
        self.assertEqual(name_master_and_params.parameters["param1"], 'val1')
        self.assertTrue('param2' in name_master_and_params.parameters)
        self.assertEqual(name_master_and_params.parameters["param2"], 'val2')
        self.assertTrue(name_master_and_params._ns_match(name='name_master_and_params'))
        self.assertTrue(name_master_and_params._ns_match(name='name*'))
        self.assertFalse(name_master_and_params._ns_match(name='name*', regex=True))
        self.assertTrue(name_master_and_params._ns_match(name='name.*?', regex=True))
        self.assertFalse(name_master_and_params._ns_match(node='node0'))
        self.assertFalse(name_master_and_params._ns_match(node='node2'))
        self.assertFalse(name_master_and_params._ns_match(node='node'))
        self.assertFalse(name_master_and_params._ns_match(node='na*'))
        self.assertTrue(name_master_and_params._ns_match(node='*'))
        self.assertTrue(name_master_and_params._ns_match(node='master_name'))
        self.assertTrue(name_master_and_params._ns_match(master='*'))
        self.assertTrue(name_master_and_params._ns_match(master='master_name'))
        self.assertFalse(name_master_and_params._ns_match(master='node2'))
        self.assertFalse(name_master_and_params._ns_match(p_name='R'))
        self.assertTrue(name_master_and_params._ns_match(p_name='param1'))
        self.assertTrue(name_master_and_params._ns_match(p_name='param2'))
        self.assertFalse(name_master_and_params._ns_match(p_name='1k'))
        self.assertTrue(name_master_and_params._ns_match(p_name='*'))
        self.assertFalse(name_master_and_params._ns_match(p_val='R0 * 1k / 42'))
        self.assertFalse(name_master_and_params._ns_match(p_val='1k'))
        self.assertTrue(name_master_and_params._ns_match(p_val='val1'))
        self.assertTrue(name_master_and_params._ns_match(p_val='val2'))
        self.assertTrue(name_master_and_params._ns_match(p_val='*'))
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertFalse(name_master_and_params._ns_match(p_name='*', p_val=constraint1))
        self.assertFalse(name_master_and_params._ns_match(p_name='*', p_val=constraint2))
        self.assertFalse(name_master_and_params._ns_match(p_name='*', p_val=constraint3))
        self.assertFalse(name_master_and_params._ns_match(p_name='*', p_val=constraint4))



class PySpectreScriptTestCase(unittest.TestCase):
    """ Tests for py_spectre PySpectreScript class. """
    def test_search(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        """ name tests """
        self.assertEqual(len(pss.search('R*')), 2)
        self.assertEqual(len(pss.search('R*').search('R*')), 2)
        self.assertEqual(len(pss.search('C*')), 2)
        self.assertEqual(len(pss.search('subckt', descend=True)), 3)
        self.assertEqual(len(pss.search('R*', descend=True)), 3)
        self.assertEqual(len(pss.search('C*', descend=True)), 3)
        for ns in pss.search('*'):
            self.assertEqual(len(pss.search(ns.name)), 1)
        """ node tests """
        self.assertEqual(len(pss.search(node='VIP')), 2)
        self.assertEqual(len(pss.search(node='VIP', descend=True)), 4)
        self.assertEqual(len(pss.search(node='VIM')), 2)
        self.assertEqual(len(pss.search(node='VIM', descend=True)), 4)
        self.assertEqual(len(pss.search(node='0')), 8)
        self.assertEqual(len(pss.search(node='0', descend=True)), 10)
        self.assertEqual(len(pss.search(node='VAM')), 3)
        self.assertEqual(len(pss.search(node='VAM', descend=True)), 3)
        self.assertEqual(len(pss.search(node='VAP')), 3)
        self.assertEqual(len(pss.search(node='VAP', descend=True)), 3)
        self.assertEqual(len(pss.search(node='VID')), 2)
        self.assertEqual(len(pss.search(node='VID', descend=True)), 2)
        self.assertEqual(len(pss.search(node='VOM')), 2)
        self.assertEqual(len(pss.search(node='VOM', descend=True)), 4)
        self.assertEqual(len(pss.search(node='VOP')), 2)
        self.assertEqual(len(pss.search(node='VOP', descend=True)), 4)
        self.assertEqual(len(pss.search(node='VOD')), 4)
        self.assertEqual(len(pss.search(node='VOD', descend=True)), 4)
        self.assertEqual(len(pss.search(node='VOC')), 1)
        self.assertEqual(len(pss.search(node='VOC', descend=True)), 1)
        self.assertEqual(len(pss.search(node='VG')), 2)
        self.assertEqual(len(pss.search(node='VG', descend=True)), 2)
        """ master tests """
        self.assertEqual(len(pss.search(master='resistor')), 2)
        self.assertEqual(len(pss.search(name='R*', master='resistor')), 2)
        self.assertEqual(len(pss.search('R*', master='resistor')), 2)
        self.assertEqual(len(pss.search(master='resistor', descend=True)), 3)
        self.assertEqual(len(pss.search(master='res*', descend=True)), 3)
        self.assertEqual(len(pss.search(master='capacitor')), 2)
        self.assertEqual(len(pss.search(name='C*', master='capacitor')), 2)
        self.assertEqual(len(pss.search('C*', master='capacitor')), 2)
        self.assertEqual(len(pss.search(master='capacitor', descend=True)), 3)
        self.assertEqual(len(pss.search(master='cap*', descend=True)), 3)
        self.assertEqual(len(pss.search(master='ideal_balun')), 2)
        self.assertEqual(len(pss.search(master='ideal_balun', descend=True)), 3)
        self.assertEqual(len(pss.search(master='vsource')), 1)
        self.assertEqual(len(pss.search(master='vsource', descend=True)), 1)
        self.assertEqual(len(pss.search(master='isource')), 1)
        self.assertEqual(len(pss.search(master='isource', descend=True)), 1)
        self.assertEqual(len(pss.search(master='nmos')), 1)
        self.assertEqual(len(pss.search(master='nmos', descend=True)), 1)
        self.assertEqual(len(pss.search(master='transformer')), 0)
        self.assertEqual(len(pss.search(master='transformer', descend=True)), 2)
        self.assertEqual(len(pss.search(master='spectre_test_RC')), 0)
        self.assertEqual(len(pss.search(master='spectre_test_RC', descend=True)), 3)
        self.assertEqual(len(pss.search(master='spectre_test_RCRC')), 1)
        self.assertEqual(len(pss.search(master='spectre_test_RCRC', descend=True)), 2)
        """ p_name tests """
        self.assertEqual(len(pss.search(p_name='r')), 2)
        self.assertEqual(len(pss.search(p_name='r', descend=True)), 3)
        self.assertEqual(len(pss.search(p_name='c')), 2)
        self.assertEqual(len(pss.search(p_name='c', descend=True)), 3)
        self.assertEqual(len(pss.search(p_name='R1')), 1)
        self.assertEqual(len(pss.search(p_name='R1', descend=True)), 1)
        """ p_val tests """
        self.assertEqual(len(pss.search(p_val='R1')), 0)
        self.assertEqual(len(pss.search(p_val='R1', descend=True)), 1)
        self.assertEqual(len(pss.search(p_name='_par0', p_val='R1')), 0)
        self.assertEqual(len(pss.search(p_name='_par0', p_val='R1', descend=True)), 1)
        constraint1 = lambda R: R < 2e3
        constraint2 = lambda R: R > 500
        constraint3 = lambda R: R > 2e3
        constraint4 = lambda R: R < 500
        self.assertEqual(len(pss.search(name='R*', p_name='r', p_val=constraint1)), 2)
        self.assertEqual(len(pss.search(name='R*', p_name='r', p_val=constraint2)), 2)
        self.assertEqual(len(pss.search(name='R*', p_name='r', p_val=constraint3)), 0)
        self.assertEqual(len(pss.search(name='R*', p_name='r', p_val=constraint4)), 0)
        self.assertEqual(len(pss.search(p_name='r', p_val=constraint1)), 2)
        self.assertEqual(len(pss.search(p_name='r', p_val=constraint2)), 2)
        self.assertEqual(len(pss.search(p_name='r', p_val=constraint3)), 0)
        self.assertEqual(len(pss.search(p_name='r', p_val=constraint4)), 0)
        self.assertEqual(len(pss.search(p_val=constraint1)), 0)
        self.assertEqual(len(pss.search(p_val=constraint2)), 0)
        self.assertEqual(len(pss.search(p_val=constraint3)), 0)
        self.assertEqual(len(pss.search(p_val=constraint4)), 0)

    def test_replace(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        pss_str = str(pss)
        names = {} 
        masters = {} 
        nodes = {} 
        for k, ns in enumerate(pss.search('*', descend=True)):
            names[k] = ns.name
            masters[k] = ns.master
            nodes[k] = list(ns.nodes)
            ns.replace(ns.name, 'diff_name')
            if ns.master:
                ns.replace(ns.master, 'diff_master')
            for j, node in enumerate(ns.nodes):
                try:
                    int(node)
                except:
                    ns.replace(node, 'diff_node' + str(j)) 
        self.assertNotEqual(pss_str, str(pss))
        for k, ns in enumerate(pss.search('*', descend=True)):
            ns.replace(ns.name, names[k])
            if ns.master:
                ns.replace(ns.master, masters[k])
            for j, node in enumerate(ns.nodes):
                ns.replace(node, nodes[k][j])
        self.assertEqual(pss_str, str(pss))
        pss.search('*').replace('0', 'zero')
        self.assertNotEqual(pss_str, str(pss))
        pss.search('*').replace('zero', '0')
        self.assertEqual(pss_str, str(pss))

    def test_change(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        pss_str = str(pss)
        names = {}
        masters = {}
        nodes = {}
        params = {}
        for k, ns in enumerate(pss.search('*', descend=True)):
            names[k] = ns.name 
            masters[k] = ns.master 
            nodes[k] = list(ns.nodes)
            params[k] = dict(ns.parameters)
            ns.change('name', 'diff_name')
            for j, node in enumerate(ns.nodes):
                ns.change(node, 'diff_node' + str(j))
            for m, key in enumerate(ns.parameters):
                ns.change(key, 'new_val' + str(m))
        self.assertNotEqual(pss_str, str(pss))
        for k, ns in enumerate(pss.search('*', descend=True)):
            ns.change('name', names[k])
            for j, node in enumerate(ns.nodes):
                ns.change(node, nodes[k][j])
            for m, key in enumerate(ns.parameters):
                ns.change(key, params[k][key])
        self.assertEqual(pss_str, str(pss))
        pss.search('*', descend=True).change('0', 'zero')
        self.assertNotEqual(pss_str, str(pss))
        pss.search('*', descend=True).change('zero', '0')
        self.assertEqual(pss_str, str(pss))
        pss.search(p_name='r', p_val=lambda R: R < 2e3, descend=True).change('r', '1.7k')
        self.assertNotEqual(pss_str, str(pss))
        pss.search(p_name='r', p_val=lambda R: R < 2e3, descend=True).change('r', '1K')
        self.assertEqual(pss_str, str(pss))
    
    def test_scale(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        pss.search(p_name='r').scale('r', 1)
        pss_str = str(pss)
        pss.search(p_name='r').scale('r', 2)
        self.assertNotEqual(pss_str, str(pss))
        pss.search(p_name='r').scale('r', 0.5)
        self.assertEqual(pss_str, str(pss))
        pss.search(p_name='r', descend=True).scale('r', 2)
        self.assertNotEqual(pss_str, str(pss))
        pss.search(p_name='r', descend=True).scale('r', 0.5)
        self.assertEqual(pss_str, str(pss))
        pss.search(p_name='r', p_val=lambda R: R<1e4).scale('r', 3)
        ns = pss.search(p_name='r', p_val=lambda R: R<1e4)[0]
        self.assertEqual(ns.parameters['r'], 3000.0)
        ns = pss.search(p_name='r', p_val=lambda R: R<1e4)[1]
        self.assertEqual(ns.parameters['r'], 3000.0)
        pss.search(p_name='r', p_val=lambda R: R<1e4)[0].scale('r', 2)
        ns = pss.search(p_name='r', p_val=lambda R: R<1e4)[0]
        self.assertEqual(ns.parameters['r'], 6000.0)

    def test_add_and_delete_parameter(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        pss_str = str(pss)
        for ns in pss.search('*'):
            value = random.random() * 1e12
            ns.add_param('weird_param_name', 1e12)
        self.assertNotEqual(pss_str, str(pss))
        for ns in pss.search('*'):
            ns.del_param('weird_param_name')
        self.assertEqual(pss_str, str(pss))
        for ns in pss.search('*'):
            value = random.randint(1, 1e12)
            ns.add_param('weird_param_name', 1e12)
        self.assertNotEqual(pss_str, str(pss))
        pss.search('*').del_param('weird_param_name')
        self.assertEqual(pss_str, str(pss))
        pss.search('*').add_param('weird_param_name', 1e12)
        self.assertNotEqual(pss_str, str(pss))
        for ns in pss.search('*'):
            ns.del_param('weird_param_name')
        self.assertEqual(pss_str, str(pss))
        pss.search('*', descend=True).add_param('weird_param_name', 1e12)
        self.assertNotEqual(pss_str, str(pss))
        pss.search('*', descend=True).del_param('weird_param_name')
        self.assertEqual(pss_str, str(pss))

    def test_add_and_remove(self):
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        pss_str = str(pss)
        ns = pss.search('R0')[0]
        pss.add(ns, 14)
        ns = pss.search('R0')[1]
        ns.change('name', 'Rnew')
        self.assertNotEqual(pss_str, str(pss))
        pss.remove('Rnew')
        self.assertEqual(pss_str, str(pss))
        for k in range(20):
            ns = 'X' + str(k) + ' VIM VIP resistor r=1e4'
            pss.add(ns)
        self.assertNotEqual(pss_str, str(pss))
        for k in range(20):
            index = random.randint(0,len(pss.nsl)-1)
            ns = 'Z' + str(k) + ' VIM VIP resistor r=1e4'
            pss.add(ns, index)
        self.assertNotEqual(pss_str, str(pss))
        pss.remove('X*')
        pss.remove('Z*')
        self.assertEqual(pss_str, str(pss))

    def test_run_write_read_results(self):
        run_scripts = True
        path_to_script = './spectre_scripts/spectre_test0.scs'
        pss = PySpectreScript(path_to_script)
        if run_scripts:
            pss.run()
            print pss.results()
            print pss.results('dc.dc')
            print pss.results('dc.dc', 'VOD')
            print pss.results('dcOp.dc', 'VOD')
            for result in pss.results('dcOp.dc'):
                value = pss.results('dcOp.dc', result)
                print str(result) + ': ' + str(value)

if __name__ == '__main__':
    unittest.main()
