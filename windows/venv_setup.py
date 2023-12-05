import os
import argparse
import sys
import subprocess
import venv
import shutil

sys.dont_write_bytecode = True
import boot_util
sys.dont_write_bytecode = False

myconfig = {}

def main():
    global myconfig
    
    parsed_args = parse_arguments()
    print("******************************************")
    print("* Jupyter Integrations VENV Creation Script")
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
    myconfig['env_name'] = parsed_args.env_name
    if parsed_args.pyver != 'na':
        myconfig['pyver'] = parsed_args.pyver

    check_pip_ini()
    check_python_ver()
    check_env_name()

    if not myconfig['silent']:
        print("*************************************************")
        print("Jupyter Integrations Parsed VENV  Variables")
        print("")
        print(f"\t SILENT Mode (-s) - {myconfig['silent']}")
        print(f"\t DEBUG  Mode (-d) - {myconfig['debug']}")
        print(f"\t OVERWRITE ENV Mode (-o) - {myconfig['overwrite']}")
        print(f"\t NO ENV INSTALL (-n) - {myconfig['no_install']}")
        print(f"\t Requested Environment Loc - {os.path.expandvars(myconfig['envloc'])}")
        print(f"\t Program Files: {os.path.expandvars(myconfig['pythoninstallloc'])}")
        print(f"\t Requested Python Version: {myconfig['pyver']}")
        print(f"\t\t Selected Python Version: {myconfig['selected_pyver']}")
        print(f"\t Requested Environment name: {myconfig['env_name']}")
        print(f"\t\t Selected Environment name: {myconfig['selected_env_name']}")
        print(f"\t Current Working directory: {myconfig['cur_dir']}")
        print("")
        print("")

    create_venv()
    copy_cfg(conf_file)

    if myconfig['no_install']:
        print(f"No Install selected - Environment {myconfig['selected_env_name']} created - Exiting now")
        sys.exit(1)

    install_requests()


def copy_cfg(conf_file):
    global myconfig
    env_dir = os.path.abspath(os.path.expandvars(myconfig['envloc']) + "\\" + myconfig['selected_env_name'])
    shutil.copy(conf_file, env_dir)

def parse_arguments():
 
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="env_name", type=str, help="The Environment to create (recommend using month, like jupjul, jupaug, etc)")
    parser.add_argument("-p", "--pyver", type=str, help="Python Version to use. Will override Config file if used. Either directories like Python310 or latest are options.", default="na")
    parser.add_argument("-c", "--config_dir", type=str, help="Alternate config Dir. Default uses integrations_cfg.py in the directory integrations_config in the same directory as this script. ", default="integrations_config")
  
    parsed_args = parser.parse_args()
    return parsed_args
 
def check_pip_ini():
    global myconfig
    user_pip = os.path.expandvars(f"%USERPROFILE%\\pip")
    user_pip_ini = f"{user_pip}\\pip.ini"

    print(f"* Checking for pip.ini in %USERPROFILE%\\pip")
    write_file = False
    if not os.path.isdir(user_pip):
        print(f"\t {user_pip} Not Found. Creating directory as well as pip.ini")
        os.mkdir(user_pip)
        write_file = True
    elif not os.path.isfile(user_pip_ini):
        print(f"\t pip directory exists but no pip.ini, creating file")
        write_file = True
    else:
        infile = open(user_pip_ini, "r")
        all_data = infile.read()
        infile.close()
        if all_data.find("user = False") < 0:
            print(f"\t {user_pip_ini} already exists, but does not include user = False ")
            print(f"\t This will cause pip issues with the VENV")
            print(f"\t We recommend adding 'user = False' to the globals section of pip.ini")
            print(f"\t You will have to manually do this so we don't alter your pip.ini")
            print(f"\t Exiting Now")
            sys.exit(1)
        else:
            print(f"\t {user_pip_ini} exists and has user = False - Continuing")

    if write_file:
        outfile = open(user_pip_ini, "w")
        outfile.write("[global]\n")
        outfile.write("user = False\n")
        outfile.close()

