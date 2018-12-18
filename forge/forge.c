#include <arpa/inet.h> /* Standard for socketprogramming */
#include <netinet/ip.h> /* For the ip header */
#include <netinet/udp.h>
#include <sys/types.h> /* Some macros */
#include <sys/socket.h> /* Also standard for socketprogramming */
#include <string.h>

struct packet {
    struct iphdr ip;
    struct udphdr udp;
    char data[512];
};

#define SRCADDR "192.168.1.10"
#define DESTADDR "192.168.1.1"

#define SRCPORT 1337
#define DESTPORT 80

int main()
{
    struct packet pk;
    memset(&pk,0,sizeof(pk));

    strcat(pk.data, "Hello, World");

    /* Filling in IP Header */
    pk.ip.ihl = 5;
    pk.ip.version = 4;
    pk.ip.tos = 0;
    pk.ip.tot_len = htons(sizeof(struct packet));
    pk.ip.id = htons(300);
    pk.ip.frag_off =  0x000;
    pk.ip.ttl = 64;
    pk.ip.protocol = IPPROTO_UDP; 
    pk.ip.check = 0;
    pk.ip.saddr = inet_addr(SRCADDR);
    pk.ip.daddr = inet_addr(DESTADDR);

    /* Filling in UDP Header */
    pk.udp.source = htons(SRCPORT);
    pk.udp.dest = htons(DESTPORT);
    pk.udp.len = htons(sizeof(pk)-sizeof(pk.ip));
    pk.udp.check = 0;

    /* Doing the socket stuff */
    int sock; 
    sock = socket(AF_INET,SOCK_RAW,IPPROTO_RAW);

    struct sockaddr_in daddr;

    daddr.sin_family = AF_INET;
    daddr.sin_addr.s_addr = inet_addr(DESTADDR);
    daddr.sin_port = htons(DESTPORT);
    memset(&daddr.sin_zero, 0, sizeof(daddr.sin_zero));

    int i;
    while(1) {
        sendto( sock, (char *) &pk, sizeof(pk), 0, (struct sockaddr *) &daddr, (socklen_t) sizeof(daddr));
    }
}
