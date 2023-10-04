CC = gcc
CFLAGS = -Wall -Wextra -pedantic -std=c99

# List of source files (one per executable)
SOURCES = w_wg.c w_hdparm.c w_smartctl.c

# Generate the list of executable names by stripping the .c extension
EXECUTABLES = $(SOURCES:.c=)

all: $(EXECUTABLES)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<
	chown root:root $@
	chmod u+s $@

clean:
	rm -f $(EXECUTABLES)