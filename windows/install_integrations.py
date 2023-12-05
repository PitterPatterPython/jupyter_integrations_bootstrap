import os
import subprocess
import argparse
import sys
sys.dont_write_bytecode = True
import boot_util
sys.dont_write_bytecode = False

myconfig = {}

def main():
    global myconfig
    
    parsed_args = parse_arguments()
    print("******************************************")
    print("* Jupyter Integrations Install Script")
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

    env_loc = myconfig['envloc']

    full_env_loc = os.path.expandvars(env_loc)

    print("********************************************")
    print("")
    if parsed_args.env_name == "-":
        env_name = input("Please enter the environment name to install to: ")
    else:
        env_name = parsed_args.env_name

    if parsed_args.pyver == 'na':
        python_ver = input("Please enter the Python Version to use, Example: Python310 or latest. (Press enter for config default): ")
    else:
        python_ver = parsed_args.pyver

    if parsed_args.req_file == 'na':
        req_file = input("Please enter the requirements file name. (It must be located in the config_dir\\requirements folder). Press Enter to use the default for the Python Version: ")
        if req_file.strip() == "":
            req_file = "na"
    else:
        req_file = "na"

    if python_ver == "":
        pyver = ""
        python_ver = "not specified"
    else:
        pyver = f"-p {python_ver}"

    print("")
    print(f"Environment Name: {env_name}")
    print(f"Python Version: {python_ver}")

    print("")

    this_env_loc = f"{full_env_loc}\\{env_name}"
    activate_script = f"{this_env_loc}\\Scripts\\activate.bat"

    myconfig['take_break'] = parsed_args.take_break

    print("")
    print("***************************************************")
    print("* Running Installation Steps")

    ######### Step one Configure the VENV 
    this_step = "Configure VENV"
    this_cmd = f"python venv_setup.py {pyver} {env_name}"
    this_num = 1

    install_step(this_step, this_cmd, this_num)

    this_step = "Install Python Packages"
    this_cmd = f"{activate_script} && python package_installs.py --req_file {req_file}"
    this_num = 2

    install_step(this_step, this_cmd, this_num)

    this_step = "Check and Configure iPython/Jupyer Directories and install Jupyter Integrations"
    this_cmd = f"{activate_script} && python jupyter_config.py"
    this_num = 3

    install_step(this_step, this_cmd, this_num)

    this_step = "Configure Startup of Integrations, Helloworlds, and Datasources (ODBC and Instance Definitions"
    this_cmd = f"{activate_script} && python org_setup.py"
    this_num = 4

    install_step(this_step, this_cmd, this_num)

    print("")
    print("")
    print("**************************************")
    print(f"* Installation of Jupyter Integrations to env {env_name} Complete")
    print("")
    pause_before_exit = input("Press Enter to Exit")
    sys.exit(0)


def install_step(step_str, step_cmd, step_num):
    global myconfig

    print(f"\t Step {step_num}: {step_str}")
    if myconfig['take_break']:
        go_on = input(f"Press Enter to {step_str}")
    run_res = boot_util.run_install_cmd(step_cmd, title=step_str, cmd_remain=False)
    if run_res != 0:
        print(f"\t\t Jupyter Installation Failure on {step_str} - Exiting")
        pause_before_exit = input("Press Enter to Exit")
        sys.exit(1)
    else:
        print(f"\t\t Install of {step_str} Successful")


def parse_arguments():
 
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env_name", type=str, help="The Environment to create (recommend using month, like jupjul, jupaug, etc)", default="-")
    parser.add_argument("-c", "--config_dir", type=str, help="Alternate config Dir. Default uses integrations_cfg.py in the directory integrations_config in the same directory as this script. ", default="integrations_config")
    parser.add_argument("-p", "--pyver", type=str, help="Python Version to use. Will override Config file if used. Either directories like Python310 or latest are options.", default="na")
    parser.add_argument("-b", "--take_break", action="store_true", help="take a break between steps in install in order to debug thing", default=False)
    parser.add_argument("-r", "--req_file", type=str, help="Use non-standard requirements file (used for testing)", default="na")
    parsed_args = parser.parse_args()
    return parsed_args
    
if __name__ == '__main__':
    main()
