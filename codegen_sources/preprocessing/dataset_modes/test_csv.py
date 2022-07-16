import csv 
if __name__ == '__main__':

    dict_path = '/home/carl/AnghaBench_dict/freebsd/tools/tools/net80211/wesside/wesside/extr_wesside.c_read_packet.csv'
    with open(dict_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        mydict = {rows[0]:rows[1] for rows in reader}
        print(mydict)
        print(sorted(mydict))