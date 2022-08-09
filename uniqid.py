import uuid


ids = ['some']


break_flag = False
for i in range(200):
    newid = str(uuid.uuid4())[:8]
    for id in ids:
        print('Compare : ', newid, id)
        if(newid == id):
            print("SAME")
            break_flag = True
            break
    if(break_flag):
        break
    else:
        ids.append(newid)
if(not break_flag):
    print('NO MATCH')
