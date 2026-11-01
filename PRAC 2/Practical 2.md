### Study of network-related commands (Linux)


---

## Aim
> To study and use basic network-related commands in Linux.

## Requirements
- Computer or laptop with Linux (for example, Ubuntu or Kali Linux)
- Terminal application
- Active network or Internet connection
- Network utilities such as `ip`, `ping`, `ss`, and `ifconfig`; some exercises may also use `netstat`, `arp`, `curl`, `nslookup`, and `traceroute`

## Procedure
Open a terminal and run each command below. Observe the output; IP addresses, interfaces, routes, and connections depend on the computer and network.

### 1. `ifconfig`
Displays network interfaces and their address information. This older utility may need to be installed separately on some Linux distributions.

```bash
ifconfig
```

![[images/practical-2-000.png]]
*Example interface and address information.*

### 2. `ip addr`
Displays and manages network configuration. The `addr` subcommand lists interfaces and their addresses.

```bash
ip addr
```

![[images/practical-2-001.png]]
*Example `ip addr` output.*

### 3. `ping`
Checks whether a host is reachable and reports response times. On many Linux systems, `ping` continues until stopped with **Ctrl + C**.

```bash
ping google.com
```

![[images/practical-2-002.png]]
*Example ping replies.*

### 4. `netstat`
Displays network connections and listening ports. This command may be provided by the `net-tools` package.

```bash
netstat -tuln
```

The options show TCP and UDP sockets, listening ports, and numeric addresses.

![[images/practical-2-003.png]]
*Example listening sockets from `netstat`.*

### 5. `ss`
Displays socket information and is commonly used as a modern alternative to `netstat`.

```bash
ss -tuln
```

![[images/practical-2-004.png]]
*Example listening sockets from `ss`.*

### 6. `hostname`
Displays the computer's network name.

```bash
hostname
```

![[images/practical-2-005.png]]
*Example hostname output.*

### 7. `arp`
Displays the ARP table, which contains mappings between local network IP addresses and hardware addresses. The command may require the `net-tools` package.

```bash
arp -a
```

![[images/practical-2-006.png]]
*Example ARP entry.*

### 8. `curl`
Makes a request to a URL and prints the server response to the terminal. A site may respond with HTML or a redirect.

```bash
curl https://google.com
```

![[images/practical-2-007.png]]
*Example response from a web request.*

### 9. `nslookup`
Queries DNS for a domain and displays the responding DNS server and returned IP addresses.

```bash
nslookup google.com
```

![[images/screenshot_20261030_195256-region.png]]
*Example DNS lookup with IPv4 and IPv6 addresses in the response.*

### 10. `traceroute`
Shows the network hops toward a destination and the response times for probes sent to each hop. A `*` means a probe did not receive a response before timing out; it does not necessarily mean that the route is broken.

```bash
traceroute google.com
```

![[images/screenshot_20261030_195756-region.png]]
*Example route trace; some hops do not reply to probes.*

Either utility may need to be installed separately on some Linux distributions.

## Conclusion
> Linux network commands help inspect interface configuration, test connectivity, view sockets, check host names and ARP entries, and make requests to websites.

