import os
import subprocess
import zipfile
import getpass
import sys
import shutil

######### Change These Settings

# Proxies, please set proxies if you need to reach out to github and your org requires proxies
# If you don't require a explicit proxy, please set to None

proxies = None
# proxies = {"http": "http://proxy.myorg.com:8080",
#            "https": "http://proxy.myorg.com:8080"}


##########
# Disable SSL warnings
disable_ssl_warn = True

##########
# The name of the temp directory to do the install from. You shouldn't need to change this.
boot_dir = "jupyter_bootstrap"


#######
# The Name of the bootstrap repo
# It is recommended to use the bootstrap at PitterPatterPython
#
# for boot auth, you can provide None which will not attempt to authenticate
# or you can provide git_enterprise_username where it will use the os.ENVIRON['USERNAME'] as the user and attempt to authenticate to a github enterprise system
# If you need a custom auth, you have to create a function that updates the requests session variable like the the git_enterprise_auth function does

boot_loc = "https://github.com/PitterPatterPython/jupyter_integrations_bootstrap/archive/refs/heads/main.zip"
boot_auth = None
boot_use_proxy = False
#######
# The Name of the config location
# You can host your config on an internal git location (recommended) Please don't host on a public git repo. That's bad practice and you should be ashamed if you do this.
# Less ideally you can host it on a shared drive.
#
# If your config_loc starts with http, we will assume it's a git location file download and pull it locally If it does not start with that we will assume file share
#
# for config auth, you can provide None which will not attempt to authenticate
# or you can provide git_enterprise_username where it will use the os.ENVIRON['USERNAME'] as the user and attempt to authenticate to a github enterprise system
# If you need a custom auth, you have to create a function that updates the requests session variable like the the git_enterprise_auth function does

config_loc = "https://github.myorg.com/mygituser/myteam_jupyter_bootstrap_config/archive/refs/heads/main.zip"

config_auth = None
#config_auth = "git_enterprise_username"
config_use_proxy = False
# config_loc = r"\\myfileserver\myshare\mylocation\myteam_jupyter_bootstrap_config"  # Use this if you have an extracted config. This directory should have the integrations_cfg.py in it
# config_loc = r"\\myfileserver\myshare\mylocation\myteam_jupyter_bootstrap_config\config.zip" # If the file ends in .zip we will copy it down and then extract it


#####################################################
# End Config - Now check for Requests

try:
    import requests
    print(f"Checking for request module: Requests installed successfully!")
