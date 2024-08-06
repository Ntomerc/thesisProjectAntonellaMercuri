import time

import Node2OneDay

# 2 containers for nodes + container with storage on SolidPod. Intermediate serialization to files is required (python wrapper does not support serialize to streams at this stage)

def main():
    # Step 1
    time.sleep(120)      # Wait for Node1 to encrypt data and store them in the Pod

    # Step 2
    #deserialize and compute the consumption for a single day
    Node2OneDay.node2_deserialize_compute_serialize_4Day()

    time.sleep(40)
    #deserialize and compute the consumption for a single month
    Node2OneDay.node2_deserialize_compute_serialize_4Month()
    # Step 3

if __name__ == '__main__':
    main()
