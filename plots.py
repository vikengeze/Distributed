import matplotlib.pyplot as plt
time_insert_linear = [62.6175,73.6560,80.1584]
thr_insert_linear = [0.1252,0.1473,0.1603]
time_insert_eventual =[62.4511,62.7700,63.0668]
thr_insert_eventual = [0.1249,0.1255,0.1261]
time_query_linear = [15.0230,16.0701,16.7400]
thr_query_linear = [0.0300,0.03214,0.03348]
time_query_eventual = [15.6715,10.4865,7.0886]
thr_query_eventual = [0.0313,0.0210,0.0142]
k=[1,3,5]

plt.figure(figsize=(8,8))
plt.bar(k,time_insert_linear)
for index,time in zip(k,time_insert_linear):
    plt.text(index-0.25,time+0.3,'{:.4f}'.format(time))
plt.xlabel('Replication Factor')
plt.ylabel('Time (sec)')
plt.title('Insert time with linearizability')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_linear_time')

plt.figure(figsize=(8,8))
plt.bar(k,thr_insert_linear)
for index,throughput in zip(k,thr_insert_linear):
    plt.text(index-0.25,throughput+0.001,'{:.4f}'.format(throughput))
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#inserts)')
plt.title('Write throughput with linearizability')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_linear_throughput')

plt.figure(figsize=(8,8))
plt.bar(k,time_insert_eventual)
for index,time in zip(k,time_insert_eventual):
    plt.text(index-0.25,time+0.1,'{:.4f}'.format(time))
plt.xlabel('Replication Factor')
plt.ylabel('Time (sec)')
plt.title('Insert time with eventual consistency')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_eventual_time')

plt.figure(figsize=(8,8))
plt.bar(k,thr_insert_eventual)
for index,throughput in zip(k,thr_insert_eventual):
    plt.text(index-0.25,throughput+0.001,'{:.4f}'.format(throughput))
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#inserts)')
plt.title('Write throughput with eventual consistency')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_eventual_throughput')

plt.figure(figsize=(8,8))
plt.bar(k,time_query_linear)
for index,time in zip(k,time_query_linear):
    plt.text(index-0.25,time+0.1,'{:.4f}'.format(time))
plt.xlabel('Replication Factor')
plt.ylabel('Time (sec)')
plt.title('Query time with linearizability')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/query_linear_time')

plt.figure(figsize=(8,8))
plt.bar(k,thr_query_linear)
for index,throughput in zip(k,thr_query_linear):
    plt.text(index-0.25,throughput+0.0002,'{:.4f}'.format(throughput))
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#queries)')
plt.title('Read throughput with linearizability')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/query_linear_throughput')

plt.figure(figsize=(8,8))
plt.bar(k,time_query_eventual)
for index,time in zip(k,time_query_eventual):
    plt.text(index-0.25,time+0.1,'{:.4f}'.format(time))
plt.xlabel('Replication Factor')
plt.ylabel('Time (sec)')
plt.title('Query time with eventual consistency')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/query_eventual_time')

plt.figure(figsize=(8,8))
plt.bar(k,thr_query_eventual)
for index,throughput in zip(k,thr_query_eventual):
    plt.text(index-0.25,throughput+0.0002,'{:.4f}'.format(throughput))
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#queries)')
plt.title('Read throughput with eventual consistency')
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/query_eventual_throughput')
############################################################
plt.figure(figsize=(8,8))
width=0.4
ticks_pos = list(map(lambda x:x+width/2,k))
k_left = list(map(lambda x:x+width,k))
plt.bar(k,thr_query_eventual,width=width,color='darkcyan',label='Eventual Consistency')
plt.bar(k_left,thr_query_linear,width=width,color='skyblue',label='Linearizability')
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#queries)')
plt.title('Read throughput')
plt.legend()
plt.xticks(ticks_pos, ('1','3', '5'))
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/read_troughput')

plt.figure(figsize=(8,8))
width=0.4
plt.bar(k,thr_insert_eventual,width=width,color='darkcyan',label='Eventual Consistency')
plt.bar(k_left,thr_insert_linear,width=width,color='skyblue',label='Linearizability')
plt.xlabel('Replication Factor')
plt.ylabel('Throughput (sec/#inserts)')
plt.title('Write throughput')
plt.legend()
plt.xticks(ticks_pos, ('1','3', '5'))
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/write_troughput')

plt.figure(figsize=(8,8))
width=0.4
plt.bar(k,time_query_eventual,width=width,color='darkcyan',label='Eventual Consistency')
plt.bar(k_left,time_query_linear,width=width,color='skyblue',label='Linearizability')
plt.xlabel('Replication Factor')
plt.ylabel('Time (s)')
plt.title('Query Times')
plt.legend()
plt.xticks(ticks_pos, ('1','3', '5'))
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_time')

plt.figure(figsize=(8,8))
width=0.4
plt.bar(k,time_insert_eventual,width=width,color='darkcyan',label='Eventual Consistency')
plt.bar(k_left,time_insert_linear,width=width,color='skyblue',label='Linearizability')
plt.xlabel('Replication Factor')
plt.ylabel('Time (s)')
plt.title('Insert Times')
plt.legend()
plt.xticks(ticks_pos, ('1','3', '5'))
plt.savefig('/Users/Savas/Downloads/Chord_PIO_FINAL/chord_plots/insert_times')