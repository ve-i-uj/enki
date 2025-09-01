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

<a name="msgreader"><h2>Message Reader</h2></a>

There is [a script](tools/msgreader.py) that can be used to analyze network traffic between KBEngine components. Using the script, you can analyze both KBEngine messages in an envelope (when its id and length are passed in the message head), and bare messages to a callback address (bare messages doesn't have a message id and its length and sent to a specific port opened by the component).

WireShark is used to capture traffic. Next, you need to select a package between the KBEngine server components and copy the package data in hexadecimal form.

![msgreader_example](https://github.com/ve-i-uj/enki/assets/6612371/2da966da-f9d1-4cd3-8ced-546124286064)

For the `msgreader` script to work in Python, you need to activate the Python virtual environment. You need [to activate]() it once and then use the script.

The script needs to get the message destination component and the binary data copied in hexadecimal form. The script deserializes the data and displays it in the console in a convenient readable format. Fields with double underscores are added by the script itself for easy reading, these fields were not sent in the message. For example, the `addr` and `finderRecvPort` fields in the message are encoded. The handler of this message adds the `__callback_address` field to the result, in which the address is already in a clear and familiar form.

In this case, the request is sent to the Machine component. The output of the script shows that the Baseapp component requests the address of the Logger component and asks to send a response to the address 172.24.0.9:20747.

```console
(enki) leto@leto-PC:/tmp/enki$ python tools/msgreader.py machine 01002300e80300006b62656e67696e650006000000591b0000000000000a000000ac180009510b
[INFO] 2023-06-10 11:34:48,908 [msgreader.py:168 - main()] *** Machine::onFindInterfaceAddr (id = 1) ***
{   'msg_id': 1,
    'result': {   '__callback_address': AppAddr(host='172.24.0.9', port=20747),
                  '__component_type': <ComponentType.BASEAPP: 6>,
                  '__find_component_type': <ComponentType.LOGGER: 10>,
                  'addr': 151001260,
                  'componentID': 7001,
                  'componentType': 6,
                  'findComponentType': 10,
                  'finderRecvPort': 2897,
                  'uid': 1000,
                  'username': 'kbengine'},
    'success': True,
    'text': ''}
```

Further, in the traffic captured by WireShark, we find the response to this message, because the reply address is known (172.24.0.9:20747).

![callback_response](https://github.com/ve-i-uj/enki/assets/6612371/2436b950-b046-49a6-b31a-1c11c3409099)

The KBEngine sources know which message will be sent in response and that the response will be sent without an envelope (i.e. without the message id and its length). In this case, to deserialize the message, the script needs to be know what the message is in the `--bare-msg` argument (--bare-msg "Machine::onBroadcastInterface"). The argument must come after the data.

<details>

<summary>The example of reading "Machine::onBroadcastInterface"</summary>

```console
(enki) leto@leto-PC:/tmp/enki$ python tools/msgreader.py machine e80300006b62656e67696e65000a000000d107000000000000591b000000000000ffffffffffffffffffffffffac180004ec35ac1800049dad0007000000000000000000000000f031010000000000000000000000000000000000000000000000000000000000d084000000000000ac1800044f82 --bare-msg "Machine::onBroadcastInterface"
[INFO] 2023-06-10 11:54:22,014 [msgreader.py:130 - main()] *** Machine::onBroadcastInterface (id = 8) ***
{   'msg_id': 8,
    'result': {   '__callback_address': AppAddr(host='172.24.0.4', port=20354),
                  '__component_type': <ComponentType.LOGGER: 10>,
                  '__external_address': AppAddr(host='172.24.0.4', port=40365),
                  '__internal_address': AppAddr(host='172.24.0.4', port=60469),
                  'backRecvAddr': 67115180,
                  'backRecvPort': 33359,
                  'componentID': 2001,
                  'componentIDEx': 7001,
                  'componentType': 10,
                  'cpu': 0.0,
                  'extaddr': 67115180,
                  'extaddrEx': '',
                  'extport': 44445,
                  'extradata': 0,
                  'extradata1': 0,
                  'extradata2': 0,
                  'extradata3': 34000,
                  'globalorderid': -1,
                  'grouporderid': -1,
                  'gus': -1,
                  'intaddr': 67115180,
                  'intport': 13804,
                  'machineID': 0,
                  'mem': 0.0,
                  'pid': 7,
                  'state': 0,
                  'uid': 1000,
                  'usedmem': 20049920,
                  'username': 'kbengine'},
    'success': True,
    'text': ''}
```

</details>
<br/>

As you can see from the response, the Machine component sends the data of the Logger component to the callback address.

Implemented messages are listed [here](enki/handler/serverhandler/__init__.py)
