# The MIT License (MIT)
# 
# Copyright (c) 2015 Ryan Boesch
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import copy
import os
import re

class NetlistStatement(object):
    """ Holds the contents of a Spectre netlist statement.

    This class represents the information in arbitrary spectre netlist
    statements. The 'name' attribute must be defined for every ns, but the
    other attributes are optional. Uniqueness of netlist statements is often
    but not always determined by the name. The method 'ns_match' is the best
    way to identify NetlistStatment objects.

    Attributes:
        name: A string holding the name of the netlist statement.
        nodes: A list of strings that contains the nodes. 
        master: An alias for the last node in nodes.
        parameters: A dictionary holding all the parameters.
        subnetlist: A list of NetlistStatement objects. It is a representation
        of a sprectre subnetlist contained in curly braces.
    """
    def __init__(self, name='', nodes=None, parameters=None, subnetlist=None):
        if nodes is None:
            nodes = []
        if parameters is None:
            parameters = {}
        if subnetlist is None:
            subnetlist = []
        self.name = name
        self.nodes = nodes
        self.parameters = parameters
        self.subnetlist = subnetlist

    def get_master(self):
        if self.nodes:
            return self.nodes[-1]
        else:
            return ''

    def set_master(self, value):
        if self.nodes and value:
            self.nodes[-1] = value
        elif value:
            self.nodes = [value]

    master = property(get_master, set_master)
    
    def replace(self, old, new):
        self.name = self.name.replace(old, new)
        for j, node in enumerate(self.nodes):
            self.nodes[j] = self.nodes[j].replace(old, new)
        for key in self.parameters:
            new_key = key.replace(old, new)
            val = self.parameters.pop(key)
            new_val = val.replace(old, new)
            self.parameters[new_key] = new_val

    def change(self, key, value):
        if key == 'name':
            self.name = value
        elif key == 'master':
            self.master = value
        elif key in self.nodes:
            for index, node in enumerate(self.nodes):
                if key == node:
                    self.nodes[index] = value
        elif key in self.parameters:
            self.parameters[key] = value

    def scale(self, p_name, alpha):
        if p_name in self.parameters:
            p_val = string_to_float(self.parameters[p_name])
            if not isinstance(p_val, str): 
                self.parameters[p_name] = p_val * alpha

    def del_param(self, key):
        if key in self.parameters:
            del self.parameters[key]

    def add_param(self, param_name, param_value):
        self.parameters[param_name] = param_value
           
    def __str__(self):
        string = self.name + ' '
        for node in self.nodes:
            string += node + ' '
        for p_name, p_val in sorted(self.parameters.items()):
            string += ' ' + p_name + '=' + str(p_val)
        return string

    def __repr__(self):
        string = str(self) 
        if self.subnetlist:
            string += ' { ... }'
        return string

    def _ns_match(self, name='', master='', node='', p_name='', p_val='', regex=False):
        """  Identify netlist statement with conditions. 
        
        This method will return true is there is a match for all inputs
        provided. The method supports the '*' wild card character. Regular
        expressions are supported through the regex flag. Comparison functions
        are supported for the p_val input. 
        """
        match = True
        if name and not self.name: match = False
        if master and not self.master: match = False
        if node and not self.nodes: match = False
        if p_name and not self.parameters: match = False
        if p_val and not self.parameters: match = False 
        if name: match &= self.compare(name, self.name, regex) 
        if master: match &= self.compare(master, self.master, regex) 
        if node:
            node_match = False
            for node_name in self.nodes:
                node_match |= self.compare(node, node_name, regex)  
            match &= node_match
        if p_name and p_val:
            param_match = False
            for key in self.parameters:
                if self.compare(p_name, key, regex):
                    value = self.parameters[key]
                    if hasattr(p_val, '__call__'):
                        value_float = string_to_float(value)
                        if isinstance(value_float, str): 
                            param_match = False
                        else:
                            param_match |= p_val(value_float) 
                        if not isinstance(param_match, bool):
                            param_match = False
                    else:
                        param_match |= self.compare(p_val, value, regex) 
            match &= param_match
        elif p_name:
            param_name_match = False
            for key in self.parameters:
                param_name_match |= self.compare(p_name, key, regex) 
            match &= param_name_match
        elif p_val:
            param_value_match = False
            for value in self.parameters.values():
                param_value_match |= self.compare(str(p_val), str(value), regex) 
            match &= param_value_match
        return match

    @staticmethod
    def compare(match_string, string, regex):
        if not regex:
            match_string = match_string.replace('*', '.*?')
            match_string = '^' + match_string + '$'
        return bool(re.match(match_string, string)) 
        
    @classmethod
    def from_string(cls, ns_string):
        """ Alternative constructor that parses an ns_string into the netlist statement variables.  

        Supports spectre netlist statements of the form: 
        name [node0 node1 ...] 
        name [node0 node1 ...] [master] param0=val0 param1=val1 ...

        Case 1: If there are no parameters (i.e. no terms with '=' signs), then the netlist
        statement is assumed to have the first form. The first term is stored in the 
        attribute 'name' and the rest of the terms are stored in the attribute 'nodes' in
        a list. Some examples of netlist statements in this form are:
        save va vb vc
        global 0 vdd vss
        There are some edge cases that do fit this form, for example:
        sens (VO1 VO2) to (R0 R1 C1) for (dc dcOp ac)
        For consistency, these are lumped into the first form anyways.

        Case 2: If there are parameters, they are stored under the key parameters
        in a dictionary. There is at least one term before the parameters and this is stored
        in the attribute 'name'.
        If there are two or more terms before the parameters, the term immediately 
        before the parameters is stored in the key 'master'. If there are 3 or more terms,
        the remaining terms are stored under the key 'nodes'.

        Statements with curly brace subnetlists must be parsed separately. 
        
        Args: 
            ns_string: A spectre netlist statement string.

        Returns:
            A NetlistStatement object initialized with the parameters parsed from ns_string. 
        """

        split_param_list = ns_string.split('=')
        parameters = {}
        nodes = []
        if len(split_param_list) != 1:  # if there are parameters
            # split_statement = [name, [node0, node1,...], first_param]
            split_statement = split_param_list.pop(0).split()
            if len(split_statement) >= 3:  # if there are nodes
                nodes = split_statement[1:-1]
            # start parsing parameters
            param_name = split_statement[-1]
            for n, split_param in enumerate(split_param_list):
                param_list_part = split_param.split()
                if n == len(split_param_list)-1:  # if last split_parameter
                    param_value = split_param
                else:
                    param_value = ' '.join(param_list_part[:-1]) # join except param_name
                parameters[param_name.strip()] = param_value.strip()
                param_name = param_list_part[-1]
        else:  # there are no parameters
            # split_statement = [name, [node0, node1,...]]
            split_statement = ns_string.split()
            if len(split_statement) > 1:  # if there are nodes
                nodes = split_statement[1:]
        name = split_statement[0]
        return cls(name, nodes, parameters)

    
