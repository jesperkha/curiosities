# A simple packet sniffer in C

If you are familiar with computer networking, you know that data packets are not actually sent only to the machine they are meant for, but are instead broadcast to the local network, and it is up to the NIC (Network Interface Card) to drop packets not meant for your computer. This allows us to be a bit _promiscuous_, which is also the name of the flag that disables this filter.

## Capturing raw Ethernet frames

Before we capture traffic on the whole network, let us start with our own machine. With the following code we create a socket that gives us raw ethernet frames fresh from the kernel:

```c
int sock_fd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
```

- `PF_PACKET`: Just get the raw packet data. No TCP/UDP parsing.
- `SOCK_RAW`: Required to use `PF_PACKET`.
- `ETH_P_ALL`: Get a socket that captures traffic from all network protocols.

Next we need to bind the socket to a network device. You can find a list of network device names with the `ifconfig` command. The one on my machine is called `wlo1`.

```c
const char *device_name = "wlo1";
setsockopt(sock_fd, SOL_SOCKET, SO_BINDTODEVICE, device_name, strlen(device_name)+1);
```

That's it! Reading from the socket with `recv()` will give raw packet data for any packets aimed at this machine. Note that you may need to run the program as root.

## Promiscuous mode

To capture all traffic on the network we need to enable _promiscuous mode_. This is a flag that instructs the kernel to tell the NIC not to drop packets not meant for us. Here is a function that enables it for a given socket:

```c
bool enable_promiscuous_mode(int sock_fd, const char *device_name)
{
    struct ifreq ethreq = {0};
    strncpy(ethreq.ifr_name, device_name, IF_NAMESIZE);

    // Get current flags for this socket
    if (ioctl(sock_fd, SIOCGIFFLAGS, &ethreq) == -1)
        return false;

    // Set the promisc flag
    ethreq.ifr_flags |= IFF_PROMISC;
    if (ioctl(sock_fd, SIOCSIFFLAGS, &ethreq) == -1)
        return false;

    return true;
}
```

If you are wondering, `SIOCGIFFLAGS` means Socket I/O Control Get Interface Flags, and the same with _set_ for `SIOCSIFF`. Truly an intuitive naming convention.

With this set up, you can capture all traffic on the local network and spy on your friends and family!

[Full example.](https://gist.github.com/jesperkha/fc8f375fc5566b129f8899f86d9d01c9)

