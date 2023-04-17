CFLAGS=-g -pthread -Wall
LDFLAGS=-g
LDLIBS=-lm -ldl

SRCS=thread_test.c
OBJS=$(SRCS)

thread_test: $(OBJS)
	gcc $(CFLAGS) -o thread_test $(OBJS) $(LDLIBS)
clean:
	rm thread_test *.o


