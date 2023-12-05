{
	# This is a JSONic Config file. All comments are stripped out before being read. If the syntax gets broken brakes happen
    

    ###############################################################################
    # Proxies. To use no proxies, please keep as blank strings, otherwise put in hosts

      "proxies":{"http": "",
                 "https": ""},   

     # "proxies":{"http": "http://proxy.domain.com:8080",
     #            "https": "http://proxy.domain.com:8080"},
     

    ###########################################################################
    # Install related flags

    # Engage Silent Mode (Less output, does not completely eliminate however)
     "silent": false,
     # Engage Debug Mode (More output)
     "debug":  false,
     # Do not install requests into vENV. Just create and exit. 
     "no_install": false,
     # If the ENV already exists, clear it first, then install. Otherwise it will exit it otherwise exist (default)
     "overwrite": false,
     # Which Python version to use (Python39, Python310 etc).  latest uses the latest Python version on the system
     "pyver": "latest",
     # Location that Jupyter Integrations vENVs are created. Not recommended to change this. 
     "envloc": "%USERPROFILE%\\PythonENVs",
     # Where versions of Python are installed
     "pythoninstallloc": "%ProgramFiles%",
     
     
     #######################################################
     # Requirements files for pip installs. 
     # For different version you can specify extra pip arguments
     # You can also override the requirements files for testing using command line arguments
     # 
     # secondary_install va are packages that are removed from the original package list. And installed one by one
     # This can be due to errors or 
     #
     "requirements": { "Python310": {"req_file": "p310_requirements.txt",
                                     "req_extra_args": ["--use-deprecated=legacy-resolver"],
                                     "secondary_install": ["neo4j", "pycountry", "matplotlib_venn"]
                                     }
                     },

     ################################################
     # Jupyter Lab extra config items
     "open_browser": true,
     
     
     ##########################################################
     # Data Sourced Setup (Instances and ODBC)
     #     Data source Instances ENV Setup - This shouldn't change
     "data_source_loc": "%USERPROFILE%\\jupyter_data_sources.bat",
     "custom_data_source_loc": "%USERPROFILE%\\jupyter_data_sources_custom.bat",
     
     ###############
     # Allows for custom Variables in ODBC Driver Templates
     # If the value is a env variable it will be resolved. 
     # This allows you to put variables in the registry file ODBC templates
     #
     
     "odbc_vars": {"%TERADRIVERVER%": "17.10",
                   "%USER%": "%USERNAME%"
                   },


     ############################################
     # User groups are used to specify different Helloworld files or different installs for groups at your org. 
     # TODO Also apply to data sources and ODBC maybe? 
     #

     "user_groups": {
                        "team1": ["user1", "user2"]
      },
      
     #######################################################
     # Integrations Setup Related Items
     
     # This is the items passed to the object instantiation. It allows you to turn on debug from load time. Debug is noisy, so this is not recommended. 
     
     "integrations_obj_vars": "ipy, debug=False",
     
     # Which integrations should be installed. These should have a corresponding value in the repo dictionary
     "install_integrations": ["jupyter_integration_base", "jupyter_pyodbc", "jupyter_splunk",
                              "jupyter_es", "jupyter_oracle", "jupyter_impala", "jupyter_tera",
                              "jupyter_hive", "qgrid", "jupyter_dummy", "jupyter_dtools", "jupyter_mongo"],
       

     #################    
     # These are the repos 
     # Type is a siz download
     # Under groups, if the string "no_install" is included, the repo is still installed. It just doesn't get a startup file. 
     # Some items like integration base or qgrid don't get instantiated during startup. (directly)
     # Also, you may specify add_cmd in order to run another command after the installation is complete. 
     
     "repos": {"jupyter_integration_base": {  
                            "type": "zip", 
                            "groups": ["no_install"],
                            "repo": "https://github.com/JohnOmernik/jupyter_integration_base/archive/refs/heads/master.zip"
                          },
               "jupyter_pyodbc": {  
                            "type": "zip",
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_pyodbc/archive/refs/heads/master.zip"
                          },
                "jupyter_splunk": {  
                            "type": "zip",
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_splunk/archive/refs/heads/master.zip"
                          },
                "jupyter_es": {  
                            "type": "zip",
                            "groups": ["all"],                            
                            "repo": "https://github.com/JohnOmernik/jupyter_es/archive/refs/heads/main.zip"
                          },                          
                "jupyter_oracle": {  
                            "type": "zip", 
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_oracle/archive/refs/heads/main.zip"
                          },                          
                "jupyter_impala": {  
                            "type": "zip",
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_impala/archive/refs/heads/master.zip"
                          },
                "jupyter_tera": {  
                            "type": "zip",
                            "groups": ["all"],                            
                            "repo": "https://github.com/JohnOmernik/jupyter_tera/archive/refs/heads/master.zip"
                          },               
                "jupyter_hive": {  
                            "type": "zip", 
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_hive/archive/refs/heads/main.zip"
                          },                
                "jupyter_dtools": {  
                            "type": "zip", 
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_dtools/archive/refs/heads/main.zip"
                          },
              "jupyter_mongo": {  
                            "type": "zip", 
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_mongo/archive/refs/heads/main.zip"
                          },
                "qgrid": {  
                            "type": "zip", 
                            "groups": ["no_install"],
                            "add_cmd": "pip install qgrid2-1.1.3-py3-none-any.whl",
                            "repo": "https://github.com/JohnOmernik/qgrid/archive/refs/heads/main.zip"
                          },                          
                "jupyter_dummy": {  
                            "type": "zip", 
                            "groups": ["all"],
                            "repo": "https://github.com/JohnOmernik/jupyter_dummy/archive/refs/heads/main.zip"
                          }
              }
}
