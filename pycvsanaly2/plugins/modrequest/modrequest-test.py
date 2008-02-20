import database as dbmodule
conection = "mysql://user:passwd@localhost/database"
db = dbmodule.Database(conection)

tuples = db.querySQL('commit_id, revision', 'log', order="revision")
lastRevision = ''
revisionList = []
list = []
for tuple in tuples:
    if tuple[1] == lastRevision:
        list.append(int(tuple[0]))
    else:
        list.sort()
        revisionList.append(list)
        list = []
        list.append(int(tuple[0]))
    lastRevision = tuple[1]


tuples = db.querySQL("commit_id, request_id", "cvsanal_modrequest", order="request_id")
lastRevision = ''
requestList = []
list = []
for tuple in tuples:
    if tuple[1] == lastRevision:
        list.append(int(tuple[0]))
    else:
        list.sort()
        requestList.append(list)
        list = []
        list.append(int(tuple[0]))
    lastRevision = tuple[1]

print len(requestList)
print len(revisionList)

count = 0
count2 = 0
for lista in requestList:
    if lista in revisionList:
#        print " OK"
        count+=1
    else:
        print lista, 
        print " NO <------"
        count2 +=1


print
print count, "OK"
print count2, "NO"