except:
    print("****************************************")
    print("Python Requests not currently installed. We will install it and exit.")
    print("")
    print("When this script exits... rerunning it should allow you to continue")
    outstr = input("Press Enter to Continue")
    out_res = subprocess.run(['pip', 'install', '--user', 'requests'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    inst_code = out_res.returncode

    if inst_code == 0:
        print("Requests Install is Successful")
        print("Please rerun install script to install")
        out_2 = input("Press Enter to Continue")
        sys.exit(0)
    else:
        print(f"Request install returned with an error: {inst_code}")
        print(f"You will want to manually check requests")
        print("")

        out_out = out_res.stdout.decode('utf-8', errors='replace')
        out_err = out_res.stderr.decode('utf-8', errors='replace')

        print(f"Std Out: {out_out}")
        print("")
        print(f"Std err: {out_err}")
        print("")
        out_2 = input("Press Enter to Continue")
        sys.exit(1)




def main():
    global boot_dir

    global boot_loc
    global boot_auth
    global boot_use_proxy

    global config_loc
    global config_auth
    global config_use_proxy

    boot_repo_dir = f"{boot_dir}\\jupyter_integrations_bootstrap-main\\windows"
    config_repo_dir = f"{boot_dir}\\ecrimepd_bootstrap_config-main"


    # Check for python requests. The base level of what we need to install.


    if not os.path.isdir(boot_dir):
        os.mkdir(boot_dir)
    else:
        print("The base bootstrap directory already seems to exist. We'd recommend deleting this.  We can remove it for you")
        remove_dir = input("Do you want us to remove the directory? (Y/N): ")
        if remove_dir.lower() == "y":
            shutil.rmtree(boot_dir)
            os.mkdir(boot_dir)
        else:
            print(f"You didn't select 'Y' - so we didn't delete the {boot_dir} directory. You should manually do this - exiting now")
            blah = input("Press Enter to Exit")
            sys.exit(1)

# Get Bootstrap
    print(f"\tGetting Bootstrap")
    download_and_unzip(boot_loc, boot_dir, use_proxy=boot_use_proxy, auth=boot_auth)

    if os.path.isdir(f"{boot_repo_dir}\\integrations_config"):
        print(f"\t Previous config exists, removing - This is weird")
        shutil.rmtree(f"{boot_repo_dir}\\integrations_config")


# Get Config
    print("\t Getting Config")
    download_and_unzip(config_loc, boot_dir, use_proxy=config_use_proxy, auth=config_auth)

    print("\t Moving config into bootstrap folder")
    shutil.move(config_repo_dir, f"{boot_repo_dir}\\integrations_config")

    print("\t Copying start script (run_integrations.py) to Desktop")
    desktop_dir = os.path.expandvars("%USERPROFILE%\\Desktop")
    shutil.copy(f"{boot_repo_dir}\\run_integrations.py", desktop_dir)

    print("\t Running installation")
    run_res = subprocess.run(['cmd', '/C', f"cd {boot_repo_dir} && python install_integrations.py"])


    print("****** Removing bootstrap Installation")
    shutil.rmtree(boot_dir)
    out_1 = input("Press Enter to Continue")


def download_and_unzip(loc, out_loc, use_proxy=False, auth=None):

    src_type = None
    if loc.find("http") == 0:
        #this is repo
        src_type = "repo"
        src_ftype = "zip"
    else:
        src_type = "file"
        if loc.find(".zip") >= 0:
            src_ftype = "zip"
        else:
            src_ftype = "dir"

    if src_type == "repo":
        repo_download(loc, "temp.zip", use_proxy=use_proxy, auth=auth)

    if src_ftype == "zip":
        print(f"\t Unzipping")
        with zipfile.ZipFile("temp.zip", "r") as zip_ref:
            zip_ref.extractall(out_loc)
        print(f"\t Removing Zip")
        os.remove("temp.zip")
    elif src_ftype == "dir":
        print(f"\t Pulling file location local")
        shutil.copytree(loc, out_loc)

def repo_download(url, zip_fname, use_proxy=False, auth=None):
    global proxies
    global disable_ssl_warn

    status = False

    if disable_ssl_warn:
        requests.packages.urllib3.disable_warnings()
        ssl_verify = False
    else:
        ssl_verify = True

    s = requests.Session()
    s.verify = ssl_verify

    if use_proxy and proxies is not None:
        s.proxies = proxies

    if auth is None:
        pass
    elif auth == "git_enterprise_username":
        thisusername = os.environ['USERNAME']
        s = git_enterprise_auth(url, thisusername, s)
    else:
        print(f"The auth specified {auth} isn't known. Please define a function that updates the requests.Session object to auth to your source (an admin may have to do this for you)")
        s = None

    if s is not None:
        r = s.get(url)
        zip_content = r.content
        with open(zip_fname, 'wb') as f:
            f.write(zip_content)
        status = True

    return status

def git_enterprise_auth(url, myusername, src_s):

    s = src_s
    print(f"\t Authenticating to git enterprise")

    temp_split = url.split(r"//")
    scheme = temp_split[0].strip()
    temp_split2 = temp_split[1].split(r"/")
    domain = temp_split2[0].strip()

    base_link = f"{scheme}//{domain}"
    print(f"Base URL: {base_link}")

    r1 = s.get(f"{base_link}/login")
    print(r1.status_code)
    #print(r1.text)
    str_text = r1.text
    iloc = str_text.find('authenticity_token" value="')
    filt_text = str_text[iloc:]
    split_text = filt_text.split('"')

    auth_token = split_text[2]

    print(f"User: {myusername}")
    pwd = getpass.getpass("Please enter your password: ")

    data = {'login': myusername, 'password': pwd, 'authenticity_token': auth_token}
    # Maybe check here?
    r2 = s.post(f"{base_link}/session", data=data)
    if r2.status_code != 200:
        print("Error Authenticating")
        s = None
    return s

if __name__ == '__main__':
    main()
