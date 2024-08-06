import openfhe
import numpy as np
import Solid_proxy
import os

# FILES PATH DEFINITION

# Save-Load locations for keys
mylocalfolder = "LocalData"
cipherMultLocation = 'ciphertextMult'
ccLocation = 'cryptocontext'
pubKeyLocation = 'key_pub'  # Pub key
multKeyLocation = 'key_mult'  # relinearization key

inverseDayLocation = 'inverseDay'
inverseMonthLocation = 'inverseMonth'

cipherTextFile = []
numberText = 48
#name of the the file that I saved the cipher consum each 30 minutes
for i in range(numberText):
    cipherTextFile.append('cipherText'+str(i))
inverseDay = 1/numberText

def demarcate(msg):
    print("**************************************************")
    print(msg)
    print("**************************************************\n")


###
#  node1SetupEncryptSerialize
#  - Setup Crypto Context
#  - Encrypt data
#  - Serialize data to files
#  - Save data to Pod
##

def node1_encrypt_serialize_4Day_firstDay(v,scaleModSize,batchSize, multDepth, day, dataForMonth):

    inverseMonth = 1/dataForMonth

    demarcate("Part 1a: CryptoContext generation (Node 1)")

    mypodfolder = "Day"+str(day)+"ForHour"

    sumpodfolder = "Day"+str(day)+"Aggregate"
    # CryptoContex CKKS parameters definition
    parameters = openfhe.CCParamsCKKSRNS()
    parameters.SetScalingModSize(scaleModSize)
    parameters.SetBatchSize(batchSize)
    parameters.SetMultiplicativeDepth(multDepth)


    # CryptoContext generation
    node1CC = openfhe.GenCryptoContext(parameters)

    # CryptoContext features enabling
    node1CC.Enable(openfhe.PKE)
    node1CC.Enable(openfhe.KEYSWITCH)
    node1CC.Enable(openfhe.LEVELEDSHE)

    print("Node1: Cryptocontext generated")

    # KeyPair generation
    node1KP = node1CC.KeyGen()
    print("Node1: Keypair generated")


    # Multiplication key generation
    node1CC.EvalMultKeyGen(node1KP.secretKey)
    print("Node1: Eval Mult Keys/ Relinearization keys have been generated")


    demarcate("Part 1b: Data packing and encryption (Node 1)")

    #cipher the consumption per 30 minutes
    plainText = []
    cipherText = []
    for number in v:
        node1P = node1CC.MakeCKKSPackedPlaintext([number])
        plainText.append(node1P)
        node1C = node1CC.Encrypt(node1KP.publicKey, node1P)
        cipherText.append(node1C)
    #cipher inverse value of day
    inverseDayP = node1CC.MakeCKKSPackedPlaintext([inverseDay])
    inverseDayC = node1CC.Encrypt(node1KP.publicKey,inverseDayP)

    #cipher inverse value of month
    inverseMonthP =  node1CC.MakeCKKSPackedPlaintext([inverseMonth])
    inverseMonthC = node1CC.Encrypt(node1KP.publicKey, inverseMonthP)


    #    Part 1c:
    #    We serialize the following:
    #      Cryptocontext
    #      Public key
    #      Some of the ciphertext
    #
    #      We serialize all of them to files
    ###

    demarcate("Part 1c: Data Serialization (Node 1)")


    if not openfhe.SerializeToFile(f"{mylocalfolder}/{ccLocation}", node1CC, openfhe.BINARY):
        raise Exception("Exception writing cryptocontext to cryptocontext.txt")
    print("Cryptocontext serialized")

    if not openfhe.SerializeToFile(f"{mylocalfolder}/{pubKeyLocation}", node1KP.publicKey, openfhe.BINARY):
        raise Exception("Exception writing public key to pubkey.txt")
    print("Public key has been serialized")


    if not node1CC.SerializeEvalMultKey(f"{mylocalfolder}/{multKeyLocation}", openfhe.BINARY):
        raise Exception("Error writing eval mult keys")
    print("EvalMult/ relinearization keys have been serialized")


    if not openfhe.SerializeToFile(f"{mylocalfolder}/{inverseDayLocation}", inverseDayC, openfhe.BINARY):
        raise Exception("Error writing inverseDay")

    if not openfhe.SerializeToFile(f"{mylocalfolder}/{inverseMonthLocation}", inverseMonthC, openfhe.BINARY):
        raise Exception("Error writing inverseMonth")

    for i in range(len(cipherText)):
        if not openfhe.SerializeToFile(f"{mylocalfolder}/{cipherTextFile[i]}", cipherText[i], openfhe.BINARY):
            raise Exception("Error writing ciphertext"+ str(i))

    # Part 1d: Saving generated files from my local folder to my pod

    demarcate("Part 1d: Saving data into SolidPod (Node 1)")

    if not Solid_proxy.write_data_to_pod(mypodfolder, mylocalfolder, ccLocation):
        raise Exception("Exception writing cryptocontext to SolidPod")
    print("Cryptocontext saved to pod")

    if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder, pubKeyLocation):
        raise Exception("Exception writing public key to SolidPod")
    print("Public key saved to pod")

    if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder, multKeyLocation):
        raise Exception("Error writing eval mult keys to SolidPod")
    print("EvalMult/ relinearization keys saved to pod")

    if not Solid_proxy.write_inverse(mylocalfolder, inverseDayLocation):
        raise Exception("Error writing inverseDay to SolidPod")

    if not Solid_proxy.write_inverse(mylocalfolder, inverseMonthLocation):
        raise Exception ("Error writing inverseMonth to SolidPod")

    for i in range(len(cipherTextFile)):
        if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder,         cipherTextFile[i]):
            raise Exception("Error writing ciphertext "+ str(i)+ " to SolidPod")


    # Remove of local files
    os.remove(f"{mylocalfolder}/{ccLocation}")
    os.remove(f"{mylocalfolder}/{pubKeyLocation}")
    os.remove(f"{mylocalfolder}/{multKeyLocation}")
    os.remove(f"{mylocalfolder}/{inverseDayLocation}")
    os.remove(f"{mylocalfolder}/{inverseMonthLocation}")

    for cipherText in cipherTextFile:
        os.remove(f"{mylocalfolder}/{cipherText}")
    return (node1CC, node1KP)


