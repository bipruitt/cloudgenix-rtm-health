##   Purpose   ##
''' This utility will pull all of the RTM flows (specific app required) for a site
over a period of time and write the details of any flow that violate a packet loss threshold to a csv file.
'''


import argparse
import json
import logging
import calendar, datetime, time


# CloudGenix Python SDK
import cloudgenix
import cloudgenix_idname


# Initialize Global Vars
SDK_VERSION = cloudgenix.version
SCRIPT_NAME = 'CloudGenix Python RTM Health'
SCRIPT_VERSION = "5.1.1"
count = 0
plc2sle3 = 0
pls2cle3 = 0
plc2sg3 = 0
pls2cg3 = 0

#########################
# Begin Input Variables #
#########################

# Hour of data to fetch back from current time
hoursOfdata = 4

# Current GMT-minus of the machine running the script
gmtminus = 5

# Minumum call duration in ms
mincallduration = 10000

site_name = "<put exact site name here>"

# name of real time app to run the report against
app_name = "rtp"

# Max Packet loss threshold
max_pl = 3

# Auth Token
CLOUDGENIX_AUTH_TOKEN = "<Auth Token Goes Here>"


#########################
#  End Input Variables  #
#########################

# Set logging to use function name
logger = logging.getLogger(__name__)


############################################################################
# Begin Script, parse arguments.
############################################################################

# Parse arguments
parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

# Allow Controller modification and debug level sets.
controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
controller_group.add_argument("--controller", "-C",
                              help="Controller URI, ex. https://api.cloudgenix.com:8443",
                              default=None)

controller_group.add_argument("--insecure", "-I", help="Disable SSL certificate and hostname verification",
                              dest='verify', action='store_false', default=True)

login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                         default=None)
login_group.add_argument("--pass", "-PW", help="Use this Password instead of prompting",
                         default=None)

debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
debug_group.add_argument("--debug", "-D", help="Verbose Debug info, levels 0-2", type=int,
                         default=0)

args = vars(parser.parse_args())

if args['debug'] == 1:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    logger.setLevel(logging.INFO)
elif args['debug'] >= 2:
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    logger.setLevel(logging.DEBUG)
else:
    # Remove all handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # set logging level to default
    logger.setLevel(logging.WARNING)

############################################################################
# Instantiate API
############################################################################

cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=args["verify"])

# set debug
cgx_session.set_debug(args["debug"])

############################################################################
# Get Current Datetime
############################################################################


# Static Variables
gmtminussec = gmtminus * 60 * 60
secondsOfdata = hoursOfdata * 60 * 60

now = datetime.datetime.utcnow()
print(now)

epoch_time = (int(time.time())) + int(gmtminussec)

starttime = ((epoch_time - secondsOfdata))

endtime = starttime + 3600

############################################################################
# Create File
############################################################################

f = open(site_name.__str__() + "." + app_name.__str__() + "." + "flowresults." + epoch_time.__str__() + ".csv","w+")

############################################################################
# Draw Interactive login banner, run interactive login including args above.
############################################################################

print("{0} v{1} ({2})\n".format(SCRIPT_NAME, SDK_VERSION, cgx_session.controller))

# interactive or cmd-line specified initial login

print("Authenticating")

#if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["password"]:
cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
if cgx_session.tenant_id is None:
    throw_error("AUTH_TOKEN login failure, please check token.")
else:
    print("Authenticated""\n")



############################################################################
# Get Site ID
############################################################################

print('Getting Site ID for Site Name : ' + site_name)

site_idname = cloudgenix_idname.siteid_to_name_dict(cgx_session)
site_id = json.dumps(site_idname[1][site_name])

print(site_name + " = " + site_id + "\n")


############################################################################
# Get App ID
############################################################################

print('Getting App ID for App Name : ' + app_name)

app_idname = cloudgenix_idname.appdefs_to_name_dict(cgx_session)
app_id = json.dumps(app_idname[1][app_name])

print(app_name + " = " + app_id + "\n")

