#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define pi 3.14159

int main(int argc, char **argv) {
  int i=0, j=0;
  float kx = atof(argv[1]);
  int Nsite = atoi(argv[2]);
  
  printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", Nsite);
  for (i=0; i<Nsite; i++) {
    printf("%d 0 %d 1 0 ", i, i);
    printf("%lf %lf\n", cos(2*kx*pi*i), sin(2*kx*pi*i));
  }
}