class PySpectreScript(object):
    def __init__(self, path=''):
        self.nsl = []
        self.command_line_args = []
        self.path_to_script_out = ''
        self.path_to_script_in = ''
        self.path_to_results = ''
        self.psf_results = {}
        if path:
            self.read(path)
    
    #########################
    # Netlist Modifications #
    #########################
    def search(self, name='', master='', node='', p_name='', p_val='', regex=False, descend=False):
        nsl = PySpectreScript()
        has_descend_str = isinstance(descend, str)
        for ns in self.nsl:
            if isinstance(ns, NetlistStatement) and not has_descend_str:
                if ns._ns_match(name, master, node, p_name, p_val, regex):
                    nsl.add(ns, deep_copy=False)
            elif isinstance(ns, list) and descend:
                if has_descend_str: 
                    descend_now = NetlistStatement.compare(descend, ns[0].nodes[0], regex)
                else:
                    descend_now = descend
                if descend_now:
                    for subns in ns:
                        if subns._ns_match(name, master, node, p_name, p_val, regex):
                            nsl.add(subns, deep_copy=False)
        return nsl
 
    def replace(self, old, new):
        for ns in self.nsl:
            ns.replace(old, new)

    def change(self, key, value):
        for ns in self.nsl:
            ns.change(key, value)

    def scale(self, p_name, alpha):
        for ns in self.nsl:
            ns.scale(p_name, alpha)

    def add(self, ns, index=None, deep_copy=True):
        if isinstance(ns, str):
            ns = [NetlistStatement.from_string(ns)]
        elif isinstance(ns, PySpectreScript):
            ns = ns.nsl
        elif isinstance(ns, NetlistStatement):
            ns = [ns]
        if deep_copy:
            ns = copy.deepcopy(ns)
        if index is None:
            self.nsl.extend(ns)
        else: 
            self.nsl[index:index] = ns

    def remove(self, name='', master='', node='', p_name='', p_val='', regex=False, descend=False):
        for ns in list(self.nsl):
            if isinstance(ns, NetlistStatement):
                indices = []
                if ns._ns_match(name, master, node, p_name, p_val, regex):
                    self.nsl.remove(ns)
            elif isinstance(ns, list) and descend:
                for subns in list(ns):
                    if subns._ns_match(name, master, node, p_name, p_val, regex):
                        ns.remove(subns)
 
    def del_param(self, key):
        for ns in self.nsl:
            ns.del_param(key)

    def add_param(self, param_name, param_value):
        for ns in self.nsl:
            ns.add_param(param_name, param_value)

    ###############
    # Netlist I/O #
    ###############
    def read(self, path):
        """ Parses netlist at path into a PySpectreScript object. """
        self.path_to_script_in = path
        fin = open(path, 'r')
        self.nsl = self._read_section(fin)
        fin.close()

    def write(self, path=''):
        """ Writes the netlist contents to file."""
        if path:
            self.path_to_script_out = path
        else:
            head, tail = os.path.split(self.path_to_script_in)
            tail_split = tail.split('.')
            if len(tail_split) > 1:
                fname = '.'.join(tail_split[:-1]) + '.pys.' + tail_split[-1]
            else:
                fname = tail + '.pys.scs'
            self.path_to_script_out = os.path.join(head, fname)
        dirname = os.path.dirname(self.path_to_script_out)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        fout = open(self.path_to_script_out, 'w')
        fout.write('// Generated by PySpectre\n')
        self._write_section(fout, self.nsl)
        fout.close()

    def run(self, path_to_results='', verbose=True):
        """ Write netlist and run. """
        self.write(self.path_to_script_out)
        self.psf_results = {}
        if path_to_results:
            self.path_to_results = path_to_results
        else:
            head, tail = os.path.split(self.path_to_script_out)
            tail = tail.split('.')[0]
            self.path_to_results = os.path.join(head, 'psf', tail)
        run(self.path_to_script_out, self.path_to_results, self.command_line_args, verbose)

    def results(self, fname='', result=''):
        if not fname:
            return tuple(os.listdir(self.path_to_results))
        else:
            if not fname in self.psf_results:
                import psf
                path = os.path.join(self.path_to_results, fname)
                results = psf.PSFReader(path)
                results.open()
                self.psf_results[fname] = results
            if not result:
                return self.psf_results[fname].getValueNames()
            else:
                y = self.psf_results[fname].getValuesByName(result)
                if self.psf_results[fname].sweeps:
                    x = self.psf_results[fname].getSweepParamValues()
                    return x, y
                else:
                    return y
     
    ###################
    # Private Methods #
    ###################
    def __repr__(self):
        string_repr = ''
        for ns in self.nsl:
            if isinstance(ns, NetlistStatement):
                string_repr += repr(ns) + '\n'
            elif isinstance(ns, list):
                string_repr += repr(ns[0]) + '{...} ' + repr(ns[-1]) + '\n'
        return string_repr[:-1]  # leave off the last newline

    def __len__(self):
        return len(self.nsl)

    def __iter__(self):
        return iter(self.nsl)

    def __getitem__(self, index):
        return self.nsl[index]

    @staticmethod
    def _write_section(fout, nsl):
        """Writes netlist and subnetlists to file recursively."""
        for ns in nsl:
            if isinstance(ns, list):  # found a subnetlist
                fout.write('\n')
                # recurse to write the subnetlist
                PySpectreScript._write_section(fout, ns)
                fout.write('\n')
            elif ns.subnetlist:
                fout.write(str(ns) + ' {\n')
                PySpectreScript._write_section(fout, ns.subnetlist)
                fout.write('}\n')
            else: 
                fout.write(str(ns) + '\n')

    @staticmethod
    def _strip_conts(line, had_backslash):
        if PySpectreScript._has_backslash_continuation(line):
            line = line[:-1]
        if PySpectreScript._has_plus_cont(line, had_backslash):
            line = line[1:]
        return line

    @staticmethod
    def _has_backslash_continuation(stripped_line):
        if stripped_line:
            return stripped_line[-1] == '\\'
        else:
            return False

    @staticmethod
    def _has_plus_cont(stripped_line, had_backslash):
        # the first character can be a '+' if the line is continuing
        if stripped_line:
            return (stripped_line[0] == '+') and (not had_backslash)
        else:
            return False

    @staticmethod
    def _read_section(fin, ns_line=''):
        nsl = [] 
        had_backslash = PySpectreScript._has_backslash_continuation(ns_line)
        if had_backslash:
            ns_line = PySpectreScript._strip_conts(ns_line, had_backslash)
        for line in fin:
            stripped_line = line.split('//')[0].strip() # remove and discard commments
            split_line = stripped_line.split('=', 1)
            split_line[0] = re.sub(r'[()]', '', split_line[0]) # remove parentheses
            stripped_line = '='.join(split_line)
            ns_segment = PySpectreScript._strip_conts(stripped_line, had_backslash)
            if PySpectreScript._has_plus_cont(stripped_line, had_backslash) or had_backslash:
                ns_line += ns_segment
            else:  # start of a new statement
                if ns_line:  # if not empty
                    ns = NetlistStatement.from_string(ns_line)
                    nsl.append(ns)
                if ns_segment:
                    segment_name = ns_segment.split()[0]
                    if segment_name in ['subckt', 'section']:
                        # found start of subnetlist, step into recursion
                        sub_statements = PySpectreScript._read_section(fin, stripped_line)
                        nsl.append(sub_statements)
                    elif segment_name in ['ends', 'endsection']:
                        # found end of subnetlist
                        ns = NetlistStatement.from_string(ns_segment)
                        nsl.append(ns)
                        # step out of recursion
                        return nsl
                    elif ns_segment[-1] == '{':
                        ns = NetlistStatement.from_string(ns_segment[:-1].strip())
                        sub_statements = PySpectreScript._read_section(fin)
                        ns.subnetlist = sub_statements
                        nsl.append(ns)
                    elif ns_segment[-1] == '}':
                        return nsl
                    else:
                        # netlist statement saved, overwrite now
                        ns_line = ns_segment
                else:  # empty line and no line continuations
                    ns_line = ''
            # check for backslash continuation and save for operations on next line
            had_backslash = PySpectreScript._has_backslash_continuation(stripped_line)
        # end of file, parse last netlist statement
        if ns_line:  # if not empty
            ns = NetlistStatement.from_string(ns_line)
            nsl.append(ns)
        return nsl

