import os
import datetime
import subprocess
def main():
    env_dir = "%USERPROFILE%\\PythonENVs"
    full_env_dir = os.path.expandvars(env_dir)
    data_source_file =  os.path.expandvars("%USERPROFILE%\\jupyter_data_sources.bat")
    custom_data_source_file = os.path.expandvars("%USERPROFILE%\\jupyter_data_sources_custom.bat")

    env_list = get_env_list(full_env_dir)

#    sorted_envs = sorted(env_list, reverse=True)

    sorted_envs = {k: v for k, v in sorted(env_list.items(), key=lambda item: item[1], reverse=True)}

#    print("index\tenv name\tlast modified")
    print(f"{'index':<8}{'env name':<14}{'last modified':<20}")
    print("-----------------------------------------------")
    myidx = 1
    envlist = ["dummy"]
    for k in sorted_envs:
        myindex= str(myidx)
        envlist.append(k)
        myname = k
        mylm = datetime.datetime.fromtimestamp(int(env_list[k])).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{myindex:<8}{myname:<14}{mylm:<20}")
#        print(f"{str(myidx)}\t{k}\t\t{datetime.datetime.fromtimestamp(int(env_list[k])).strftime('%Y-%m-%d %H:%M:%S')}")
        myidx += 1

    print("")
    print("")

    if len(sorted_envs) >= 5:
        print(f"Note: You have {len(sorted_envs)} environments defined. We recommend cleaning environments by removing older ENVs")
        print("")
        print(f"This can be done by going to {full_env_dir} and deleting any older environments")
        print("")

    run_idx = input("Enter Index of Environment you wish to run or hit enter for the latest: ")
    if run_idx == "":
        run_idx = 1
    else:
        run_idx = int(run_idx)

    env_name = envlist[run_idx]
    print(f"You want to run item {run_idx}")

    createddm = datetime.datetime.fromtimestamp(int(sorted_envs[env_name])).strftime('%Y-%m-%d %H:%M:%S')
    print(f"ENV {env_name} - Last Modified {createddm}")

    user_profile = os.path.expandvars("%USERPROFILE%")
    env_path = f"{full_env_dir}\\{env_name}"
    activate_cmd = f"{env_path}\\Scripts\\activate"
    cd_cmd = f"cd {user_profile}"
    env_cmds = f"call {data_source_file} && call {custom_data_source_file}"
    jupyter_cmd = f"jupyter lab"

    full_command = f"{activate_cmd} && {cd_cmd} && {env_cmds} && {jupyter_cmd}"

    subprocess.run(["cmd", '/K', full_command])



def get_env_list(env_dir):
    envs = {}
    for x in os.listdir(env_dir):
        envs[x] = os.stat(f"{env_dir}\\{x}").st_mtime
    return envs

if __name__ == '__main__':
    main()
