## Просмотр только сообщений в файле pcap (полученного tcpdump'ом)

```bash
tshark -r /tmp/merged.pcap -Y "ip.dst == 172.19.0.11 and tcp.flags.push == 1" -T fields \
   -e frame.time \
   -e ip.src \
   -e ip.dst \
   -e tcp.srcport \
   -e tcp.dstport \
   -e data \
   -E separator="|" \
   -E occurrence=f \
   |  python tools/msgreader loginapp --read-stdin --log-level=INFO
```
