import os
import requests
import argparse
import sys
import subprocess
import shutil
import zipfile
import codecs

sys.dont_write_bytecode = True
import boot_util
sys.dont_write_bytecode = False

myconfig = {}

def main():
    global myconfig
    parsed_args = parse_arguments()
    print("******************************************")
    print("* Jupyter Integrations Organization Specific Installs")
    print(f"\t Integrations Config Directory: {parsed_args.config_dir}")
    print("")
    
    conf_dir = parsed_args.config_dir
    conf_file = f"{os.path.expandvars(conf_dir)}\\integrations_cfg.py"

    if not os.path.isfile(conf_file):
        print(f"*** Warning = Config File (integrations_cfg.py) not found at {conf_dir}")
        print(f"\t You may need to change the integrations_cfg_template.py to integrations_cfg.py in {conf_dir}")
        print(f"\t You also may need to specify your configuration directory with -c")
        print(f"*** Exiting")
        sys.exit(1)

    myconfig = boot_util.load_json_config(file_loc=conf_file)

    if myconfig is None:
        print(f"*** Config File Not loaded - Exiting")
        sys.exit(1)
    
    myconfig['conf_dir'] = conf_dir
    myconfig['conf_file'] = conf_file


    myconfig['cur_dir'] = os.path.dirname(__file__)
    myconfig['current_cwd'] = os.getcwd()
    myconfig['pyver'] = boot_util.ret_pyver()
    myconfig['env_name'] = boot_util.ret_venv()
    myconfig['myuser'] = os.environ['USERNAME'].lower()
    myconfig['u_groups'] = get_config_groups()
    myconfig['profile_startup_loc'] = os.path.expandvars(f"%USERPROFILE%\\.ipython\\profile_default\\startup")
    
    
    clear_startup()
    write_base_ipy()
    write_helloworld()
    write_integration_startups()
    write_env_imports()
    write_odbc_configs()

    #print(f"Current Working Dir: {current_cwd}")


def write_odbc_configs():
    global myconfig

    print("")
    print("* Writing ODBC Config")

    data_source_file = os.path.expandvars(myconfig['data_source_loc'])
    custom_data_source_file = os.path.expandvars(myconfig['custom_data_source_loc'])

    odbc_dir = f"{myconfig['conf_dir']}\\ODBC"

    if not os.path.isdir(odbc_dir):
        print("\t ODBC Config Directory {odbc_dir} does not exist")
        return None
    for odbc_file in os.listdir(odbc_dir):
        if odbc_file.find(".reg") > 0:
            print(f"\t Processing file {odbc_file} as ODBC Template File")
            with codecs.open(f"{odbc_dir}\\{odbc_file}", encoding='utf-16') as in_reg:
                this_data = in_reg.read()
            for odbc_var in myconfig['odbc_vars'].keys():
                if this_data.find(odbc_val) >= 0:
                    replace_val = myconfig['odbc_vars'][odbc_var]
                    if isinstance(replace_val, str):
                        if replace_val.find('%') >= 0:
                            replace_val = os.path.expandvars(replace_val)
                    elif isinstance(replace_val, dict):
                        r_type = replace_val.get("type", "")
                        r_value = replace_val.get("value", "")
                        if r_type == "dir_max":
                            my_dir = r_value
                            if os.path.isdir(my_dir):
                                replace_val = max(os.listdir(my_dir))
                            else:
                                print(f"Provided Path does not exist {mydir} - Using name of odbc_val {odbc_val}")
                                replace_val = odbc_val
                        else:
                            print(f"Warning: r_type {r_type} not functional. Not setting odbc_val (going to use name of {odbc_val}")
                            replace_val = odbc_val
                    this_data = this_data.replace(odbc_var, replace_val)
            with codecs.open(odbc_file, 'w', encoding='utf-16') as out_reg:
                out_reg.write(this_data)

            run_res = boot_util.run_install_cmd(['reg', 'import', odbc_file], title=f"ODBC Import {odbc_file}", raw_args=True, cmd_remain=False)
            if run_res == 0:
                pass
            else:
                print(f"\t\t\t Error importing {odbc_file}")
            os.remove(odbc_file)

    
