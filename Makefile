default: clean all

all: ro write

ro:
	gcc ro.c -o ro

write:
	gcc write.c -o write

clean:
	rm -rf write ro

