import Node1OneDay
import time
import pandas as pd

def main():
    #path of one file about dataset
    file_path = '/app/Apt2_2016.csv'

    # read the file specifying the separator
    df = pd.read_csv(file_path, sep=',', header=None, names=['datetime', 'value'])


    step = 30
    totalData = 43201
    result = df.iloc[:totalData:step, 1]  # select the column 'value' each 30 rows, because I'm interested in data every 30 minutes

    dataForMonth = (totalData-1)/step
    tmp = result.tolist()
    v =[]
    for val in tmp:
        n = float(val)
        v.append(n)
    #parameters
    scale_mod_size = 50
    batch_size = 8
    mult_depth=1
    time.sleep(10)

    segment_length=48
    c=1
    #the method encrypt and serialize values about consum per day. The called this method 30 times, one for day. I use the same key and crypto context for every day.
    for i in range(0,len(v)-1,segment_length):
        if (c == 1):
            node1SetupTuple = Node1OneDay.node1_encrypt_serialize_4Day_firstDay(v[i:i+segment_length],scale_mod_size,batch_size, mult_depth,c, dataForMonth)
            cc = node1SetupTuple[0]
            keypair = node1SetupTuple[1]
            c = c+1
        else:
            node1SetupTuple = Node1OneDay.node1_encrypt_serialize_4Day(v[i:i+segment_length],scale_mod_size,batch_size, mult_depth, c, cc, keypair)
            c = c+1

    time.sleep(160)  # Wait for Node2 computations
    sum=[]
    k=1
    #check the consumption is correct for each day
    for i in range(0,len(v)-1,segment_length):
        result =  Node1OneDay.node1_deserialize_decrypt_verify_4Day(v[i:i+segment_length], cc, keypair,k)
        sum.append(result)
        k = k+1
    time.sleep(20)

    #check the consumption is correct for the month
    Node1OneDay.node1_deserialize_decrypt_verify_4Month(sum, cc, keypair, dataForMonth)

'''
ONLY ONE DAY
   # Estrai i valori dalla seconda colonna (colonna 'value') ONLY ONE DAY
        result = df.iloc[:1441:15, 1]  # Seleziona la colonna 'value' ogni 15 righe, partendo dalla seconda riga
        tmp = result.tolist()
        v =[]
        for val in tmp:
            n = float(val)
            v.append(n)
    # df = pd.read_csv(file_path,header=None)
        #result = df.iloc[:97:15,1]
        #i = len(v)
    #Step 1 Only One Day
    node1SetupTuple = Node1OneDay.node1_encrypt_serialize_4Day(v,scale_mod_size,batch_size,1)
    cc = node1SetupTuple[0]
    keypair = node1SetupTuple[1]

    # Step 2 Only One Day
    time.sleep(15)  # Wait for Node2 computations


    # Step 3
    Node1OneDay.node1_deserialize_decrypt_verify_4Day(v, cc, keypair)
'''
if __name__ == '__main__':
    main()
