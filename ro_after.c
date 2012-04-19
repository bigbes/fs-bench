#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>

int main(){
    int fd = open("./tempfc", O_RDWR | O_CREAT);
    int sig = fcntl(fd, 11);
    if (fd < 0){
        printf("%d %d %d\n", -2, sig, errno);
        return 0;
    }
    sleep(3);

    ssize_t ret;
    char c[] = "12345\n";

    while ((ret = write(fd, c, sizeof(c))) == sizeof(c));
    sig = fcntl(fd, 11);

    printf("%d %d %d\n", ret, sig, errno);

    close(fd);
    return errno;
}
