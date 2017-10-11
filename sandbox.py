#!/usr/bin/python
import googleapiclient.discovery
from pyrfc3339 import parse
import iso8601



def genconf(A):
    with open('confTempl', 'r') as f:
        template = f.read()     
    conf = template.replace("PLACE IP HERE", A)
    with open('conf','w') as f:
        f.write(conf)

def getLongestRunningId( runningInstances , compute, projId, zone ):
    instances = list( runningInstances )
    if instances == []:
        return instances
        
    def getStartTime( instance ):
        filterString = '(targetId eq {})(operationType eq start)'.format( instance['id'] ) 
        operations = compute.zoneOperations().list( project = projId, zone = zone ,
                                                    filter = filterString ).execute() 
        
        return sorted( operations['items'] , key = lambda x: x['startTime'] , reverse = True )[0]['startTime']

    startTimes = map( getStartTime, instances ) 
    
    instanceNames = map ( lambda x: x['name'] , instances )

    idStart =  zip( instanceNames , startTimes )

    sortedStartTimes = sorted( idStart , key = lambda x: x[1] )
    print( sortedStartTimes)

    return sortedStartTimes[0][0] 

def stopInstance( longestName, compute, projId, zone ):
    compute.instances().stop( project = projId, zone = zone, instance = longestName ).execute()
    
def makeLessServers( instances, compute, projId, zone, serverCount ):
    longestName = getLongestRunningId( runningInsts , compute , projId , zone )
    #check to make sure the there was at least one server running
    if longestName != []:
        stopInstance( longestName, compute, projId, zone )
    

def restConfig( serverName ):
    return {
        "name": serverName,
        "machineType": "projects/linen-walker-178616/zones/us-central1-c/machineTypes/f1-micro",
        "disks": [
            {
                "autoDelete": True,
                "boot": True,
                "initializeParams" : {
                    "sourceImage" : "projects/linen-walker-178616/global/images/lab02-restserver",
                }
            }
        ],
        "serviceAccounts": [
            {
            "email": "default",
            "scopes": [
                "https://www.googleapis.com/auth/devstorage.read_only",
                "https://www.googleapis.com/auth/logging.write",
                "https://www.googleapis.com/auth/monitoring.write",
                "https://www.googleapis.com/auth/servicecontrol",
                "https://www.googleapis.com/auth/service.management.readonly",
                "https://www.googleapis.com/auth/trace.append"
            ]
            }
        ],
        "metadata": {
            "items" : [{
                "key" : "startup-script",
                "value" : "nohup sudo FLASK_APP=/opt/restserver/restserver.py flask run --host=0.0.0.0 --port=80 &"
            }],
        },
        "networkInterfaces": [
            {
                "accessConfigs": [
                    {
                        "name": "External NAT",
                        "type": "ONE_TO_ONE_NAT"
                    }
                ],
                "network": "projects/linen-walker-178616/global/networks/default"
            }
        ]
    }
        
        
    
   


def main():
    
    compute = googleapiclient.discovery.build('compute','v1')
    projId = 'linen-walker-178616'
    zone = 'us-central1-c'
    #gather all restservers
    instances = compute.instances().list( project = projId, zone = zone, filter = '(name eq restserver.*)' ).execute()
    #determine how many of these are running
    #runningInsts = filter( lambda x: x['status'] == 'RUNNING', instances['items'] )
    #runningCount = len( list( runningInsts ) )    
    #makeLessServers( instances, compute , projId, zone, 1 )

    config = restConfig( "restserver-07" )

    compute.instances().insert( project = projId , body = config , zone = zone ).execute()

    #operations = compute.zoneOperations().list( project = projId, zone = zone ,filter = '(targetId eq 7746285348118427911)(operationType eq start)').execute() 
    #print( sorted([ opp['startTime'] for opp in operations['items'] ]))
    
    #print(operations)



    
main() 


'''
 {
  "canIpForward": false,
  "cpuPlatform": "Unknown CPU Platform",
  "creationTimestamp": "2017-09-15T10:08:07.968-07:00",
  "description": "",
 
  "id": "4343228110604449304",
  "kind": "compute#instance",
  "labelFingerprint": "42WmSpB8rSM=",
 
  "scheduling": {
    "automaticRestart": true,
    "onHostMaintenance": "MIGRATE",
    "preemptible": false
  },
  "selfLink": "projects/linen-walker-178616/zones/us-central1-c/instances/restserver-0",
  "startRestricted": false,
  "status": "TERMINATED",
  "tags": {
    "fingerprint": "6smc4R4d39I=",
    "items": [
      "http-server",
      "https-server"
    ]
  },
 
}
'''