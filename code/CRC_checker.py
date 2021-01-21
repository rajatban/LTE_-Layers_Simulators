import random
def perform_xor(s1,s2):
    """
    Returns xor of s1,s2 of same length
    """
    out=''
    n=len(s1)
    for i in range(1,n):
        if(s1[i]==s2[i]):
            out+='0'
        else:
            out+='1'
    return out

def bin_division(divident,divisor):
    """
    Returns remainder of the binary polynomial division
    """
    k=len(divisor)
    curr=divident[:k]
    while k < len(divident): 
        if curr[0] == '1':
            curr=perform_xor(divisor,curr)+divident[k] 
        else:
            curr=perform_xor('0'*len(divisor),curr)+divident[k] 
        k+=1
    if curr[0] == '1': 
        curr = perform_xor(divisor, curr) 
    else: 
        curr = perform_xor('0'*len(divisor), curr) 
    rem=curr 
    return rem

def sender(data_to_send,CRC_polynomial):
    """
    Returns the final code word to be sent.
    """
    m=len(CRC_polynomial)
    n=m-1
    data=data_to_send + '0'*n       #Appending n zeros
    rem=bin_division(data,CRC_polynomial)
    out_data=data_to_send+rem
    return rem,out_data

def reciever(data_recieved,CRC_polynomial):
    """
    Returns whether recieved data contains error
    """
    checker=bin_division(data_recieved,CRC_polynomial)
    for i in checker:
        if i=='1':
            return -1
    return 0

def main():
    """
    Testing the functions
    """
    data="1101011011"
    CRC="10011"
    rem,out_data=sender(data,CRC)
    print("Remainder :"+rem)
    print("Encoded data : "+out_data)
    rec_data=''
    for i in out_data:
        if random.uniform(0,1)>=0.95:
            if i=='1':
                rec_data+='0'
            else:
                rec_data+='1'
        else:
            rec_data+=i
    print("Recieved data: "+rec_data)
    check_reciever=reciever(rec_data,CRC)
    if check_reciever==0:
        print("No errors")
    else:
        print("Error in transmission")
if __name__ == '__main__':
    main()