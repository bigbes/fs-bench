#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
//#include <sys/fcntl.h>
#include <errno.h>

int main(){
    int fd = open("./tempfc", O_RDWR | O_CREAT);
    ssize_t ret;
    char c[] = "12345\n";
    while ((ret = write(fd, c, sizeof(c))) == sizeof(c));
    int sig = fcntl(fd, 11);
    printf("%d %d %d\n", ret, sig, errno);
    close(fd);
    return errno;
}
