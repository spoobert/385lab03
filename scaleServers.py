#!/usr/bin/python
import googleapiclient.discovery
from sys import argv
from itertools import islice
from subprocess import call

MAXINSTS = 7

def genconf(A):
    with open('confTempl', 'r') as f:
        template = f.read()     
    conf = template.replace("PLACE IP HERE", '\n'.join('\tserver {};'.format(ip) for ip in A ) ) 
    with open('conf','w') as f:
        f.write(conf)
#this function is used by makeLessServers to determine which server to shut down first
def sortedNamesLongest( runningInstances , compute, projId, zone ):
    def getStartTime( instance ):
        filterString = '(targetId eq {})(operationType eq start|insert)'.format( instance['id'] ) 
        operations = compute.zoneOperations().list( project = projId, zone = zone ,
                                                    filter = filterString ).execute() 
        print( filterString )
        mostRecentStart = sorted(operations['items'],
                            key = lambda x: x['startTime'],
                            reverse = True )[0]['startTime']
        return dict(name=instance['name'], startTime=mostRecentStart)

    startTimes = map( getStartTime, runningInstances ) 
    sortedStartTimes = sorted( startTimes , key = lambda x: x['startTime'] )

    return ( opp['name'] for opp in sortedStartTimes )

def stopInstance( longestName, compute, projId, zone ):
    compute.instances().stop( project = projId, zone = zone, instance = longestName ).execute()
    
def stopLongestInsts( instances, compute, projId, zone, targetCount ):
    longestNames = sortedNamesLongest( instances , compute , projId , zone )
    for name in islice( longestNames, targetCount ):
        stopInstance( name, compute, projId, zone )
        

    

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
        
'''
def nextServerName( currentNames ):
    newServers = []
    for j in range( len( serverList ) ):
'''


serverSet = { 
    'restserver-00', 'restserver-01', 'restserver-02' , 
    'restserver-03', 'restserver-04', 'restserver-05',
    'restserver-06' }

def main():
    
    
    compute = googleapiclient.discovery.build('compute','v1')
    projId = argv[1]
    zone = argv[2]

    targetCount = int( argv[3] )
    if targetCount > MAXINSTS:
        print( "to many instances you gave {} max is {}".format( targetCount, MAXINSTS ) )
        exit(1) 
    #gather all restservers
    instances = compute.instances().list( project = projId, zone = zone, filter = '(name eq restserver.*)' ).execute()
    #check if their are any items in instances: sort running set and stopped set
    print( instances )
    if 'items' in instances:
        runningInsts =  filter( lambda x: x['status'] == 'RUNNING', instances['items'] )
        stoppedInsts =  filter( lambda x: x['status'] in ( 'TERMINATED', 'STOPPED' ), instances['items'] )
        runningInstsList = list( runningInsts )
        stoppedInstsList = list( stoppedInsts )
        runningCount = len( runningInstsList ) 
        stoppedCount = len( stoppedInstsList )
        print( runningCount )
        print( stoppedCount )
    else: 
        runningCount = 0 
       
    usedInstsNames = set( [instance['name'] for instance in instances['items']] )
    avalInstsNames = serverSet - usedInstsNames
    changeInRCount = abs( targetCount - runningCount )
    if targetCount < runningCount:
        stopLongestInsts( runningInstsList, compute, projId, zone, changeInRCount )
    elif targetCount > runningCount:
        avalCount = min( changeInRCount, stoppedCount )
        for stopped in stoppedInstsList[:avalCount]:
            print( stopped['name'] )
            compute.instances().start( project = projId , zone = zone, instance = stopped['name'] ).execute()
        for avalName in islice( avalInstsNames, changeInRCount - avalCount ):
            config = restConfig( avalName )
            compute.instances().insert( project = projId , body = config , zone = zone ).execute()
    elif changeInRCount == 0:
        print("no changes to be made")
    updatedInsts = compute.instances().list( project = projId, zone = zone , filter = '(name eq restserver.*)(status eq RUNNING)' ).execute()
    
    ipList = [ instance['networkInterfaces'][0]['networkIP']  for instance in updatedInsts['items'] ]
    
    genconf( ipList )

    
    retCode = call(['scp', '-i','~/.ssh/id_gcp','/Users/comrade/Desktop/385/lab03/conf', 'devin@104.154.156.77:/etc/nginx/sites-available/default'])
    
    sshCallCode = call( ['ssh','-i','~/.ssh/id_gcp','devin@104.154.156.77','sudo service nginx reload'] )


    
main() 
 