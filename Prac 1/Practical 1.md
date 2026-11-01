### Study of network-related commands (Windows)


---

## Aim
> To study and execute different network-related commands available in Windows.

## Requirements
- Windows computer
- Command Prompt (CMD)
- Internet or network connection

## Procedure
Open Command Prompt by pressing **Windows + R**, entering `cmd`, and pressing **Enter**. Run each command below and observe its output. Results vary by computer and network.

### 1. `ipconfig`
Displays IP configuration, including the IP address, subnet mask, and default gateway.

```cmd
ipconfig
```

![[images/practical-1-000.png]]
*Example `ipconfig` output.*

### 2. `ping`
Checks whether a destination can be reached and reports response times and packet loss.

```cmd
ping google.com
```

![[images/practical-1-001.png]]
*Example ping replies and statistics.*

### 3. `tracert`
Shows the network hops taken by packets on the way to a destination.

```cmd
tracert google.com
```

![[images/practical-1-002.png]]
*Example route trace. A timeout at a hop can occur when a router does not respond to probes.*

### 4. `nslookup`
Queries DNS to find the address associated with a domain name and shows the DNS server used.

```cmd
nslookup google.com
```

![[images/practical-1-003.png]]
*Example DNS lookup output.*

### 5. `netstat`
Displays active TCP connections. To include listening ports and show numeric addresses, use the optional flags below:

```cmd
netstat
netstat -ano
```

![[images/practical-1-004.png]]
*Example active connections.*

### 6. `arp`
Displays the ARP cache, which maps local network IP addresses to physical (MAC) addresses.

```cmd
arp -a
```

![[images/practical-1-005.png]]
*Example ARP table.*

### 7. `route`
Displays the computer's routing table.

```cmd
route print
```

![[images/practical-1-006.png]]
*Example routing table.*

### 8. `hostname`
Displays the computer's network name.

```cmd
hostname
```

![[images/practical-1-007.png]]
*Example computer name.*

### 9. `getmac`
Displays the physical (MAC) addresses of network adapters.

```cmd
getmac
```

![[images/practical-1-008.png]]
*Example adapter MAC addresses.*

### 10. `pathping`
Combines route tracing with checks for delay and packet loss along the path. It may take time to complete.

```cmd
pathping google.com
```

![[images/practical-1-009.png]]
*Example path and packet-loss statistics.*

## Conclusion
> Windows network commands help inspect IP configuration, test connectivity, resolve domain names, view routes and MAC addresses, and troubleshoot connections.

