import time
import random
import socket

PING_COUNT = 15
TIMEOUT = 0.6

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

server_add = ('127.0.0.1', 12000) #self IP

RTTS = [] # 存储 RTT
count = 0 #计算响应的ping
start_time = time.time() #时间戳
sequence_num = random.randint(10000, 20000)

for i in range(PING_COUNT):
    send_time = time.time()
    message = f'PING {sequence_num + i} {send_time}'

    try:
        client_socket.sendto(message.encode(), server_add)
        response, _ = client_socket.recvfrom(1024)
        receive_time = time.time()
        RTT = (receive_time - send_time) * 1000 #毫秒换算
        RTTS.append(RTT) #存放rtt
        count += 1

        print(f'PING to {server_add[0]}, seq={sequence_num + i}, rtt={int(RTT)} ms')
    except socket.timeout:
        print(f'PING to {server_add[0]}, seq={sequence_num + i}, rtt=timeout')

end_time = time.time()
total_time = (end_time - start_time) * 1000
packet_loss = (PING_COUNT - count) / PING_COUNT * 100
min_RTT = min(RTTS) if RTTS else 0 #不存在为0
max_RTT = max(RTTS) if RTTS else 0
avg_RTT = sum(RTTS) / len(RTTS) if RTTS else 0
jitter = sum([abs(RTTS[i] - RTTS[i-1]) for i in range(1, len(RTTS))]) / (len(RTTS) - 1) if len(RTTS) > 1 else 0

#output
print(f'Total packets sent: {PING_COUNT}')
print(f'Packets acknowledged: {count}')
print(f'Packet loss: {int(packet_loss)}%')
print(f'Minimum RTT: {int(min_RTT)} ms, Maximum RTT: {int(max_RTT)} ms, Average RTT: {int(avg_RTT)} ms')
print(f'Total transmission time: {int(total_time)}ms')
print(f'Jitter: {int(jitter)} ms')


