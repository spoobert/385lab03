#!/usr/bin/python
import googleapiclient.discovery
from pyrfc3339 import parse
import iso8601



def genconf(A):
    with open('defTemplate', 'r') as f:
        template = f.read()     
    conf = template.replace("PLACE IP HERE", A)
    with open('conf','w') as f:
        f.write(conf)

def getLongestRunningId( runningInstances , compute, projId, zone ):
    instances = list( runningInstances )
        
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
    

def main():
    
    compute = googleapiclient.discovery.build('compute','v1')
    projId = 'linen-walker-178616'
    zone = 'us-central1-c'
    #all instances servers gathered
    instances = compute.instances().list( project = projId, zone = zone, filter = '(name eq restserver.*)' ).execute()
    #if to many instances stop one sto filter all to RUNNING
    runningInsts = filter( lambda x: x['status'] == 'RUNNING', instances['items'] )

    longestName = getLongestRunningId( runningInsts , compute , projId , zone )

    stopInstance( longestName, compute, projId, zone )




    #operations = compute.zoneOperations().list( project = projId, zone = zone ,filter = '(targetId eq 7746285348118427911)(operationType eq start)').execute() 
    #print( sorted([ opp['startTime'] for opp in operations['items'] ]))
    
    #print(operations)



    '''
    icount = curNumIns()
    # x : + - instance counter, (1,x) : reduce instances, 
    # (2,x) : create instances, 0 : do nothing
    state = getState()

    # *** When to generate confTempl ***
    # the info for the confTempl 
    ipList = ipBuilder()
    genconf(ipList)

    if state == 0:
        #Do nothing?
    elif state == 1:
        #find the longest running instance
        longestID = getLongestID()
        #stop this instance
        stopInstance(longestID)
        while(instance counter != 0)
            nextId = getNextRunningId()
            stop(nexId)
            instance counter --
        placeIdHere = 
    elif state == 2:
        #start instance from existing copies
        while(instance counter != 0)
            #returns 0 if no copies available 
            nextId = getNextAvailableID()
            if( nextID == 0 )
        #check instance count
        #if instance count still not at 0 creat new instances
        #after creating then start
    
    # this function needs to ssh into the loadbalancer server
    # in order to run < sudo service nginx reload > 
    nGinxReload()

    
    
    '''
main() 
