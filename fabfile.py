import os
from contextlib import contextmanager 
from fabric.api import *
from fabric.api import local,prefix
from fabric.api import lcd,cd
from fabric.api import run, env

env.hosts = ['IP address of remote machine']
env.user = "root"
env.db_user = "user"
env.db_passwd = " "
env.activate = "/bin/bash --rcfile '/path/to/env/bin/activate'"
env.dir = "/path/to/project/root"
env.ldir = "/path/to/local/database/dump/directory"
env.rdir = "/path/to/remote/database/dump/directory"


'''
Prepares the deployment on local machine and pushes the changes to remote
machine
'''
def prepare_deployment(branch_name):
  local('git add * && git commit')
  local('git checkout master && git merge ' + branch_name)
  local('git push origin master:branch_name')

'''
Deploys the changes on the remote machine
'''
def deploy(branch_name):
  branch = raw_input("Enter the name of the branch you want to checkout: ")
  with cd(env.dir):
    run('git checkout %s && git merge %s' %(branch,branch_name))
    restart()
'''
Installs the requirements on the remote Virtual Environment
'''
def install():
  with cd(env.dir):
    run("pip install -r requirements.txt")
    pass
'''
Activates the Virtual Environment on remote machine
'''
def activate():
  run(env.activate)
  pass

'''
Restarts the remote machine
'''
def restart():
  local('sudo service apache2 reload')

'''
Drop the old database , creates the new Database and synchronises the
new model changes.
Caution : Be careful using this fab function it will delete all the data in the
database
''' 
def rebuild_db():
  env.db_schema = raw_input("Enter the name of Database you want to drop: ")
  run('mysql -u %s -p%s -e "drop database if exists %s"' % (env.db_user,
    env.db_passwd, env.db_schema))
  env.db_schema = raw_input("Enter the name of Database you want to create: ")
  run('mysql -u %s -p%s -e "create database %s"' % (env.db_user,
    env.db_passwd, env.db_schema))
  run('python manage.py syncdb')

'''
Runs a query on your desired Database on remote machine from your local machine
'''
def query():
  env.db_schema = raw_input("Enter the name of Database you want to use: ")
  env.query = raw_input("Enter the query : ")
  run('mysql -u %s -p%s -e "use %s;%s"' % (env.db_user,
    env.db_passwd, env.db_schema,env.query))

'''
Kills the particular process you want to by specifying the name
of the process
'''
def kill():
  kill = raw_input("Enter the name of process you want to kill: ")
  run('pkill -f %s' %(kill))

'''
Takes the dump of the remote database and transfers the dump on your local machine
'''
def remote_dump():
  env.dbname = raw_input("Enter the name of Database you want to dump : ")
  env.dump = raw_input("Enter the name you want to assign to dump : ")
  run('mysqldump -u %s -p%s %s > %s/%s.sql' %(env.db_user,env.db_passwd,
    env.dbname,env.rdir,env.dump))
  env.dump1 = raw_input("Enter the name you want to assign to local dump : ")
  get(env.rdir+"/"+env.dump+".sql",env.ldir+"/"+env.dump1+"."+env.host)

'''
Collects all static files
'''
def collectstatic():
  with cd(env.dir):
    run('python manage.py collectstatic')