def node1_encrypt_serialize_4Day(v,scaleModSize,batchSize, multDepth, day, node1CC, node1KP):
    demarcate("Part 1a: CryptoContext generation (Node 1)")

    mypodfolder = "Day"+str(day)+"ForHour"

    evaluatorpodfolder = "Day"+str(day)+"Aggregate"
    '''
    # CryptoContex CKKS parameters definition
    parameters = openfhe.CCParamsCKKSRNS()
    parameters.SetScalingModSize(scaleModSize)
    parameters.SetBatchSize(batchSize)


    # CryptoContext generation
    node1CC = openfhe.GenCryptoContext(parameters)

    # CryptoContext features enabling
    node1CC.Enable(openfhe.PKE)
    node1CC.Enable(openfhe.KEYSWITCH)
    node1CC.Enable(openfhe.LEVELEDSHE)

    print("Node1: Cryptocontext generated")

    # KeyPair generation
    node1KP = node1CC.KeyGen()
    print("Node1: Keypair generated")

    demarcate("Part 1b: Data packing and encryption (Node 1)")
'''
    #cipher the consumption per 30 minutes
    plainText = []
    cipherText = []
    for number in v:
        node1P = node1CC.MakeCKKSPackedPlaintext([number])
        plainText.append(node1P)
        node1C = node1CC.Encrypt(node1KP.publicKey, node1P)
        cipherText.append(node1C)

    inverseDayP = node1CC.MakeCKKSPackedPlaintext([inverseDay])
    inverseDayC = node1CC.Encrypt(node1KP.publicKey, inverseDayP)

    #    Part 1c:
    #    We serialize the following:
    #      Cryptocontext
    #      Public key
    #      Some of the ciphertext
    #
    #      We serialize all of them to files
    ###

    demarcate("Part 1c: Data Serialization (Node 1)")


    if not openfhe.SerializeToFile(f"{mylocalfolder}/{ccLocation}", node1CC, openfhe.BINARY):
        raise Exception("Exception writing cryptocontext to cryptocontext.txt")
    print("Cryptocontext serialized")

    if not openfhe.SerializeToFile(f"{mylocalfolder}/{pubKeyLocation}", node1KP.publicKey, openfhe.BINARY):
        raise Exception("Exception writing public key to pubkey.txt")
    print("Public key has been serialized")

    if not node1CC.SerializeEvalMultKey(f"{mylocalfolder}/{multKeyLocation}", openfhe.BINARY):
        raise Exception("Error writing eval mult keys")
    print("EvalMult/ relinearization keys have been serialized")

    if not openfhe.SerializeToFile(f"{mylocalfolder}/{inverseDayLocation}", inverseDayC, openfhe.BINARY):
        raise Exception("Error writing inverseDay")

    for i in range(len(cipherText)):
        if not openfhe.SerializeToFile(f"{mylocalfolder}/{cipherTextFile[i]}", cipherText[i], openfhe.BINARY):
            raise Exception("Error writing ciphertext"+ str(i))

    # Part 1d: Saving generated files from my local folder to my pod

    demarcate("Part 1d: Saving data into SolidPod (Node 1)")

    if not Solid_proxy.write_data_to_pod(mypodfolder, mylocalfolder, ccLocation):
        raise Exception("Exception writing cryptocontext to SolidPod")
    print("Cryptocontext saved to pod")

    if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder, pubKeyLocation):
        raise Exception("Exception writing public key to SolidPod")
    print("Public key saved to pod")

    if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder, multKeyLocation):
        raise Exception("Error writing eval mult keys to SolidPod")
    print("EvalMult/ relinearization keys saved to pod")

    if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder, inverseDayLocation):
        raise Exception("Error writing inverseDay to SolidPod")

    for i in range(len(cipherTextFile)):
        if not Solid_proxy.write_data_to_pod(mypodfolder,mylocalfolder,         cipherTextFile[i]):
            raise Exception("Error writing ciphertext "+ str(i)+ " to SolidPod")


    # Remove of local files
    os.remove(f"{mylocalfolder}/{ccLocation}")
    os.remove(f"{mylocalfolder}/{pubKeyLocation}")
    os.remove(f"{mylocalfolder}/{multKeyLocation}")
    os.remove(f"{mylocalfolder}/{inverseDayLocation}")

    for cipherText in cipherTextFile:
        os.remove(f"{mylocalfolder}/{cipherText}")
    return (node1CC, node1KP)


