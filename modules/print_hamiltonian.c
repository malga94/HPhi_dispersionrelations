#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>

float fetch_value(char *ptr) {
  //Function to return an int value from the string ptr
  float num_value = 0, temp = 0;
  int cont = 0, isneg = 0;

  for (int i=strlen(ptr)-1; i>=0; i--) {
    if (*(ptr+i) == '-') {
      isneg = 1;
      continue;
    }
    if (*(ptr+i) == '.') {
      num_value *= pow(10, -cont);
      cont = 0;
      continue;
    }
    //The pesky newlines were messing up the conversion, because of course they have an ASCII value, so that
    //*(ptr+i) - '0' was giving -38 when *(ptr+i) = '\n'
    if (*(ptr+i) == '\n') {
      continue;
    }
    temp = *(ptr+i) - '0';
    temp = temp * pow(10, cont);
    num_value += temp;
    cont++;

  }
  if (isneg == 1) {
    num_value *= -1;
  }
  return num_value;
}

int main(int argc, char **argv) {

  FILE *fp;
  char buff[255];

  fp = fopen("../PrepareData/output/zvo_Ham.dat", "r");
  //Reading first two lines of zvo_Ham.dat. The first line is useless, the second specifies the dimensions of
  //the Hamiltonian matrix and the number of non-zero elements (3 ints) in this order, separated by spaces
  fgets(buff, 255, (FILE*)fp);
  fgets(buff, 255, (FILE*)fp);

  //Separating the string at the spaces
  char delim[] = " ";
  char *ptr = strtok(buff, delim);

  //First int is the matrix dimension
  //-'0' is to convert the ASCII value (since ptr is a *char) to an int
  int matrix_dim = 0;
  matrix_dim = fetch_value(ptr);

  //The next line reads the second matrix dimension, but since the Hamiltonian is always a square matrix, I
  //don't bother saving the value. It will be the same as matrix_dim
  ptr = strtok(NULL, delim);

  //Third int is number of nonzero elements
  ptr = strtok(NULL, delim);

  int num_lines = 0, cont = 0;
  num_lines = fetch_value(ptr);

  char hamiltonian[num_lines][127];
  for (int i=0; i<num_lines; i++) {
    fgets(hamiltonian[i], 127, (FILE*)fp);

  }

  fclose(fp);

  //Initializing the Hamiltonian matrix (output of this program) with all zeros
  float matrix[matrix_dim+1][matrix_dim+1];

  cont = 0;
  for (int i=1; i<=matrix_dim; i++) {
    for (int j=1; j<=matrix_dim; j++) {
        matrix[i][j] = 0;
    }
  }

  float values[num_lines][4];
  float value_to_append;
  for (int k=0; k<num_lines; k++) {

    ptr = strtok(hamiltonian[k], delim);

    value_to_append = fetch_value(ptr);
    for (int i=0; i<3; i++) {
      values[k][i] = value_to_append;
      ptr = strtok(NULL, delim);

      value_to_append = fetch_value(ptr);

    }
    values[k][3] = value_to_append;
  }

  //Now we need to populate the Hamiltonian matrix
  double complex z = 0.0 + 0.0*I;
  int column = 0, row = 0;
  int num_zeros;

  for (int i=1; i<=num_lines; i++) {
    z = values[i-1][2] + values[i-1][3]*I;
    row = (int)values[i-1][0];
    column = (int)values[i-1][1];
    matrix[row][column] = z;
    matrix[column][row] = conj(z);

  }

  fp = fopen("../output_ham.dat", "w");


  for (int i=1; i<=matrix_dim; i++) {
    for (int j=1; j<=matrix_dim; j++) {
      if (creal(matrix[i][j]) == 0 && cimag(matrix[i][j]) == 0) {
        num_zeros++;
      }
      fprintf(fp, "%f + %f    ", creal(matrix[i][j]), cimag(matrix[i][j]));
    }
    fprintf(fp, "\n");
  }
  fprintf(fp, "\nNumber of zero elements: %d, which are %f of the total, which is %d\n", num_zeros, (float)num_zeros/(matrix_dim*matrix_dim), matrix_dim*matrix_dim);
  fclose(fp);

}
