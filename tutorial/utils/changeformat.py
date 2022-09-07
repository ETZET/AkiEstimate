import sys
# Fix the format of the dispersion file for Aki02 code
input = sys.argv[1]
stapair = sys.argv[2]

filename = input+'/LoveResponse/dispersion_'+stapair+'.txt'
file1 = open(filename, 'r')
ori = file1.readlines()
print(stapair)
file1.close()

broken = ori[1].split(' ')
newline = broken[0] + ' ' + str(int(float(broken[1]))) + ' ' + broken[2] + ' '+ broken[3] + ' 7200\n'

try:
    file2 = open(filename, 'w')
    file2.write(ori[0])
    file2.write(newline)
    for i in range(2, len(ori)):
        file2.write(ori[i])
    file2.close()
except:  # prevent the python code from erasing the text file
    print("Failed to change format --python")
    file2 = open(filename, 'w')
    file2.writelines(ori)
    file2.close()

filename = input+'/RayleighResponse/dispersion_'+stapair+'.txt'
file1 = open(filename, 'r')
ori = file1.readlines()
file1.close()

broken = ori[1].split(' ')
newline = broken[0] + ' ' + str(int(float(broken[1]))) + ' ' + broken[2] + ' '+ broken[3] + ' 7200\n'
try:
    file2 = open(filename, 'w')
    file2.write(ori[0])
    file2.write(newline)
    for i in range(2, len(ori)):
        file2.write(ori[i])
    file2.close()
except:
    print("Failed to change format --python")
    file2 = open(filename, 'w')
    file2.writelines(ori)
    file2.close()

filename = input+'/RayleighResponse_R/dispersion_'+stapair+'.txt'
file1 = open(filename, 'r')
ori = file1.readlines()
file1.close()

broken = ori[1].split(' ')
newline = broken[0] + ' ' + str(int(float(broken[1]))) + ' ' + broken[2] + ' '+ broken[3] + ' 7200\n'
try:
    file2 = open(filename, 'w')
    file2.write(ori[0])
    file2.write(newline)
    for i in range(2, len(ori)):
        file2.write(ori[i])
    file2.close()
except:
    print("Failed to change format --python")
    file2 = open(filename, 'w')
    file2.writelines(ori)
    file2.close()
