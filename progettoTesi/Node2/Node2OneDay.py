import os

import openfhe
import Solid_proxy

# FILES PATH DEFINITION

mylocalfolder = "LocalData"
podSum = "podSum"
podAverage = "podAverageMonth"
# Save-Load locations for keys
ccLocation = 'cryptocontext'
pubKeyLocation = 'key_pub'  # Pub key
multKeyLocation = 'key_mult'  # relinearization key

cipherTextFile = []
for i in range(48):
    cipherTextFile.append('cipherText'+str(i))


# Save-load locations for evaluated ciphertexts
cipherAddLocationMonth = 'ciphertextAddMonth'
cipherAverageLocationMonth = 'ciphertextAverageMonth'
inverseDayLocation = 'inverseDay'
inverseMonthLocation = 'inverseMonth'
# Demarcate - Visual separator between the sections of code
def demarcate(msg):
    print("**************************************************")
    print(msg)
    print("**************************************************\n")

###
# node2_deserialize_computate_serialize
#  - Download Context, Keys and Ciphertexts from Node1's Pod
#  - deserialize data from downloaded files
#  - process data by doing operations
#  - Serialize the result to files
#  - Write serialized files to my pod
# It is the same for the two methods
###

def node2_deserialize_compute_serialize_4Day():
    demarcate("Part 2a: Download Context, Keys and Ciphertexts from Node1's Pod (Node 2)")

    esiste = True
    j=1
    # I calculate the consum for every day in one month and I check if exists the day because I can also calculate the consum for only one day.
    while esiste and j<31:
        mypodfolder = "Day"+str(j)+"Aggregate"
        ownerpodfolder = "Day"+str(j)+"ForHour"
        print(mypodfolder)
        print(ownerpodfolder)
        if (Solid_proxy.url_exists(ownerpodfolder)):
            Solid_proxy.read_data_from_pod(ownerpodfolder, mylocalfolder, ccLocation)
            Solid_proxy.read_data_from_pod(ownerpodfolder, mylocalfolder, pubKeyLocation)
            Solid_proxy.read_inverse(mylocalfolder, inverseDayLocation)
            Solid_proxy.read_data_from_pod(ownerpodfolder, mylocalfolder, multKeyLocation)
            for cipherText in cipherTextFile:
                Solid_proxy.read_data_from_pod(ownerpodfolder, mylocalfolder, cipherText)

            demarcate("Part 2b: Cryptocontext and data deserialization (Node 2)")

            node2CC, res = openfhe.DeserializeCryptoContext(f"{mylocalfolder}/{ccLocation}", openfhe.BINARY)
            if not res:
                raise Exception(f"I cannot deserialize the cryptocontext from {mylocalfolder}/{ccLocation}")

            print("Node2: Deserialized CryptoContex")

            if not node2CC.DeserializeEvalMultKey(f"{mylocalfolder}/{multKeyLocation}", openfhe.BINARY):
                raise Exception(f"Cannot deserialize eval mult keys from {mylocalfolder}/{multKeyLocation}")
            print("Node2: Deserialized eval mult keys\n")

            inverseDay, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{inverseDayLocation}", openfhe.BINARY)
            if not res:
                raise Exception(f"I cannot deserialize the inverse from {mylocalfolder}/{inverseDayLocation}")

            # Deserialize every ciphertext, so every cipher consum for different minutes in one day
            node2C = []
            for i in range(len(cipherTextFile)):
                # Initialize node2C list with None (assuming it will store deserialized ciphertexts)
                node2C.append(None)
                node2C[i], res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{cipherTextFile[i]}", openfhe.BINARY)
                if not res:
                    raise Exception(f"Cannot deserialize the ciphertext from {mylocalfolder}/{cipherTextFile[i]}")
                print(f"Node2: Deserialized ciphertext {i}\n")


            # Remove of local files
            #os.remove(f"{mylocalfolder}/{ccLocation}")
            os.remove(f"{mylocalfolder}/{pubKeyLocation}")
            os.remove(f"{mylocalfolder}/{multKeyLocation}")
            os.remove(f"{mylocalfolder}/{inverseDayLocation}")

            for cipherText in cipherTextFile:
                os.remove(f"{mylocalfolder}/{cipherText}")

            demarcate("Part 2c: Computation (Node 2)")



            # Calculate consum in one day: consum(i) + consum(i+1)
            node2CiphertextAdd = node2C[0]
            for i in range(1, len(node2C)):
                node2CiphertextAdd = node2CC.EvalAdd(node2CiphertextAdd, node2C[i])

            # Calculate average of one day: cipher consum * 1/number of data
            node2CiphertextAverage= node2CC.EvalMult(node2CiphertextAdd, inverseDay)


            demarcate("Part 2d: Serialization of data that has been operated on (Node 2)")

             # Node 2 serialize the result of the computation and average, to send it back to Node 1
            cipherAddLocation = 'ciphertextAdd'+str(j)
            cipherAverageLocation = 'cipherAverage'+str(j)
            openfhe.SerializeToFile(f"{mylocalfolder}/{cipherAddLocation}", node2CiphertextAdd, openfhe.BINARY)
            openfhe.SerializeToFile(f"{mylocalfolder}/{ccLocation}", node2CC, openfhe.BINARY)
            openfhe.SerializeToFile(f"{mylocalfolder}/{cipherAverageLocation}", node2CiphertextAverage, openfhe.BINARY)

            demarcate("Part 2e: Saving computation result on SolidPod (Node2)")

            if not Solid_proxy.write_data_to_pod(mypodfolder, mylocalfolder, cipherAddLocation):
                raise Exception("Exception writing AddResult to SolidPod")
            print("AddResult saved to pod")

            if not Solid_proxy.write_data_to_pod(mypodfolder, mylocalfolder, ccLocation):
                raise Exception("Exception writing CryptoContext to SolidPod")
            print("CryptoContex saved to pod")

            if not Solid_proxy.write_data_to_pod(mypodfolder, mylocalfolder, cipherAverageLocation):
                raise Exception("Exception writing AverageResult to SolidPod")
            print("AverageResult saved to pod")

            # Remove of local files
            os.remove(f"{mylocalfolder}/{cipherAddLocation}")
            os.remove(f"{mylocalfolder}/{ccLocation}")
            os.remove(f"{mylocalfolder}/{cipherAverageLocation}")

            j = j+1

        else:
            esiste = False
            print("CARTELLA NON TROVATA")