############################################################################
# Function for Handling Flow Data
############################################################################

def flowhanlder(flow):

    # Get Values, assign to variable
    src_ip = json.dumps(flow['source_ip'])
    src_port = json.dumps(flow['source_port'])
    dst_ip = json.dumps(flow['destination_ip'])
    dst_port = json.dumps(flow['destination_port'])
    avg_pl_s2c = json.dumps(flow['avg_packet_loss_s2c'])
    avg_pl_c2s = json.dumps(flow['avg_packet_loss_c2s'])
    max_pl_s2c = json.dumps(flow['max_packet_loss_s2c'])
    max_pl_c2s = json.dumps(flow['max_packet_loss_c2s'])
    avg_mos_c2s = json.dumps(flow['avg_mos_c2s'])
    avg_mos_s2c = json.dumps(flow['avg_mos_s2c'])
    path_id = json.dumps(flow['path_id'])
    media_type = json.dumps(flow['media_type'])
    flow_start_time_epoch = int(json.dumps(flow['flow_start_time_ms'])) / 1000
    flow_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(flow_start_time_epoch))
    flow_end_time_epoch = int(json.dumps(flow['flow_end_time_ms'])) / 1000
    flow_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(flow_end_time_epoch))
    callduration = int(json.dumps(flow['flow_end_time_ms'])) - int(json.dumps(flow['flow_start_time_ms']))
    calldurationsec = callduration / 1000
    lan_dscp_lan_to_wan = json.dumps(flow['lan_dscp_lan_to_wan'])
    lan_dscp_wan_to_lan = json.dumps(flow['lan_dscp_wan_to_lan'])
    lan_to_wan = json.dumps(flow['lan_to_wan'])

    # Print to console, write to file
    print("Call Duration: " + str(calldurationsec))
    print('Average PL C2S : ' + json.dumps(flow['avg_packet_loss_c2s']))
    print("Source : " + (json.dumps(flow['source_ip'])) + ':' + (json.dumps(flow['source_port'])))
    print("Dest : " + (json.dumps(flow['destination_ip'])) + ':' + (json.dumps(flow['destination_port'])))
    print("Start Time : " + str(flow_start_time))
    print("End   Time : " + str(flow_end_time) + '\n')
    f.write(src_ip + ',' + src_port + ',')
    f.write(dst_ip + ',' + dst_port + ',')
    f.write(str(flow_start_time) + ',' + str(flow_end_time) + ',')
    f.write(str(calldurationsec) + ',')
    f.write(str(media_type) + ',' + str(lan_to_wan) + ',')
    f.write(avg_pl_s2c + ',' + avg_pl_c2s + ',' + max_pl_s2c + ',' + max_pl_c2s + ',')
    f.write(avg_mos_c2s + ',' + avg_mos_s2c + ',' + path_id + ',')
    f.write(lan_dscp_lan_to_wan + ',' + lan_dscp_wan_to_lan + '\n')

############################################################################
# Begin Logic
############################################################################

# Write CSV Header
f.write('src_ip' + ',' + 'src_port' + ','  + 'dst_ip' + ','  + 'dst_port' + ',' + 'start_time' + ','  + 'end_time' + ',' + 'call_duration_secs' + ',' + 'media_type' + ',' + 'lan_to_wan' + ',' + 'avg_loss_svr_to_client'  + ',' + 'avg_loss_client_to_svr' + ',' +  'max_loss_svr_to_client'  + ',' + 'max_loss_client_to_svr' + ',' +  'avg_mos_c2s'  + ',' + 'avg_mos_s2c' + ',' + 'path_id' + ','+ 'lan_dscp_lan_to_wan' + ',' + 'lan_dscp_wan_to_lan' + '\n')

# While loop used to iterate through 1 hour time blocks
while endtime <= epoch_time:
    endtimestr = time.strftime('%Y-%m-%d', time.localtime(endtime)) + 'T' + time.strftime('%H:%M:%S', time.localtime(endtime)) + '.0Z'
    print('Getting Flows for: ' + endtimestr)
    endtime = endtime + 3600

