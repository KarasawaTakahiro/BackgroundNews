#include <stdio.h>

int main(int argc, char **argv){
	int i;

	for(i=0; i<3; i++){
		sleep(1);
		printf("%d seceonds\n", i);
	}

	return 0;
}