def write_env_imports():
    global myconfig

    print("")
    print("* Writing ENV Files for loading")

    data_source_file = os.path.expandvars(myconfig['data_source_loc'])
    custom_data_source_file = os.path.expandvars(myconfig['custom_data_source_loc'])

    global_base_data = f":: Global Settings from config env_sources base.env\n\n"

    # Load the "global" items from base.env. This should be proxy Info, shared locations etc. No data sources here. 
    print(f"\t Writing team data sources {myconfig['data_source_loc']}")
    f = open(f"{myconfig['conf_dir']}\\env_sources\\base.env", "r")
    base_data = f.read()
    f.close()
    global_base_data += base_data + "\n\n"


    # Check for global data sources in data_sources.env These get writtend next. If one isn't created, we create it at this time from a template. 
    global_ds_data = ":: Global Data sources from config env_sources data_sources.env\n\n"

    if not os.path.isfile(f"{myconfig['conf_dir']}\\env_sources\\data_sources.env"):
        print("\t\t data_sources.env not created. Copying template at example_data_sources.env")
        f = open(f"{myconfig['conf_dir']}\\env_sources\\example_data_sources.env", "r")
        ds_data = f.read()
        f.close()
        f = open(f"{myconfig['conf_dir']}\\env_sources\\data_sources.env", "w")
        f.write(ds_data)
        f.close()
    else:
        f = open(f"{myconfig['conf_dir']}\\env_sources\\data_sources.env", "r")
        ds_data = f.read()
        f.close()

    global_ds_data += ds_data + "\n\n"

    # Next step, look for any data source files (data_sources.env) with a prepended group name. 
    # We ignore all, but we check for each group a user is in. If there is a specified name like team1, and team1_data_sources.env exists we append that AFTER the global data source. 
    # This allows us to overwrite global data_sources.env with customized team specific data. 
    team_ds_data = ":: User Group Data Source data if specified\n\n"


    if len(myconfig['u_groups']) == 1 and myconfig['u_groups'][0] == 'all':
        print(f"\t User {myconfing['myuser']} is not in any config group. Using standard no additional datasources specified")
    elif len(myconfig['u_groups']) >= 2:
        the_groups  = [x for x in myconfig['u_groups'] if x != 'all']

        for x in the_groups:
            test_ds_file = f"{myconfig['conf_dir']}\\env_sources\\{x}_data_sources.env"
            if not os.path.isfile(test_ds_file):
                print(f"\t Group {x} does not have dedicated data source file")
                team_ds_data += f":: No team data source data for {x}\n\n"
            else:
                f = open(f"{myconfig['conf_dir']}\\env_sources\\{x}_data_sources.env", "r")
                this_ds_data = f.read()
                f.close()
                team_ds_data += f"::Team {x} Data Source Data\n\n{this_ds_data}\n\n"
                this_ds_data = None


    # Now we write all the data
    f = open(data_source_file, "w")
    f.write(global_base_data + "\n" + global_ds_data + "\n" + team_ds_data)
    f.close()



# Done every time for every group
    print(f"\t Checking Custom Data Source File")
    if os.path.isfile(custom_data_source_file):
        print(f"\t\t Custom Data Source already exists at {custom_data_source_file}")
    else:
        print(f"\t\t No Custom Data Source: Creating template at {custom_data_source_file}")
        f = open(f"{myconfig['conf_dir']}\\env_sources\\example_custom_data_sources.env", "r")
        cust_ds_data = f.read()
        f.close()
        f = open(custom_data_source_file, "w")
        f.write(cust_ds_data)
        f.close()
        

    

def write_integration_startups():
    global myconfig
    dir_loc =  myconfig['profile_startup_loc']
    
    print("")
    print("* Writing objects for integrations")
    
    start_idx = 20

    for integ in myconfig['install_integrations']:
        if len([x for x in myconfig['u_groups'] if x in myconfig['repos'][integ]['groups'] ]) > 0:
            fname = f"{str(start_idx)}_{integ.replace('jupyter_', '')}.py"
            fdata = ret_standard_obj_inst(integ)
            print(f"\t writing startup files for {integ} at {fname}")           
            write_res = write_startup(dir_loc, fname, fdata)
            start_idx += 1
            
        
 

