#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

#define THREAD_COUNT 300

typedef struct silky{
  int modify_this;
  int modify_that;
  int index;
  pthread_t thread_id;
  pthread_rwlock_t rwlock;
} silk;

void * run(void * vargp)
{
  silk * args = (silk *)vargp;
  printf("Thread is starting: %i\n", args->index);
  int ret;
  sleep(1);
  for (int i = 0; i < 10000000; i++)
  {
    //silk_threads
    ret = pthread_rwlock_wrlock(&(args->rwlock));
    if (0!=ret)
    {
      printf("pthread_rw_lock_wrlock: %i", ret);
    }
    args->modify_this += 1;
    args->modify_that += 1;
    pthread_rwlock_unlock(&(args->rwlock));
  }
  printf("Thread is done\n");
  return NULL;
}

int main()
{
  silk silk_threads[THREAD_COUNT];

  pthread_rwlockattr_t attr;
  pthread_rwlockattr_init(&attr);
  int ret;

  printf("Creating threads\n");
  for (int i =0; i< THREAD_COUNT; ++i)
  {
    silk_threads[i].modify_this = 0;
    silk_threads[i].modify_that = 0;
    silk_threads[i].index = i;
    ret = pthread_rwlock_init(&(silk_threads[i].rwlock), &attr);
    if (0!=ret)
    {
      printf("pthread_rwlock_init: %i\n", ret);
    }

    ret = pthread_create(&(silk_threads[i].thread_id), NULL, run, &silk_threads[i]);
    if (0 !=ret)
    {
      printf("pthread_rwlock_init %i\n", ret);
    }
  }
  printf("Sleeping\n");
  sleep(2);

  printf("Printing threads\n");
  for (int j = 0; j < 5000000; j++)
  //for (int j = 0; j < THREAD_COUNT; j++)
  {
    int index = j % THREAD_COUNT - 1;
    pthread_rwlock_rdlock(&(silk_threads[index].rwlock));
    printf("%i (%i): %i\n", index, silk_threads[index].index, silk_threads[index].modify_this);
    pthread_rwlock_unlock(&silk_threads[index].rwlock);
  }
  sleep(10);

  printf("Destroying threads\n");
  for (int i = 0; i< THREAD_COUNT; ++i)
  {
    pthread_join(silk_threads[i].thread_id, NULL);
    pthread_rwlock_destroy(&silk_threads[i].rwlock);
  }
  printf("After thread\n");
  exit(0);
}
