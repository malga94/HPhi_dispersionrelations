#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define pi 3.14159

void write_chain(float kx, int L) {

  int i = 0;
  printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", L);
  for (i=0; i<L; i++) {
    printf("%d 0 %d 1 0 ", i, i);
    printf("%lf %lf\n", cos(2*kx*pi*i), sin(2*kx*pi*i));
  }

}

void write_ladder(float kx, int L) {

  float ky = pi;
  int i = 0;
  printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", L*2);
  for (i=0; i<L*2; i=i+2) {
    printf("%d 0 %d 1 0 ", i, i);
    printf("%lf %lf\n", cos(kx*pi*i), sin(kx*pi*i));
    printf("%d 0 %d 1 0 ", i+1, i+1);
    printf("%lf %lf\n", cos(kx*pi*i)*cos(ky*2*pi), sin(kx*pi*i)*cos(ky*2*pi));
    }
}

int main(int argc, char **argv) {

  float kx = atof(argv[1]);
  int L = atoi(argv[2]);
  int lattice = atoi(argv[3]);

  if (lattice == 1) {
  	write_chain(kx, L);
  }

  else if (lattice == 2) {
  	write_ladder(kx, L);
  }
  
}
