#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char ** const argv) {
    uid_t uid = getuid();
	setuid(0);

	char cmd[] = "/usr/sbin/smartctl -i -a --json ";
	char cmd_full[100];
	strcpy(cmd_full, cmd);
	strcat(cmd_full, argv[1]);
	system(cmd_full);

    setuid(uid);
	return 0;
}