#   Used to post data to the flow_monitor api.  Specifies end time, site, appid
    postBody = '{"end_time":"' + endtimestr + '","filter":{"site":[' + site_id + '],"app":[' + app_id + ']},"debug_level":"all"}'
    # Get Flow Data
    response = cgx_session.post.flows_monitor(json.loads(postBody))

    # status is a boolean based on success/failure. If success, print raw dictionary
    if response.cgx_status:
        flow_records = response.cgx_content

    # else, let user know something didn't work.
    else:
        print("ERROR: ", json.dumps(response.cgx_content, indent=4))


    ############################################################################
    # Work with Flow Records
    ############################################################################


    json_status = flow_records['_status_code']
    if str(json_status) == '200':
        for flow in flow_records['flows']['items']:
            appid = flow['app_id']
            avg_pl_s2c = json.dumps(flow['avg_packet_loss_s2c'])
            avg_pl_c2s = json.dumps(flow['avg_packet_loss_c2s'])
            max_pl_s2c = json.dumps(flow['max_packet_loss_s2c'])
            max_pl_c2s = json.dumps(flow['max_packet_loss_c2s'])
            media_type = json.dumps(flow['media_type'])
            flow_end_time = int(json.dumps(flow['flow_end_time_ms']))
            flow_start_time = int(json.dumps(flow['flow_start_time_ms']))
            duration = flow_end_time - flow_start_time

            # Check for Packet loss value of null
            if max_pl_s2c != 'null':
                if float(max_pl_s2c) <= max_pl:
                    pls2cle3 += 1

                # Ignore Calls Shorter than Minimum Call Duration
                elif flow_end_time - flow_start_time <= mincallduration:
                    print(str(duration))
                    print("\n flow not greater than 10 seconds \n")

                else:
                    flowhanlder(flow)
                    pls2cg3 += 1

            # Check for Packet loss value of null
            if max_pl_c2s != 'null':
                if float(max_pl_c2s) <= max_pl:
                    plc2sle3 += 1

                # Ignore Calls Shorter than Minimum Call Duration
                elif int(json.dumps(flow['flow_end_time_ms'])) - int(json.dumps(flow['flow_start_time_ms'])) <= mincallduration:
                    durationss = int(json.dumps(flow['flow_start_time_ms'])) - int(json.dumps(flow['flow_end_time_ms']))
                    print(str(durationss))
                    print("\n flow not longer than 10 seconds \n")

                # Any flows with packet loss greater than 3 %
                else:
                    flowhanlder(flow)
                    plc2sg3 += 1

            count += 1

end = datetime.datetime.utcnow()

f.write('\n\n  -----  Results Summary  ----- \n')
f.write("Flow Records " + count.__str__() + '\n' + "Flows w/ PL LE 3 S2C: " + pls2cle3.__str__()+ '\n' + "Flows w/ PL LE 3 C2S: " + plc2sle3.__str__()+ '\n')
f.write("Flows w/ PL Greater than 3% S2C: " + pls2cg3.__str__() + '\n' + "Flows w/ PL Greater than 3% C2S: " + plc2sg3.__str__()+ '\n')
f.write('Minimum Call Duration Seconds: ' + (mincallduration/1000).__str__() + '\n')
f.write("Total Query Time : " + (end - now).__str__())

print('\n' + " -----  Results ----- ")
print("Flow Records " + count.__str__() + '\n' + "Flows w/ PL LE 3 S2C: " + pls2cle3.__str__()+ '\n' + "Flows w/ PL LE 3 C2S: " + plc2sle3.__str__())
print("Flows w/ PL Greater than 3 % S2C: " + pls2cg3.__str__() + '\n' + "Flows w/ PL Greater than 3 % C2S: " + plc2sg3.__str__())
print('Minimum Call Duration Seconds: ' + (mincallduration/1000).__str__())
print("Total Query Time : " + (end - now).__str__())

# end of script

