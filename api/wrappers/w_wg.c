#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main() {
    uid_t uid = getuid();
    setuid(0);
    system("/usr/bin/wg");
    setuid(uid);
    return 0;
}
