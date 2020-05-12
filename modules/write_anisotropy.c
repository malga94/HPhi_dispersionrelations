#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int calculate_site_number(int lattice, int Nsites, float J0, float J1, float J2, float J3, float J4) {

    if (lattice == 1) {
      if (J1 == 0) {
        return Nsites;
      }
      else if (J0 != 0 && J1 != 0) {
        return Nsites*2;
      }
    }

    if (lattice == 2) {
      return 3*Nsites/2;
    }

    if (lattice == 3) {
      if (J2 == 0 && J3 == 0) {
        return Nsites*2;
      }
      else if (J2 == 0 && J3 != 0){
        return Nsites*4;
      }
      else if (J2 != 0 && J3 == 0) {
        return Nsites*4;
      }
      else {
        return Nsites*6;
      }
    }

    return 0;
}

int main(int argc, char **argv) {

int L = atoi(argv[1]);
int W = atoi(argv[2]);
int lattice = atoi(argv[3]);
/* In this program there are 5 exchange couplings, because that is how many can be specified for the
ladder lattice (the one with the most possible exchange couplings). For the chain, only J0 and J1 will
ever be used, and for the square lattice only J0, J1 and J2. For now these are the only kinds of lattice
available*/
float J0 = atof(argv[4]);
float J1 = atof(argv[5]);
float J2 = atof(argv[6]);
float J3 = atof(argv[7]);
float J4 = atof(argv[8]);
float anisotropy = atof(argv[9]);
int selector = atoi(argv[10]);

int Nsites = L*W;
int Nlines;
Nlines = calculate_site_number(lattice, Nsites, J0, J1, J2, J3, J4);

char filename[20];
//This means that the program is supposed to write to the hund.def file (in which the couplings have to be opposite sign and
//double the magnitude than in the coulombinter file)
//If selector == 0, it writes to the coulombinter.def file, and nothing has to be changed
if (selector == 1) {
  J0 = -2*J0;
  J1 = -2*J1;
  J2 = -2*J2;
  J3 = -2*J3;
  J4 = -2*J4;

  char c[20] = "NHund";
  strcpy(filename, c);
}

else {
  char c[20] = "nNCoulombInter";
  strcpy(filename, c);
}

if (lattice == 1) {
  J0 = J0*(1 + anisotropy);
  int i=0;
  printf("=========================================\n%s   %d\n==========================================\n", filename, Nlines);
  for (i=0; i<Nsites; i++){
    printf("%d   %d   %f\n", i, (i+1)%Nsites, -J0/4);
    if (J1 != 0) {
      printf("%d   %d   %f\n", i, (i+2)%Nsites, -J1/4);
    }
  }
}

else if (lattice == 2) {
  J1 = J1*(1 + anisotropy);
  int i=0;
  printf("=========================================\n%s   %d\n==========================================\n", filename, Nlines);
  for (i=0; i<Nsites*2; i++) {
    if (i%2 == 0) {
      printf("%d   %d   %f\n", i, i+1, -J0/4);
      printf("%d   %d   %f\n", i, (i+2)%(Nsites*2), -J1/4);
    }
    else {
      printf("%d   %d   %f\n", i, (i+2)%(Nsites*2), -J1/4);
    }
    //TODO: Write lines for other couplings as well!!
  }
}

else if (lattice == 3) {
  J0 = J0*(1 + anisotropy);
  J1 = J1*(1 + anisotropy);
  printf("=========================================\n%s    %d\n==========================================\n", filename, Nlines);
  int cont=-1, i=0;
    for(i=0; i<Nsites; i++) {
      if (i%W == 0) {
        cont++;
      }
      //Remember that, differently from the ladder, here J0 is horizontal coupling and J1 vertical coupling
      printf("%d    %d    %f\n", i, (i+1)%W+cont*W, -J0/4);
      printf("%d    %d    %f\n", i, (i+W)%Nsites, -J1/4);

      //These 4 lines are for the diagonals of the square
      if (J2 != 0) {
        printf("%d    %d    %f\n", i, ((i+W+1)%W+(cont+1)*W)%Nsites, -J2/4);
        printf("%d    %d    %f\n", i, ((i+W-1)%W+(cont+1)*W)%Nsites, -J2/4);
      }

      //And the last two lines for the next-next-NN (so 2 lattice points vertically or horizontally)
      if (J3 != 0) {
        printf("%d    %d    %f\n", i, (i+2)%W+cont*W, -J3/4);
        printf("%d    %d    %f\n", i, (i + 2*W)%Nsites, -J3/4);
      }
        }
    }
}
