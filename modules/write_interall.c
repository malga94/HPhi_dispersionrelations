#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {

int L = atoi(argv[1]);
int W = atoi(argv[2]);
int lattice = atoi(argv[3]);
float DM = atof(argv[4]);
float S = atof(argv[5]);
float J = atof(argv[6]);
float Jt = atof(argv[7]);

int Nsites = L*W;

if (lattice==1) {
      int i=0;

      if (DM != 0 && S != 1) {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*8);
      }
      else if (DM != 0) {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*2);
      }
      else {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*6);
      }
      for(i=0; i<Nsites; i++) {
	//This first part adds the SxSx+SySy part of the Heisenberg Hamiltonian. In fermion operator language, the DM interaction has the
	//exact same terms, but with imaginary coefficients, so we can add that too in the same lines
  if (DM!=0) {
	   printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+1)%Nsites, (i+1)%Nsites, DM);
	   printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+1)%Nsites, (i+1)%Nsites, -DM);
    }
  if (S!=1) {
     printf("%d    0    %d    1    %d    1    %d    0    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J);
     printf("%d    1    %d    0    %d    0    %d    1    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J);
     printf("%d    0    %d    0    %d    0    %d    0    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J/2);
     printf("%d    1    %d    1    %d    1    %d    1    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J/2);
     printf("%d    0    %d    0    %d    1    %d    1    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J/2);
     printf("%d    1    %d    1    %d    0    %d    0    %f    0.00\n", i, i, (i+1)%Nsites, (i+1)%Nsites, J/2);
    }
  }
}

if (lattice==2) {
      int i=0;
      if (DM != 0 && S != 1) {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*24);
      }
      else if (DM != 0) {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*6);
      }
      else {
        printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*18);
      }

      for(i=0; i<Nsites*2; i++) {

          if (DM!=0) {
            	if(i%2==0) {
            	  printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i,  i+1,  i+1, DM);
            	  printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i,  i+1,  i+1, -DM);
            	  printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), DM);
            	  printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), -DM);
            	}
            	else {
            	  printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), DM);
            	  printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), -DM);
              }
          }

          if (S!=1) {
            if(i%2==0) {
                printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i,  i+1,  i+1, Jt);
                printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i,  i+1,  i+1, Jt);
                printf("%d    0    %d    0    %d    0    %d    0    0.00    %f\n", i, i,  i+1,  i+1, Jt/2);
                printf("%d    1    %d    1    %d    1    %d    1    0.00    %f\n", i, i,  i+1,  i+1, Jt/2);
                printf("%d    0    %d    0    %d    1    %d    1    0.00    %f\n", i, i,  i+1,  i+1, Jt/2);
                printf("%d    1    %d    1    %d    0    %d    0    0.00    %f\n", i, i,  i+1,  i+1, Jt/2);

                printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J);
                printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J);
                printf("%d    0    %d    0    %d    0    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    1    %d    1    %d    1    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    0    %d    0    %d    1    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    1    %d    1    %d    0    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
            }
            else{
                printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J);
                printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J);
                printf("%d    0    %d    0    %d    0    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    1    %d    1    %d    1    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    0    %d    0    %d    1    %d    1    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
                printf("%d    1    %d    1    %d    0    %d    0    0.00    %f\n", i, i, (i+2)%(Nsites*2), (i+2)%(Nsites*2), J/2);
            }
        }
    }
}

if (lattice==3) {
      printf("=========================================\nNInterAll    %d\n==========================================\n", Nsites*4);
      int cont=-1, i=0;
      for(i=0; i<Nsites; i++) {
      	if (i%W == 0) {
      	  cont++;
      	}
      	printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+1)%W+cont*W, (i+1)%W+cont*W, DM);
      	printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+1)%W+cont*W, (i+1)%W+cont*W, -DM);
      	printf("%d    0    %d    1    %d    1    %d    0    0.00    %f\n", i, i, (i+W)%Nsites, (i+W)%Nsites, DM);
      	printf("%d    1    %d    0    %d    0    %d    1    0.00    %f\n", i, i, (i+W)%Nsites, (i+W)%Nsites, -DM);
            }
        }
}
