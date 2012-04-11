#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>

int main(){
    int fd = open("./tempfc", O_RDWR | O_CREAT | O_APPEND);
    if ( fchmod(fd, S_IRWXU | S_IRWXG | S_IRWXO))
        printf("Error, while chmod");

   	ssize_t ret;
    unsigned int i=0;

    char c[] = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \n\
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n\
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n\
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n";

    while ((ret = write(fd, c, sizeof(c))) == sizeof(c)) i++;

    int sig = fcntl(fd, 11);
    printf("%d %d %d %u", ret, sig, errno, i);

    close(fd);
    return errno;
}
