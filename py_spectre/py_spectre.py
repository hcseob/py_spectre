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
        parameters: A dictionary holding all the parameters.
        subnetlist: A list of NetlistStatement objects. It is a representation
        of a sprectre subnetlist contained in curly braces.
    """
    def __init__(self, name='', nodes=None, master='', parameters=None, subnetlist=None):
        if nodes is None:
            nodes = []
        if parameters is None:
            parameters = {}
        if subnetlist is None:
            subnetlist = []
        self.name = name
        self.master = master
        self.nodes = nodes
        self.parameters = parameters
        self.subnetlist = subnetlist
            
    def __str__(self):
        string = self.name + ' '
        for node in self.nodes:
            string += node + ' '
        if self.master != '':
            string += self.master
        for param_name in self.parameters:
            param_val = self.parameters[param_name]
            string += ' ' + param_name + '=' + str(param_val)
        return string

    def __repr__(self):
        string = str(self)
        if self.subnetlist:
            string += ' { ... }'
        return string

    @staticmethod
    def _ns_match(name='', master='', node_name='', param_name='', param_value='', regex=False):
        """  Identify netlist statement with conditions. 
        
        This method will return true is there is a match for all inputs
        provided. The method supports the '*' wild card character. Regular
        expressions are supported through the regex flag. Comparison functions
        are supported for the param_value input. 
        """
        if not regex:
            name = name.replace('*', '.*?')
            master = master.replace('*', '.*?')
            node_name = node_name.replace('*', '.*?')
            param_name = param_name.replace('*', '.*?')
            param_value = param_value.replace('*', '.*?')
        match = True
        if name: match &= bool(re.match('^' + name + '$', self.name))
        if master: match &= bool(re.match('^' + master + '$', self.master))
        if node_name:
            node_match = False
            for node in self.nodes:
                node_match |= bool(re.match('^' + node_name + '$', node))
            match &= node_match
        if param_name and param_value:
            param_match = False
            for key in self.parameters:
                if re.match('^' + param_name + '$', key):
                    value = self.parameters[key]
                    if isinstance(param_value, function):
                        param_match |= param_value(string_to_float(value)) 
                    else:
                        param_match |= bool(re.match('^' + param_value + '$', value))
            match &= param_match
        elif param_name:
            param_name_match = False
            for key in self.parameters:
                param_name_match |= bool(re.match('^' + param_name + '$', key))
            match &= param_name_match
        elif param_value:
            param_value_match = False
            for value in ns.parameters.values():
                param_value_match |= bool(re.match('^' + str(param_value) + '$', value))
            match &= param_value_match
        return match

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
        master = ''
        nodes = []
        if len(split_param_list) != 1:  # if there are parameters
            # split_statement = [name, [node0, node1,...], [master], first_param]
            split_statement = split_param_list.pop(0).split()
            if len(split_statement) >= 3:  # if there is a master
                master = split_statement[-2]
            if len(split_statement) >= 4:  # if there are nodes
                nodes = split_statement[1:-2]
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
        else:  # there are no parameters and, therefore, no master
            # split_statement = [name, [node0, node1,...]]
            split_statement = ns_string.split()
            if len(split_statement) > 1:  # if there are nodes
                nodes = split_statement[1:]
        name = split_statement[0]
        return cls(name, nodes, master, parameters)

    
class PySpectreScript(object):
    def __init__(self):
        self.nsl = []
        self.command_line_args = []
        self.path_to_script = ''
        self.path_to_results = ''

    def change(self, key, value):
        for ns in self.nsl:
            if key == 'name':
                ns.name = value 
            elif key == 'master':
                ns.master = value 
            elif key in ns.nodes:
                for index, node_name in enumerate(ns.nodes): 
                    if node_name == key:
                        ns.nodes[index] = value
            elif key in ns.parameters:
                ns.parameters[key] = value

    def delete(self, key):
        for ns in self.nsl:
            if key in ns['nodes']:
                ns['nodes'].remove(key)
            elif key in ns['parameters']:
                del ns['parameters'][key]

    def add_node(self, node, index=0):
        for ns in self.nsl:
            ns['nodes'].insert(index, value)

    def add_parameter(self, param_name, param_value):
        for ns in self.nsl:
            ns['parameters'][param_name] = param_value

    def add_ns(self, ns, index=None):
        if isinstance(ns, str):
            ns = NetlistStatement.from_str(ns)
        if index is None:
            self.nsl.append(ns)
        else: 
            self.nsl.insert(index, ns)

    def query(self, name='', master='', node_name='', param_name='', param_value=''):
        nsl = PySpectreScript()
        for ns in self.nsl:
            if ns._ns_match(name, master, node_name, param_name, param_value):
                nsl.add_ns(ns)
        return nsl
           
    def __repr__(self):
        string_repr = ''
        for ns in self.nsl:
            string_repr += repr(ns) + '\n'
        return string_repr[:-1]  # leave off the last newline

    def run_script(self, path='', command_line_args=[]):
        if path:
            self.path_to_script = path
        if command_line_args:
            self.add_command_line_args(command_line_args)
        run_script(self.path_to_script, self.command_line_args)

    def read_script(self, path):
        fin = open(path, 'r')
        self.netlist = self._read_section(fin)
        fin.close()

    def write_script(self, path):
        """ Writes the netlist contents to file."""
        self.path_to_script = path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        fout = open(path, 'w')
        fout.write('// Generated by PySpectre\n')
        self._write_section(fout, self.netlist)
        fout.close()

    def add_command_line_args(self, *arg):
        self.command_line_args += arg

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
        had_backslash = False
        for line in fin:
            stripped_line = line.split('//')[0].strip() # remove and discard commments
            stripped_line = re.sub(r'[()]', '', stripped_line) # remove parentheses
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
                        # use next line just to get the name
                        first_statement = NetlistStatement.from_string(ns_segment)
                        sub_name = first_statement.nodes[0]  # subckt subckt_name
                        sub_statements = PySpectreScript._read_section(fin, ns_segment)
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

def run_script(path, command_line_args):
    command_str = 'spectre %s ' % path
    for command in command_line_args:
        command_str += command + ' '
    print command_str
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