##########################
def check_python_ver():
# Current uses ProgramFiles ENV variable.
# TODO: Check for custom ProgramFiles if not fall back to ProgramFiles


    global myconfig

    print(f"* Checking for Python versions installed")

    check_dir = os.path.expandvars(myconfig['pythoninstallloc'])
    if not os.path.isdir(check_dir):
        print(f"Path provided for program files {check_dir} is not valid - exiting")
        sys.exit(1)
    else:
        if not myconfig['silent']:
            print(f"\t Using default Program Files Director {check_dir}")
        all_pys = []
        for x in os.listdir(check_dir):
            if x.find("Python") == 0:
                all_pys.append(x)
        sorted_pys = sorted(all_pys) # TODO Note we need to handle the weirdness here, Python310 and up is fine, but what about Python39?
        if len(sorted_pys) == 0:
            print(f"No Python Versions found in {check_dir} - Exiting")
            sys.exit(1)
        elif myconfig['pyver'] == 'latest':
            our_pyver = sorted_pys[-1]
            if not myconfig['silent']:
                print(f"\t Using latest installed version - {our_pyver}")
        elif myconfig['pyver'] in sorted_pys:
            if not myconfig['silent']:
                print(f"Found provided {myconfig['pyver']} in installed envs, using that")
                our_pyver = myconfig['pyver']
        else:
            print(f"Provided Python version {myconfig['pyver']} not found in Python Install Location ({check_dir}) - Exiting")
            sys.exit(1)
    myconfig['selected_pyver'] = our_pyver

def check_env_name():
    global myconfig

    print("* Checking Enviroment Name")

    env_root = os.path.expandvars(myconfig['envloc'])
    if not os.path.isdir(env_root):
        print(f"\t ENV location {env_root} does not exist - Attempting to Create")
        print(f"\t If Creation fails we will exit")
        try:
            os.mkdir(env_root)
        except Exception as e:
            print(f"\t ENV directory creation failed with {str(e)} - Exiting")
            sys.exit(1)
    all_envs = []
    for x in os.listdir(env_root):
        all_envs.append(x)
    if myconfig['env_name'] in all_envs and not myconfig['overwrite']:
        print(f"\t Requested Enviroment name {myconfig['env_name']} already exists in {myconfig['envloc']} - Exiting")
        sys.exit(1)
    elif myconfig['env_name'] in all_envs and myconfig['overwrite']:
        print(f"\t ENV {myconfig['env_name']} exists, but -o selected *** WARNING WILL OVERWRITE ***")
    else:
        print(f"\t ENV {myconfig['env_name']} doesn't exist -> Using for New Environment")
    myconfig['selected_env_name'] = myconfig['env_name']

def create_venv():
    global myconfig

    print("* Creating Virtual Environment")
    env_dir = os.path.abspath(os.path.expandvars(myconfig['envloc']) + "\\" + myconfig['selected_env_name'])
    venv.create(env_dir, system_site_packages=False, clear=True, with_pip=True, prompt=None, upgrade_deps=False)


def install_requests():
    global myconfig

    print(f"* Installing Requests in New Environment")

    envs_path = os.path.expandvars(myconfig['envloc'])
    env_path = f"{envs_path}\\{myconfig['selected_env_name']}"

    activate_cmd = f"{env_path}\\Scripts\\activate.bat"
    install_cmd = f"pip install requests"
    full_command = f"{activate_cmd} && {install_cmd}"
    

    retry_cnt = 0
    retries = 3
    run_res = -1
    while run_res != 0 and retry_cnt < retries: 
        retry_cnt += 1
        print(f"Try {retry_cnt} of {retries}")
        run_res = boot_util.run_install_cmd(full_command, title="Installing Requests in new VENV", cmd_remain=False)

    if run_res != 0:
        print(f"\t\t Requests Install Failed after {retries} attempts")
        sys.exit(1)

if __name__ == '__main__':
    main()
