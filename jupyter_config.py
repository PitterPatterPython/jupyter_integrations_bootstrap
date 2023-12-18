import os
import requests
import argparse
import sys
import subprocess
import venv

sys.dont_write_bytecode = True
import boot_util
sys.dont_write_bytecode = False

myconfig = {}


def main():
    global myconfig
    parsed_args = parse_arguments()
    print("******************************************")
    print("* Jupyter Integrations Base Jupyter configuration and integrations install")
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
   
    ipython_setup()
    jupyter_setup()
    integrations_install()

def parse_arguments():
 
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_dir", type=str, help="Alternate config Dir. Default uses integrations_cfg.py in the directory integrations_config in the same directory as this script. ", default="integrations_config")
    parsed_args = parser.parse_args()
    return parsed_args  


def integrations_install():
    global myconfig
    
    print("")
    print("* Installing all repos from 'install_integrations' in config")
    
    for this_repo in myconfig["install_integrations"]:
        print(f"\t Installing Repo {this_repo}")
        this_url = myconfig['repos'][this_repo]['repo']
        this_type = myconfig['repos'][this_repo]['type']
        this_add_cmd = myconfig['repos'][this_repo].get('add_cmd', None)
        if this_add_cmd is not None:
            print(f"\t Extra Add Command: {this_add_cmd}")

        if this_type == 'zip':
            res = boot_util.download_unzip_install_repo(this_repo, this_url, myconfig['proxies'], rmdir=True, add_cmd=this_add_cmd)
        elif this_type == 'zip_pip':
            res = boot_util.download_unzip_pip_install_repo(this_repo, this_url, myconfig['proxies'], rmdir=True, add_cmd=this_add_cmd)
        else:
            print(f"Error: Unknown install type: {this_type}")
            res = 1

        if res == 0:
            print(f"\t\t Install Successful")
        else:
            print(f"\t\t ***** Install of {this_repo} failed")

def jupyter_setup():

    # TODO: Maybe make a way to check for non commented items and or add more via config. 
    global myconfig
    print("")
    print(f"* Setup for .jupyter folder in userprofile and config")


    user_profile_path = os.path.expandvars(f"%USERPROFILE%")
    jupyter_path = f"{user_profile_path}\\.jupyter"   

    if not os.path.isdir(jupyter_path):
        subprocess.run(['jupyter', 'lab', '--generate-config'])
    
    
    jup_conf_file = f"{jupyter_path}\\jupyter_lab_config.py"    
    f = open(jup_conf_file, "r")
    in_data = f.read()
    f.close()
    out_data = ""
    for line in in_data.split("\n"):
        if line == "# c.ServerApp.open_browser = False":
            if myconfig['open_browser']:
                out_data += "c.ServerApp.open_browser = True" + "\n"
            else:
                out_data += line + "\n"
        else:
            out_data += line + "\n"
    f = open(jup_conf_file, "w")
    f.write(out_data)
    f.close()
    


def ipython_setup():
    # TODO Add a way for to add certs 
    global myconfig
    print("")
    print(f"* Setup for .ipython folder in userprofile")
    
    user_profile_path = os.path.expandvars(f"%USERPROFILE%")
    ipython_path = f"{user_profile_path}\\.ipython"
    
    if not os.path.isdir(ipython_path):
        if not myconfig['silent']:
            print(f"\t .ipython folder not found in user profile. Running ipython profile create")
        subprocess.run(['ipython', 'profile', 'create'])
    if not myconfig['silent']:
        print(f"\t Checking for Subdirs in .ipython for Jupyter Integrations - Creating if not existing")
        
    ipython_dirs = ['certs', 'integrations', 'integrations_install']
    for i_dir in ipython_dirs:
        if not os.path.isdir(f"{ipython_path}\\{i_dir}"):
            if not myconfig['silent']:
                print(f"\t\t.ipython subdir {i_dir} not found - Creating")
            os.mkdir(f"{ipython_path}\\{i_dir}")
        else:
            if not myconfig['silent']:
                print(f"\t\t.ipython subdir {i_dir} - Found!")
    


if __name__ == '__main__':
    main()
