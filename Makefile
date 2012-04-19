.DEFAULT: default
.PHONY: default

default: clean all

all: ro_before ro_after write erase

ro_after:
	gcc ro_after.c -g -o ro_after

ro_before:
	gcc ro_before.c -g -o ro_before

write:
	gcc write.c -g -o write

erase:
	gcc erase.c -g -o erase

clean:
	rm -rf write ro_before ro_after erase

