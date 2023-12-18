import os
import json
import sys
import subprocess
import shutil
import zipfile

def main():
    print("No need to run this direct. Include as a module with import boot_util")


def run_install_cmd(inst_command, title=None, raw_args=False, cmd_remain=False):


    if raw_args:
        run_args = inst_command
    else:
        run_args = ['cmd']
        if cmd_remain:
            run_args.append("/K")
        else:
            run_args.append("/C")
        run_args.append(inst_command)

    if title is None:
        title = f"Running {inst_command}"
    print(f"\t {title}")
    out_proc = subprocess.run(run_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    inst_code = out_proc.returncode
    if inst_code == 0:
        print(f"\t\t {title} run success")
    else:
        print(f"\t\t Error running {title} - Error Code: {inst_code}")
        out_out = out_proc.stdout.decode('utf-8', errors='replace')
        out_err = out_proc.stderr.decode('utf-8', errors='replace')
        print(f"\t\t\t Std out: {out_out}")
        print(f"\t\t\t Std err: {out_err}")
    return inst_code


def download_unzip_pip_install_repo(repo_name, repo_url, myproxies, rmdir=True, add_cmd=None):
    import requests

    print("")
    print(f"\t Downloading and PIP Installing {repo_name}\n\t\t {repo_url}")

    output = f"{repo_name}.zip"

    inst_dir = "cur_repo_install"

    requests.packages.urllib3.disable_warnings()

    print(f"\t\t Downloading")
    r = requests.get(repo_url, proxies=myproxies, verify=False)
    zip_content = r.content

    with open(output, 'wb') as f:
        f.write(zip_content)
    print(f"\t\t Unzipping")
    with zipfile.ZipFile(output, 'r') as zip_ref:
        zip_ref.extractall(inst_dir)
    print(f"\t\t Removing Zip")
    os.remove(output)

    subfolders = [f.path for f in os.scandir(inst_dir) if f.is_dir() and f.name.find(repo_name) >= 0]
    repo_base = subfolders[0].split('\\')[1]
    install_cmd = f"cd {inst_dir} && cd {repo_base} && pip install --upgrade --force-reinstall ."
    inst_code = 0
    inst_add_code = 0

    isnt_code = run_install_cmd(install_cmd, title=f"\t Installing repo {repo_name}", cmd_remain=False)

    if inst_code == 0 and add_cmd is not None:
        add_install_cmd = f"cd {inst_dir} && cd {repo_base} && {add_cmd}"
        isnt_add_code = run_install_cmd(add_install_cmd, title=f"\t\t Running addtional cmd {add_install_cmd} for repo {repo_name}", cmd_remain=False)

    if rmdir:
        print("\t\t Removing Installation Directory")
        shutil.rmtree(inst_dir)
    if inst_code == 0 and inst_add_code == 0:
        return 0
    else:
        return 1


def download_unzip_install_repo(repo_name, repo_url, myproxies, rmdir=True, add_cmd=None):
    import requests

    print("")
    print(f"\t Downloading and Installing {repo_name}\n\t\t {repo_url}")

    output = f"{repo_name}.zip"

    inst_dir = "cur_repo_install"

    requests.packages.urllib3.disable_warnings()

    print(f"\t\t Downloading")
    r = requests.get(repo_url, proxies=myproxies, verify=False)
    zip_content = r.content

    with open(output, 'wb') as f:
        f.write(zip_content)
    print(f"\t\t Unzipping")
    with zipfile.ZipFile(output, 'r') as zip_ref:
        zip_ref.extractall(inst_dir)
    print(f"\t\t Removing Zip")
    os.remove(output)

    subfolders = [f.path for f in os.scandir(inst_dir) if f.is_dir() and f.name.find(repo_name) >= 0]
    repo_base = subfolders[0].split('\\')[1]
    install_cmd = f"cd {inst_dir} && cd {repo_base} && python setup.py install"
    inst_code = 0
    inst_add_code = 0

    isnt_code = run_install_cmd(install_cmd, title=f"\t Installing repo {repo_name}", cmd_remain=False)

    if inst_code == 0 and add_cmd is not None:
        add_install_cmd = f"cd {inst_dir} && cd {repo_base} && {add_cmd}"
        isnt_add_code = run_install_cmd(add_install_cmd, title=f"\t\t Running addtional cmd {add_install_cmd} for repo {repo_name}", cmd_remain=False)

    if rmdir:
        print("\t\t Removing Installation Directory")
        shutil.rmtree(inst_dir)
    if inst_code == 0 and inst_add_code == 0:
        return 0
    else:
        return 1

def load_json_config(file_loc="integrations_cfg.py"):

    if not os.path.isfile(file_loc):
        print(f"File {file_loc} does not exist or is not a file. JSON not loaded")
        return None
    f = open(file_loc, "r")
    raw_cfg = f.read()
    f.close()
    cleaned_cfg = ""
    for line in raw_cfg.split("\n"):
        if line.strip().find("#") == 0 or line.strip() == "":
           pass
        else:
            cleaned_cfg += line + "\n"
    try:
        json_cfg = json.loads(cleaned_cfg)

    except Exception as e:
        except_out = str(e)
        print(f"Unable to parse JSON in {file_loc}")
        print(f"Exception: {except_out}")

        if except_out.find(' line '):
            linestart = except_out.find( ' line ')
            colstart = except_out.find(' column ')
            line_num = except_out[linestart:colstart].replace(' line ', '')
            int_line_num = int(line_num)
            ar_cleaned_cfg = cleaned_cfg.split("\n")
            if int_line_num > 1:
                startline = int_line_num - 2
            else:
                startline = 0

            if int_line_num + 1 >= len(ar_cleaned_cfg) - 1:
                endline = None
            else:
                endline = int_line_num + 1
            lines_out = "\n".join(ar_cleaned_cfg[startline:endline])

            print(f"Possible lines of issue are:\n{lines_out}")

        sys.exit(1)

        json_cfg = None

    return json_cfg

def ret_pyver():

    full_path = os.environ['PATH']

    p_items = full_path.split(";")
    for x in p_items:
        if x.find(r"C:\Program Files\Python") == 0:
            for i in x.split("\\"):
                if i.find("Python") == 0:
                    pyver = i
                    break
    return pyver

def ret_venv():
    venv = os.environ['VIRTUAL_ENV']
    return venv.split("\\")[-1]


if __name__ == '__main__':
    main()
