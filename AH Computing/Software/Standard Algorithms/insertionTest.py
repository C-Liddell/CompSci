list = [4,5,7,3,2,6,9,1]

for sortingList in range(len(list)-1,0,-1):
    for index in range(sortingList):
        if list[index] > list[index+1]:
            temp = list[index]
            list[index] = list[index+1]
            list[index+1] = temp

print(list)