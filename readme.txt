
To avoid granting raw socket access to every Python script on your system, apply the capability only to a local copy of the interpreter within a virtual environment. 
Medium
Medium
Create a venv:
python3 -m venv my_rfof_env
Apply to the local binary:
sudo setcap cap_net_raw+ep ./my_rfof_env/bin/python3 
