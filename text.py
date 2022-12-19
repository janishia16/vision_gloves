#x=open("obj.txt","w")
#x.close()

"""
def wordcount(filename,usersaid):
    file=open(filename,'r')
    read=" "
    while(read):
        read=file.readline()
        print(read)
        if usersaid in read:
            return True
    file.close()

if wordcount("objects.txt","fruit"):
        print("hi")
"""
import datetime


hour=int(datetime.datetime.now().hour)
time=datetime.datetime.now().strftime("%H:%M:%S")
print(time)