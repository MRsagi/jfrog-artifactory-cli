import argparse
import urllib3
from urllib.parse import urlencode
from getpass import getpass
import json
import sys
import os


parser = argparse.ArgumentParser(description="Sagi's API for jfrog artifactory")
parser.add_argument("-p", "--ping", action="store_true",help="ping the system for health check")
parser.add_argument("-v", "--version", action="store_true",help="Show server version information")
parser.add_argument("-a","--add", action="store_true",help="add user (prompts for username, email address, and password)")
parser.add_argument("-d","--delete", action="store_true",help="deletes user (prompts for username)")
parser.add_argument("-s","--storage", action="store_true",help="shows the server storage information")
parser.add_argument("-c","--config", action="store_true",help="reconfig user configuration")

args = parser.parse_args()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HTTP = urllib3.PoolManager()

def main():
    if not os.path.exists("config.json"):
        print("No configuration file found")
        config_client()
    if args.ping:
        ping()
    elif args.version:
        get_version()
    elif args.add:
        create_user()
    elif args.delete:
        delete_user()
    elif args.storage:
        get_storage_info()
    elif args.config:
        config_client()
    else:
        sys.exit("No valid option specified.\nRun with --help to see manual.")


def config_client():
    configs = {}
    configs["server"] = input("server address: ")
    configs["context"] = "artifactory"
    configs["username"] = input("username: ")
    password = getpass()
    configs["access_token"] = login(configs["server"],configs["context"],configs["username"],password)
    with open("config.json","w") as f:
        json.dump(configs,f)
    print("Config written.")

def get_config(key=False):
    with open("config.json","r") as f:
        j = json.load(f)
    if key:
        return j[key]
    else:
        return j

def login(server,context,username,password,timeout_sec=0):
    options =  {'username': username, 'scope': 'member-of-groups:*', 'expires_in': timeout_sec}
    encoded_options = urlencode(options)
    headers_dict = urllib3.make_headers(basic_auth='%s:%s' % (username,password))
    headers_dict['Content-Type'] = 'application/x-www-form-urlencoded'
    URL='https://%s/%s/api/security/token?%s'% (server,context,encoded_options)
    resp = HTTP.request('POST',URL,headers=headers_dict)
    if resp.status == 200:
        output = json.loads(resp.data.decode('utf-8'))
        return output["access_token"]
    else:
        sys.exit("ERROR retriving token from server\n%s" % resp.data.decode('utf-8'))


def send_api_request(api_req,req_type="GET",data=""):
    j = get_config()
    ACCESS_HEADER = urllib3.make_headers(basic_auth='%s:%s' % (j['username'],j["access_token"]))
    URL = 'https://%s/%s%s' % (j["server"],j["context"],api_req)
    print("Requesting url: "+URL)
    if req_type == "PUT":
        headers_dict = ACCESS_HEADER
        headers_dict['Content-Type'] = 'application/json'
        response = HTTP.request(req_type,URL,headers=headers_dict,body=data)
    else:
        response = HTTP.request(req_type,URL,headers=ACCESS_HEADER)
    return response


def ping():
    server = get_config("server")
    print("pinging "+server)
    req ="/api/system/ping"
    resp = send_api_request(req)
    if resp.data == b'OK':
        print("Response from %s: %s" % (server,resp.data.decode('utf-8')))
    else:
        print("Error from server %s:\n%s" % (server,resp.data.decode('utf-8')))


def get_version():
    req ="/api/system/version"
    resp = send_api_request(req)
    print(resp.data.decode('utf-8'))


def create_user():
    user_dict={}
    user_dict["name"] = input("name: ")
    user_dict["email"] = input("Email: ")
    user_dict["password"] = getpass()
    user_json = json.dumps(user_dict).encode('utf-8')
    resp = send_api_request("/api/security/users/"+user_dict["name"],"PUT",user_json)
    if resp.status == 201:
        print("User successfully created")


def delete_user():
    username = input("please specify the user name you want to delete: ")
    if username != "":
        resp = send_api_request("/api/security/users/"+username,"DELETE")
    else:
        sys.exit("Invalid username")

    if resp.status == 200:
        print(resp.data.decode('utf-8'))
    else:
        print("Could not delete user %s. %s" % (username,resp.data.decode('utf-8')))
    
def get_storage_info():
    resp = send_api_request('/api/storageinfo')
    json_resp = json.loads(resp.data.decode('utf-8'))
    print(json.dumps(json_resp,indent=2))


if __name__ == "__main__":
    main()