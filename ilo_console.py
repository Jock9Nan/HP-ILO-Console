import sys
import os
import redfish
import httplib2
import hpilo
import configparser
import time
import re
import httplib2


if len(sys.argv) <= 1:
    print  ("Thammudu, Pls provide the ILO IP/Hostname !")
    sys.exit()

ilo_ip=sys.argv[1]
user_login=
passwd=
IRC="ILO-IRC.jnlp"
IRC_URL='https://'+str(ilo_ip)+'/html/java_irc.html'
get_jar = re.compile(".*archive.*\/(.*.jar)")
counter=0

def obfuscate_pass(password):
    # return 1st 2 and the latest chars of the password
    return password[:2]+password[len(password) - 1:len(password)]


def check_hpilo(ilo_ip):  
    kind = "HP"
    ilo_url = ("https://%s/xmldata?item=All" % ilo_ip)
    h = httplib2.Http(".cache", disable_ssl_certificate_validation=True,timeout=10)
    h.follow_redirects = False
    try:
        resp, content = h.request(ilo_url, "GET")
        data = content
        if resp.status == 200:
            print (("Server: %s\nManufacturer: %s") % (ilo_ip, kind))
            #tls_signature = check_tls_signature(ilo_ip)
            return True
        else:
            print ("\n Hey, This Script works only for HP...")
            #check_tls_signature(ilo_ip)
            sys.exit(1)          
    except (httplib2.ServerNotFoundError,ConnectionRefusedError):
        print ("\nCould not connect to %s, Seems its not a proper HP-ILO and check VPN too.." % ilo_ip)
        sys.exit(1)


if check_hpilo(ilo_ip):
    #for Password in passwd.split('):
        hide_pass=obfuscate_pass(passwd)
        print ("\ntrying with %s password.." % hide_pass)
        try:
            RED_OBJ=redfish.redfish_client(base_url='https://'+str(ilo_ip),username=user_login,password=passwd,default_prefix="/redfish/v1")
            time.sleep(5)
            RED_OBJ.login(username=user_login, password=passwd, auth="session")
            session_id=RED_OBJ.get_session_key()
        except:
            print (sys.exc_info()[0])
            RED_OBJ.logout()
            del RED_OBJ
            counter+=10
            print ("\nLogin Delayed for %s seconds to with try another password ..." % (counter))
            time.sleep(counter) 
            #continue

        try:    
            h = httplib2.Http(".cache",disable_ssl_certificate_validation=True,timeout=3)
            h.add_credentials(user_login,passwd)
            headers={'Cookie': 'sessionKey=%s' % session_id }
            resp,content = h.request(
            IRC_URL,
            'GET',headers=headers   
            )
            data = content.decode('utf-8')
            jar=(get_jar.findall(data)[0])
        except NameError:
            print ("Session Key not created.. quitting ")
            sys.exit(1)
        except httplib2.ServerNotFoundError:
            print ("\nCould not connect to %s, Seems its not a proper HP-ILO" % ilo_ip)
            sys.exit(1)
        
        if isinstance (session_id,str):
            if isinstance (str(jar), str):
                with open("ilo_temp.jnlp") as f:
                    newText=f.read().replace('ILO_IP', ilo_ip).replace("session",session_id).replace('JAR',jar)
                    #newText=f.read().replace("session",session_id)
                with open(IRC, "w") as f:
                    f.write(newText)
            else:
                print ("proper java jar file not found.. it may not work with exist one..")
            print ("%s file created..." % IRC)
            os.system("javaws %s" % IRC )
            sys.exit(1)
        else:
            print ("seem something went wrong!!, Please try again...")
            exit
