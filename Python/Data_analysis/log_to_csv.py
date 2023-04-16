from new_Packet import Packet, PacketType, Command

def filter_packets(line):
    line_elements = line.split('::')
    # print(line_elements)
    
    if line_elements[1] =='PACKET' and Packet.from_json(line_elements[2]).packet_type != PacketType.COMMAND:
        return True
    return False

def load_log(file_name: str):
    with open(file_name, 'r') as f:
        return  [Packet.from_json(i.split('::')[2]) for i in filter(filter_packets, f.readlines())]
    
def write_csv():
    base = []
    ext = []
    for i in load_log('log.out'):
        if i.packet_type == PacketType.BASE:
            base.append(i.encode().split(';')[1:])
        elif i.packet_type == PacketType.EXTENDED:
            ext.append(i.encode().split(';')[1:])
    
    base_csv = '\n'.join((','.join(i) for i in base))
    print(base_csv)
    with open('base.csv', 'w') as f:
        f.write(base_csv)
    
    ext_csv = '\n'.join((','.join(i) for i in ext))
    print(ext_csv)
    with open('extended.csv', 'w') as f:
        f.write(ext_csv)
    
    
    
write_csv()