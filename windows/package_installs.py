import os
import requests
import argparse
import sys
import subprocess
import shutil

sys.dont_write_bytecode = True
import boot_util
sys.dont_write_bytecode = False

myconfig = {}


def main():
    # This script is only to be run in a VENV with requests installed. It gets the Python Version and the ENV name from the ENV Variables

    global myconfig
    parsed_args = parse_arguments()
    print("******************************************")
    print("* Jupyter Integrations Python Package Setup")
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

    myconfig['req_file'] = parsed_args.req_file

    myconfig['cur_dir'] = os.path.dirname(__file__)
    myconfig['current_cwd'] = os.getcwd()


    myconfig['pyver'] = parsed_args.pyver
    if myconfig['pyver'] == 'na':
        print("\t Pyver not passed, trying to infer from PATH")
        myconfig['pyver'] = boot_util.ret_pyver()

    myconfig['env_name'] = boot_util.ret_venv()


    print(f"\t Current Working Dir: {myconfig['current_cwd']}")

    install_requirements()



def install_requirements():
    global myconfig

    print("* Install requirements")

    if myconfig['pyver'] not in myconfig['requirements']:
        print(f"\t Python config {myconfig['pyver']} not in config requirements mapping - Requirements NOT INSTALLED")
        print("")
        sys.exit(1)
    else:
        if myconfig['req_file'] == 'na':
            req_file = myconfig['requirements'][myconfig['pyver']]['req_file']
        else:
            req_file = myconfig['req_file']

        if not os.path.isfile(f"{myconfig['conf_dir']}\\requirements\\{req_file}"):
            print(f"\t Requirements file for {myconfig['pyver']} specified  ({req_file}) but does not exist in configuration directory requirements folder - requirements not installed!")
            print("")
            sys.exit(1)
        else:
            req_extra_args = myconfig['requirements'][myconfig['pyver']]['req_extra_args']


            secondary_list = myconfig['requirements'][myconfig['pyver']].get('secondary_install', [])


            with open(f"{myconfig['conf_dir']}\\requirements\\{req_file}", "r") as source, open("requirements.txt", "w") as dest:
                for line in source:
                    if line.strip() not in secondary_list:
                        dest.write(line)

            install_cmd = f"pip install {' '.join(req_extra_args)} -r requirements.txt"

            retry_cnt = 0
            retries = 3
            run_res = -1
            while run_res != 0 and retry_cnt < retries:
                retry_cnt += 1
                print(f"Try {retry_cnt} of {retries} on Main install")
                run_res = boot_util.run_install_cmd(install_cmd, title=f"Running Package Install command: {install_cmd}", cmd_remain=False)
            if run_res != 0:
                print(f"\t\t Main Package Install Failed after {retries} attempts")
                sys.exit(1)


            for pack in secondary_list:
                install_cmd = f"pip install {' '.join(req_extra_args)} {pack}"
                retry_cnt = 0
                retries = 5
                run_res = -1

                while run_res != 0 and retry_cnt < retries:
                    retry_cnt += 1
                    print(f"Try {retry_cnt} of {retries} for {pack} install")
                    run_res = boot_util.run_install_cmd(install_cmd, title=f"Running Package Install command: {install_cmd}", cmd_remain=False)
                if run_res != 0:
                    print(f"\t\t Secondary Package Install Failed after {retries} attempts on {pack}")
                    sys.exit(1)



 
def parse_arguments():
 
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_dir", type=str, help="Alternate config Dir. Default uses integrations_cfg.py in the directory integrations_config in the same directory as this script. ", default="integrations_config")
    parser.add_argument("-p", "--pyver", type=str, help="Python Version to use. Will override Config file if used. Either directories like Python310 or latest are options.", default="na")
    parser.add_argument("-r", "--req_file", type=str, help="Use non-standard requirements file (used for testing)", default="na") 
    parsed_args = parser.parse_args()
    return parsed_args
    

if __name__ == '__main__':
    main()
