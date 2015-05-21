import sys
sys.path.append('../')

import unittest
from py_spectre.py_spectre import NetlistStatement, PySpectreScript
from py_spectre.post.read_results import read_results

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

        line = ('  R2  node0    node1   resistor     '
                'R  =  R0 *   1k / 42  aTasi = 5e7')
        R2 = NetlistStatement.from_string(line)
        self.assertEqual(R2.master, 'resistor')
        self.assertEqual(R2.name, 'R2')
        self.assertEqual(R2.nodes[0], 'node0')
        self.assertEqual(R2.nodes[1], 'node1')
        self.assertTrue('R' in R2.parameters)
        self.assertEqual(R2.parameters["R"], 'R0*1k/42')
        self.assertTrue('aTasi' in R2.parameters)
        self.assertEqual(R2.parameters["aTasi"], '5e7')

        line = '   name_and_nodes   node0    node1  node2'
        name_and_nodes = NetlistStatement.from_string(line)
        self.assertEqual(name_and_nodes.master, '')
        self.assertEqual(name_and_nodes.name, 'name_and_nodes')
        self.assertEqual(len(name_and_nodes.parameters), 0)
        self.assertEqual(name_and_nodes.nodes[0], 'node0')
        self.assertEqual(name_and_nodes.nodes[1], 'node1')
        self.assertEqual(name_and_nodes.nodes[2], 'node2')

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

class NetlistStatementTestCase(unittest.TestCase):
    """ Tests for py_spectre PySpectreScript class. """
    def test_write_script(self):
        run_scripts = False
        pss = PySpectreScript()
        pss.read_script('./spectre_test_scripts/spectre_test0.scs')
        pss.write_script('./spectre_test_scripts/write_script_output/spectre_test0.write_script.scs')
        pss.add_command_line_args('-raw ./spectre_scripts/psf/test0','-format psfascii')
        if run_scripts:
            pss.run_script()

        pss = PySpectreScript()
        pss.read_script('./spectre_test_scripts/spectre_test1.scs')
        pss.write_script('./spectre_test_scripts/write_script_output/spectre_test1.write_script.scs')
        pss.add_command_line_args('-raw ./spectre_scripts/psf/test1','-format psfascii')
        if run_scripts:
            pss.run_script()

if __name__ == '__main__':
    unittest.main()