def ret_standard_obj_inst(integ):

    int_str = integ.replace("jupyter_", "")
    
    ret_str = f"""# Integrations are loaded as base items first for speed
from {int_str}_core.{int_str}_base import {int_str.capitalize()}
{int_str}_base = {int_str.capitalize()}({myconfig['integrations_obj_vars']})
ipy.register_magics({int_str}_base)
"""
    return ret_str

def write_helloworld():
    global myconfig
    dir_loc =  myconfig['profile_startup_loc']

    print("")
    print("* Writing Helloworld scripts based on group membership")

    if len(myconfig['u_groups']) == 1 and myconfig['u_groups'][0] == 'all':
        print(f"\t User {myconfing['myuser']} is not in any config group. Using standard helloworld")
    elif len(myconfig['u_groups']) >= 2:
        the_groups  = [x for x in myconfig['u_groups'] if x != 'all']
        if len(the_groups) == 1:
            #the_groups[0]
            print(f"\t Using {the_groups[0]} for Helloworld")
        elif len(the_groups) > 1:
            print(f"\t User {myconfig['myuser']} is in more than one group (excluding 'all'): ({the_groups}).")
            print(f"\t\t We will use the first group that they have a helloworld file for, but it may have unexpected side affects")

        else:
            print(f"\t Weird: {the_groups}")
        helloworld_file = None
        for x in the_groups:
            test_helloworld_file = f"{myconfig['conf_dir']}\\helloworlds\\{x}_helloworld.py"
            if not os.path.isfile(test_helloworld_file):
                print(f"\t Group {x} does not have dedicated helloworld")
            else:
                helloworld_file = test_helloworld_file
                print(f"\t Using {helloworld_file} for custom helloworld")
        if helloworld_file is not None:
            f = open(helloworld_file, "r")
            helloworld_data = f.read()
            f.close()
            write_res = write_startup(dir_loc, "05_helloworlds.py", helloworld_data)

    print("")
    print("* Writing Helloworld Object Instantiation")

    h_data = f"""# Helloworld is loaded as Full on every load
from helloworld_core.helloworld_full import Helloworld
helloworld_full = Helloworld({myconfig['integrations_obj_vars']})
ipy.register_magics(helloworld_full)
"""

    write_res = write_startup(dir_loc, "10_helloworld.py", h_data)


def clear_startup():
    global myconfig
    dir_loc =  myconfig['profile_startup_loc']
    
    print("")
    print("* Clearing startup location items")

    for x in os.listdir(dir_loc):
        
        try:
            valchk = x.split("_")[0]
            valchk = int(valchk)
            os.remove(f"{dir_loc}\\{x}")
        except:
            pass

def write_base_ipy():
    global myconfig
    dir_loc =  myconfig['profile_startup_loc']
    
    print("")
    print("* Writing Base ipy config")
    
    fname = "01_ipy.py"
    fdata = """# Basic Imports for everyone

ipy = get_ipython()
import pandas as pd

hello_go = \"\"\"# %helloworld will get you basic help and where to start"
%helloworld
\"\"\"
"""
    write_res = write_startup(dir_loc, fname, fdata)
            

def write_startup(dir_loc, file_name, file_data):

    file_order = file_name.split("_")[0]
    try:
        file_order = int(file_order)
    except:
        print(f"File order did not cast to int - bad")
        return False
    
    f = open(f"{dir_loc}\\{file_name}", 'w')
    f.write(file_data)
    f.close()
    
    return True
    
    
def get_config_groups():
    global myconfig
    
    all_groups = myconfig['user_groups']
    
    rev_groups = {}
    
    for g in all_groups.keys():
        for u in all_groups[g]:
            if u.lower() in rev_groups:
                rev_groups[u.lower()].append(g)
                rev_groups[u.lower()] = list(set(rev_groups[u.lower()]))
            else:
                rev_groups[u.lower()] = ['all', g]
    return rev_groups[myconfig['myuser'].lower()]

    
def parse_arguments():
 
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_dir", type=str, help="Alternate config Dir. Default uses integrations_cfg.py in the directory integrations_config in the same directory as this script. ", default="integrations_config")
    parsed_args = parser.parse_args()
    return parsed_args  



if __name__ == '__main__':
    main()
