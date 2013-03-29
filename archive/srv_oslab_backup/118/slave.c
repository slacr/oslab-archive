/* this is in good enough shape till it can be tested! */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <openssl/sha.h>

#include "pvm3.h"
#include "common.h"


static unsigned char * hashed_pass;
static char word[9];

int check(int prefix[3]){

	int int_array[] = {0,0,0,0,0,0,0,0};
	int k=0, retval=0;
	unsigned char * hashed_word = malloc(20);

	for(k=0; k<3; k++){
	    int_array[k] = prefix[k];
	}
	

//	for(k = 0; k<916132832; k++){
	for(k = 0; k<900; k++){

		convert(int_array, word);

		SHA1((unsigned char *)word, 8, hashed_word);

		if(!strncmp((const char *)hashed_word, (const char *)hashed_pass, 20)){
			retval = 1;
			break;
		}

		increment(int_array, 8);
	
	}
	
	return retval;
}

int main(int argc, char * argv[]){

	//not necessary.
	int whoiam = atoi(argv[1]);
		
	
	hashed_pass = malloc(20);
	
	// pass -1 and plaintext password to the terminal to run in not-pvm debug mode
	if (whoiam == -1){
		SHA1((unsigned char *)argv[2], 8, hashed_pass);
		int retval;
		int prefix[3] = {0,0,0};
		retval = check(prefix);
		printf("%d \n", retval);
		prefix[2]++;			
		retval = check(prefix);
		printf("%d \n", retval);			

	} else {

	//else this is a child of the main pvm program
		int momma = pvm_parent();
		struct timeval t;
		t.tv_sec = 10;
		t.tv_usec = 0;
		int prefix[3] = {9,9,9};
		int retval = -1;
		int atwork = 2;
		int k = 0;

		strncpy((char *)hashed_pass, argv[2], 20);

		while(atwork>0){
			for (k=0; k<3; k++){
			
				pvm_trecv( momma, -1, &t );
				pvm_upkint(&prefix[k], 1, 1);
			}
			printf(" recvd %d%d%d \n", prefix[0], prefix[1], prefix[2]);
			fflush(stdout);	
			retval = check(prefix);
			pvm_initsend(PvmDataDefault);
			pvm_pkint(&retval, 1, 1);
			pvm_send(momma, whoiam);
			if (retval == 1) {
				printf("slave says ! %s\n", word);
				pvm_initsend(PvmDataDefault);
				pvm_pkstr(word);
				pvm_send(momma, whoiam);
				atwork = 0;
			}
		}
	}
	pvm_exit();
	return 0;
}
