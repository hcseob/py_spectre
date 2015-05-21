from ordered_dict import OrderedDict
import os
import re

def read_results(path, node = '', all_results = False):
    """ Read results for spectre psfascii results files.

    Behavior is similar to cds_srr() for MATLAB. """
    if os.path.isdir(path):
        return os.listdir(path)
    elif os.path.isfile(path):
        if node or all_results:
            return _parse_all(path, node, all_results)
        else:
            return _parse_outputs(path)
    else:
        raise Exception('No results at %s.' % path)

def _parse_outputs(path):
    fin = open(path, 'r')
    preamble = _parse_preamble_sections(fin)
    if 'TRACE' in preamble:
        outputs = preamble['TRACE'].keys()
    else:
        data = _parse_point(fin, '', preamble)
        outputs = data.keys()
    fin.close()
    return outputs
        
def _parse_all(path, node, all_results):
    fin = open(path, 'r')
    preamble = _parse_preamble_sections(fin)
    if all_results:
        # all_results flag takes precedence over node value
        value = _parse_value_section(fin, '', preamble)
    else:
        value = _parse_value_section(fin, node, preamble)
    fin.close()
    return value

def _parse_preamble(path):
    fin = open(path, 'r')
    preamble = _parse_preamble_sections(fin)
    fin.close()
    return preamble

###########################
# Parse preamble sections.#
###########################

def _parse_preamble_sections(fin):
    """ Find results routing function. """
    parse_dict_sections = ['HEADER', 'TRACE']
    parse_props_sections = ['TYPE', 'SWEEP']
    end_sections = ['VALUE', 'END']
    sections = {}
    section = 'HEADER'
    while section not in end_sections:
        if section in parse_dict_sections:
            sections[section], section = _parse_props(fin)
        elif section in parse_props_sections:
            sections[section], section = _parse_props(fin)
        else:
            raise Exception('Found unrecognized section: %s.' % section)
    return sections

def _parse_dict(fin):
    end_string_list = [')', 'TYPE', 'SWEEP', 'TRACE', 'VALUE', 'END']
    dict = OrderedDict() 
    for line in fin:
        stripped_line = line.strip()
        if stripped_line in end_string_list:
            end_string = stripped_line
            return dict, end_string
        match = re.search(r'"(.+)"\s+"(.+)"', stripped_line)
        if match:
            dict[match.group(1)] = match.group(2)
    return dict, ''

def _parse_props(fin):
    end_string_list = [')', 'TYPE', 'SWEEP', 'TRACE', 'VALUE', 'END']
    props_dict = OrderedDict()
    for line in fin:
        stripped_line = line.strip()
        if stripped_line in end_string_list:  # found end of STRUCT or end of TYPE
            end_string = stripped_line
            return props_dict, end_string 
        match = re.search(r'^"(.+?)"(.*)\s(\w+)\(', stripped_line)
        if match:
            name = match.group(1)
            type = match.group(2)
            prop = match.group(3)
            if prop == 'STRUCT':  # need to recurse
                props_dict[name], _ = _parse_props(fin)
                props_dict[name]['type'] = 'STRUCT' 
            elif prop == 'PROP':
                props_dict[name], _ = _parse_dict(fin)
                props_dict[name]['type'] = type.strip()
        else:  # possibly a nonprop, key/value pair
            match = re.search(r'"(.+)"\s+"(.+)"', stripped_line)
            if match:
                props_dict[match.group(1)] = match.group(2)
    return props_dict, ''


#######################
# Parse VALUE section.#
#######################

def _parse_value_section(fin, node, preamble):
    if 'SWEEP' in preamble:
        return _parse_sweep(fin, node, preamble)
    else: 
        return _parse_point(fin, node, preamble) 

def _parse_point(fin, node, preamble):
    point = OrderedDict()
    for line in fin:
        match = re.search(r'"(.+)"\s"(.+)"\s(.+)', line)
        if match:
            net = match.group(1)
            master = match.group(2)
            value = match.group(3)
            if not node or node == net:
                point[net] = string_to_float(value) 
    return point

def _parse_sweep(fin, node, preamble):
    sweep_var = preamble['SWEEP'].keys()[0]  # only one prop key in SWEEP  
    data = {}
    # inialize the data dict
    COMPLEX_list = []
    FLOAT_list = []
    STRUCT_list = []
    STRUCT_subname_dict = {}
    STRUCT_subtype_dict = {}
    data[sweep_var] = []
    if node:
        name_list = [node]
    else:
        name_list = preamble['TRACE'].keys()
    for name in name_list:
        master = preamble['TRACE'][name]
        if master.__class__.__name__ == 'OrderedDict':
            master = master['units']
        type = preamble['TYPE'][master]['type']
        if type == 'STRUCT':
            STRUCT_list.append(name)
            STRUCT_subname_dict[name] = [key for key in preamble['TYPE'][master] if key != 'type']
            STRUCT_subtype_dict[name] = [preamble['TYPE'][master][subname]['type'] for subname in STRUCT_subname_dict[name]]
            data[name] = {}
            for key in preamble['TYPE'][master]:
                if key != 'type':
                    data[name][key] = []
        elif type == 'FLOAT DOUBLE':
            FLOAT_list.append(name)
            data[name] = []
        elif type == 'COMPLEX DOUBLE':
            COMPLEX_list.append(name)
            data[name] = []

    # parse the file
    parsing_STRUCT = False
    for line in fin:
        if parsing_STRUCT:
            value = line.strip()
            if value == ')':
                parsing_STRUCT = False
            else: 
                subname = STRUCT_subname_dict[name_STRUCT][count_STRUCT]
                type = STRUCT_subtype_dict[name_STRUCT][count_STRUCT]
                if type == 'COMPLEX DOUBLE':
                    data[name_STRUCT][subname].append(_parse_complex(value))
                elif type == 'FLOAT DOUBLE':
                    data[name_STRUCT][subname].append(string_to_float(value))
                else:
                    data[name_STRUCT][subname].append(string_to_float(value))
                count_STRUCT += 1 
        else:  # not parsing a struct
            match = re.search(r'"(.+)"\s(.+)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                if name == sweep_var:
                    data[sweep_var].append(string_to_float(value))
                elif name in FLOAT_list:
                    data[name].append(string_to_float(value))
                elif name in COMPLEX_list:
                    data[name].append(_parse_complex(value))
                elif name in STRUCT_list:
                    parsing_STRUCT = True 
                    name_STRUCT = name
                    count_STRUCT = 0
    return data


def _parse_complex(value):
    match = re.search(r'\((.+)\s(.+)\)', value)
    if match:
        real = string_to_float(match.group(1))
        imag = string_to_float(match.group(2))
        return real + imag * 1j 


###############################
# py_spectre helper functions.#
###############################
_SCALE_FACTOR_DICT = {'P':1e15, 'T':1e12, 'G':1e9, 'M':1e6, 'K':1e3, 'k':1e3,
                      '_':1, '%':1e-2, 'c':1e-2, 'm':1e-3, 'u':1e-6, 'n':1e-9,
                      'p':1e-12, 'f':1e-15, 'a':1e-18, 'z':1e-21, 'y':1e-24}
def string_to_float(string):
    """ Can be used to convert a spectre string number to float.

    string_to_float(string) """
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