###
#  node1DeserializeDecryptVerify
#  - Download data from Node2 pod
#  - deserialize data from the client.
#  - Verify that the results are as we expect
# @params v1,v2 vectors for result verification
# @param cc cryptocontext that was previously generated
# @param kp keypair that was previously generated
# @param vectorSize vector size of the vectors supplied
# @return
#  5-tuple of the plaintexts of various operations
# the two methodss have the same schema
##
def node1_deserialize_decrypt_verify_4Day(v, cc, kp, day):
    cipherAddLocation = 'ciphertextAdd'+str(day)
    cipherAverageLocation = 'cipherAverage'+str(day)

    demarcate("Part 3a: Read computed data from Node2's pod and write them in my local folder (Node 1)")

    evaluatorpodfolder = "Day"+str(day)+"Aggregate"

    Solid_proxy.read_data_from_pod(evaluatorpodfolder, mylocalfolder, cipherAddLocation)
    Solid_proxy.read_data_from_pod(evaluatorpodfolder, mylocalfolder, cipherAverageLocation)

    demarcate("Part 3b: Result deserialization (Node 1)")
    node1CiphertextFromNode2_Add, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{cipherAddLocation}", openfhe.BINARY)
    node1CiphertextFromNode2_Average, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{cipherAverageLocation}", openfhe.BINARY)
    print("Deserialized all data from client on server\n")


    # Remove of local files
    os.remove(f"{mylocalfolder}/{cipherAddLocation}")
    os.remove(f"{mylocalfolder}/{cipherAverageLocation}")

    demarcate("Part 3c: Result Decryption (Node 1)")
    node1PlaintextFromNode2_Add = cc.Decrypt(kp.secretKey, node1CiphertextFromNode2_Add)
    node1PlaintextFromNode2_Add.SetLength(1)

    node1PlaintextFromNode2_Average = cc.Decrypt(kp.secretKey, node1CiphertextFromNode2_Average)
    node1PlaintextFromNode2_Average.SetLength(1)

    demarcate("Part 3d: Result Verification (Node 1)")



    expected_sum = v[0]
    for i in range(1,len(v)):
        expected_sum = expected_sum + v[i]
    print(f"Consum for day {day} EXPECTED = {expected_sum} ACTUAL = {node1PlaintextFromNode2_Add}")

    averageExpected = expected_sum/len(v)
    print(f"Average of the day {day} EXPECTED = {averageExpected} ACTUAL = {node1PlaintextFromNode2_Average}")

    return expected_sum


def node1_deserialize_decrypt_verify_4Month(v, cc, kp, dataForMonth):

    demarcate("Part 3a: Read computed data from Node2's pod and write them in my local folder (Node 1)")
    cipherAddLocation = 'ciphertextAddMonth'
    cipherAverageLocation = 'ciphertextAverageMonth'


    sumpodfolder = "podSum"
    averagepodfolder = "podAverageMonth"
    Solid_proxy.read_data_from_pod(sumpodfolder, mylocalfolder, cipherAddLocation)
    Solid_proxy.read_data_from_pod(averagepodfolder, mylocalfolder, cipherAverageLocation)

    demarcate("Part 3b: Result deserialization (Node 1)")
    node1CiphertextFromNode2_Add, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{cipherAddLocation}", openfhe.BINARY)
    print(node1CiphertextFromNode2_Add)
    node1CiphertextFromNode2_Average, res = openfhe.DeserializeCiphertext(f"{mylocalfolder}/{cipherAverageLocation}", openfhe.BINARY)
    print("Deserialized all data from client on server\n")


    # Remove of local files
    os.remove(f"{mylocalfolder}/{cipherAddLocation}")
    os.remove ( f"{mylocalfolder}/{cipherAverageLocation}")

    demarcate("Part 3c: Result Decryption (Node 1)")
    node1PlaintextFromNode2_Add = cc.Decrypt(kp.secretKey, node1CiphertextFromNode2_Add)
    node1PlaintextFromNode2_Add.SetLength(1)

    node1PlaintextFromNode2_Average = cc.Decrypt(kp.secretKey, node1CiphertextFromNode2_Average)
    node1PlaintextFromNode2_Average.SetLength(1)
    demarcate("Part 3d: Result Verification (Node 1)")



    expected_sum = v[0]
    for i in range(1,len(v)):
        expected_sum = expected_sum + v[i]
    print(f"Consum for month EXPECTED = {expected_sum} ACTUAL = {node1PlaintextFromNode2_Add}")

    averageExpected = expected_sum/dataForMonth
    print(f"Average for month EXPECTED = {averageExpected} ACTUAL = {node1PlaintextFromNode2_Average}")








