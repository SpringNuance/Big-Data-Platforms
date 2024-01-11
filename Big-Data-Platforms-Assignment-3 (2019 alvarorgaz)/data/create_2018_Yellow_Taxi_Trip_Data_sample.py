import sys
n =0
with open('2018_Yellow_Taxi_Trip_Data.csv', 'r') as file, open('2018_Yellow_Taxi_Trip_Data_sample300.csv', 'w') as sample:
    for i, row in enumerate(file):
        n+=1
print(n)