def node2_deserialize_compute_serialize_4Month():
    #I use the same schema as the previous method, but I need one value for the total consum in one month so I put in the variable of the sum the cipher value of the consum of the first day
    esiste = True
    mypodfolder = "Day1Aggregate"
    Solid_proxy.read_data_from_pod(mypodfolder, mylocalfolder, ccLocation)

    ciphertextAddLocation = 'ciphertextAdd1'

    Solid_proxy.read_data_from_pod(mypodfolder, mylocalfolder, ciphertextAddLocation)

    demarcate("Part 2b: Cryptocontext and data deserialization (Node 2)")
    node2CC, res = openfhe.DeserializeCryptoContext(f"{mylocalfolder}/{ccLocation}", openfhe.BINARY)
    if not res:
        raise Exception(f"I cannot deserialize the cryptocontext from {mylocalfolder}/{ccLocation}")

    print("Node2: Deserialized CryptoContex")

    cipherAdd, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{ciphertextAddLocation}", openfhe.BINARY)
    if not res:
            raise Exception(f"Cannot deserialize the ciphertext from {mylocalfolder}/{ciphertextAddLocation}")
    print(f"Node2: Deserialized ciphertextAddLocation\n")


    # Remove of local files
    #os.remove(f"{mylocalfolder}/{ccLocation}")
    #os.remove(f"{mylocalfolder}/{ciphertextAddLocation}")

    demarcate("Part 2c: Computation (Node 2)")
    node2CipherAdd = cipherAdd

    #I sum every daily consum in the variable of the monthlt consum but first I check if exists the day because I can also calculate the consum for only one day.
    j=2
    while esiste and j<31:
        mypodfolder = "Day"+str(j)+"Aggregate"

        if (Solid_proxy.url_exists(mypodfolder)):
            #Solid_proxy.read_data_from_pod(mypodfolder, mylocalfolder, ccLocation)

            #demarcate("Part 2b: Cryptocontext and data deserialization (Node 2)")

            ciphertextAddLocation = 'ciphertextAdd'+str(j)

            Solid_proxy.read_data_from_pod(mypodfolder, mylocalfolder, ciphertextAddLocation)

            demarcate("Part 2b: Cryptocontext and data deserialization (Node 2)")
            #node2CC, res = openfhe.DeserializeCryptoContext(f"{mylocalfolder}/{ccLocation}", openfhe.BINARY)
            #if not res:
                #raise Exception(f"I cannot deserialize the cryptocontext from {mylocalfolder}/{ccLocation}")

            #print("Node2: Deserialized CryptoContex")

            cipherAdd, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{ciphertextAddLocation}", openfhe.BINARY)
            if not res:
                raise Exception(f"Cannot deserialize the ciphertext from {mylocalfolder}/{ciphertextAddLocation}")
            print(f"Node2: Deserialized ciphertextAddLocation\n")


            # Remove of local files
            #os.remove(f"{mylocalfolder}/{ccLocation}")

            demarcate("Part 2c: Computation (Node 2)")



            # C1+C2
            node2CipherAdd = node2CC.EvalAdd(node2CipherAdd, cipherAdd)
            j = j+1
            # Node 2 serialize the result of the computation, to send it back to Node 1
        else:
            esiste = False
            print("CARTELLA NON TROVATA")


    demarcate("Part 2d: Serialization of data that has been operated on (Node 2)")
    openfhe.SerializeToFile(f"{mylocalfolder}/{cipherAddLocationMonth}", node2CipherAdd, openfhe.BINARY)

    demarcate("Part 2e: Saving computation result on SolidPod (Node2)")

    if not Solid_proxy.write_data_to_pod(podSum, mylocalfolder, cipherAddLocationMonth):
        raise Exception("Exception writing AddResult to SolidPod")
    print("AddResult saved to pod")

    #averageMonth
    Solid_proxy.read_data_from_pod_inverseMonth(mylocalfolder, inverseMonthLocation)
    cipherInverseMonth, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{inverseMonthLocation}", openfhe.BINARY)
    if not res:
        raise Exception(f"Cannot deserialize the ciphertext from {mylocalfolder}/{inverseMonthLocation}")
    print(f"Node2: Deserialized inverseMonthLocation\n")

    #calculate the monthly average
    node2CipherAverageM= node2CC.EvalMult(node2CipherAdd, cipherInverseMonth)

    openfhe.SerializeToFile(f"{mylocalfolder}/{cipherAverageLocationMonth}", node2CipherAverageM, openfhe.BINARY)

    demarcate("Part 2e: Saving computation result on SolidPod (Node2)")

    if not Solid_proxy.write_data_to_pod(podAverage, mylocalfolder, cipherAverageLocationMonth):
        raise Exception("Exception writing AverageResultMonth to SolidPod")
    print("AverageResultMonth saved to pod")

    k=1
    while k<31:
        # Remove of local files
        cipherAddLocation = 'ciphertextAdd'+str(k)
        os.remove(f"{mylocalfolder}/{cipherAddLocation}")
        k = k+1
    os.remove(f"{mylocalfolder}/{cipherAddLocationMonth}")
    os.remove(f"{mylocalfolder}/{cipherAverageLocationMonth}")
    os.remove(f"{mylocalfolder}/{inverseMonthLocation}")

    os.remove(f"{mylocalfolder}/{ccLocation}")


















