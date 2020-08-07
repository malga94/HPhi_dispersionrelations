#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define pi 3.14159

void write_chain(float kx, int L) {
  int single = 0;
  int i = 0;
  if (single == 0) {
    printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", L);
    for (i=0; i<L; i++) {
      printf("%d 0 %d 1 0 ", i, i);
      printf("%lf %lf\n", cos(2*kx*pi*i), sin(2*kx*pi*i));
    }
  }

  //Legacy code remaining to test the SingleExcitation file. Should define a magnon state starting from the GS, just like pair.def does: try to test it eventually
  else {
    printf("=============================================\nNSingle %d\n=============================================\n=============================================\n=============================================\n", L*2);
    for (i=0; i<L; i++) {
      printf("%d 0 0 %lf, %lf\n", i, cos(2*kx*pi*i), sin(2*kx*pi*i));
      printf("%d 1 1 %lf, %lf\n", i, cos(2*kx*pi*i), sin(2*kx*pi*i));
    }
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

void write_square(float kx, float ky, int L, int W) {

  printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", L*W);
  for (int i=0; i<L; i++) {
    for (int j=0; j<W; j++) {
      printf("%d 0 %d 1 0 ", j+W*i, j+W*i);
      printf("%lf %lf\n", cos(2*pi*j*kx)*cos(2*pi*i*ky)-sin(2*pi*j*kx)*sin(2*pi*i*ky), cos(2*pi*j*kx)*sin(2*pi*i*ky)+sin(2*pi*j*kx)*cos(2*pi*i*ky));
      }
    }
}

void write_double(float kx, float ky, int L, int W) {

  //Maybe eventually the user can specify kz, altough I don't see the need for bilayer systems
  float kz = 0;
  printf("=============================================\nNPair %d\n=============================================\n=============================================\n=============================================\n", L*W);

  for (int k=0; k<2; k++) {  
    for (int i=0; i<4; i++) {
      for (int j=0; j<4; j++) {
        printf("%d 0 %d 1 0 ", j+4*i+16*k, j+4*i*+16*k);
        printf("%lf %lf\n", cos(2*pi*j*kx)*cos(2*pi*i*ky)*cos(2*pi*k*kz)-sin(2*pi*j*kx)*sin(2*pi*i*ky)*cos(2*pi*k*kz)-cos(2*pi*j*kx)*sin(2*pi*i*ky)*sin(2*pi*k*kz)-sin(2*pi*j*kx)*cos(2*pi*i*ky)*sin(2*pi*k*kz), cos(2*pi*j*kx)*sin(2*pi*i*ky)*cos(2*pi*k*kz)+sin(2*pi*j*kx)*cos(2*pi*i*ky)*cos(2*pi*k*kz)+cos(2*pi*j*kx)*cos(2*pi*i*ky)*sin(2*pi*k*kz)-sin(2*pi*j*kx)*sin(2*pi*i*ky)*sin(2*pi*k*kz));
      }
    }
  }

}

int main(int argc, char **argv) {

  float kx = atof(argv[1]);
  float ky = atof(argv[2]);
  int L = atoi(argv[3]);
  int W = atoi(argv[4]);
  int lattice = atoi(argv[5]);

  if (lattice == 1) {
  	write_chain(kx, L);
  }

  else if (lattice == 2) {
  	write_ladder(kx, L);
  }

  else if (lattice == 3) {
	write_square(kx, ky, L, W);
  }
  
}