def run(path, path_to_results=None, command_line_args=None, verbose=True):
    command_str = 'spectre %s ' % path
    if path_to_results:
        command_str += '-raw %s' % path_to_results
    for command in command_line_args:
        command_str += command + ' '
    if not verbose:
        command_str += ' >> ' + path + '.log'
    os.system(command_str)

def string_to_float(string):
    """ Can be used to convert a spectre string number to float.

    string_to_float(string) """
    _SCALE_FACTOR_DICT = {'P':1e15, 'T':1e12, 'G':1e9, 'M':1e6, 'K':1e3, 'k':1e3,
                          '_':1, '%':1e-2, 'c':1e-2, 'm':1e-3, 'u':1e-6, 'n':1e-9,
                          'p':1e-12, 'f':1e-15, 'a':1e-18, 'z':1e-21, 'y':1e-24}
    if (type(string) == float) or (type(string) == int): # already a float
        return float(string)
    else:
        match = re.search(r'(^[-\+\d.]+)(.?)', string) # PTGMKk_%cmunpfazyeE
        if match:
            base = float(match.group(1))
            scale_factor = match.group(2)
            if scale_factor:
                if scale_factor.lower() == 'e': # check for exponential notation
                    try:
                        return float(string)
                    except ValueError:
                        return string
                elif scale_factor in _SCALE_FACTOR_DICT:
                    return base * _SCALE_FACTOR_DICT[scale_factor] 
                else: # not a number, maybe a expression?
                    return string
            else:  # no scale factor
                return base
        else:
            return string

