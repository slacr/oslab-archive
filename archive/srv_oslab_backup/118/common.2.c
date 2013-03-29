#include <stdio.h>
#include <stdlib.h>

#include "pvm3.h"
//for ease, this is the size of teh array minus 1
#define CHAR_ARRAY_LEN 61 

static char characters[] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

int increment(int * int_array, int len){

	int retval = 0;
	if(len == 0){
	
		retval = 1;
	
	} else {
	
		if(int_array[--len] >= CHAR_ARRAY_LEN){
		
			int_array[len] = 0;
			retval = increment(int_array, len);

		} else {
			
			int_array[len]++;

		}		

	}

	return retval;

/*
	//printf("i was passed %d \n", int_array[2]);

	if(int_array[len]>=CHAR_ARRAY_LEN){
		int_array[len]=0;
		for(place = len-1; place >= 0; place--){
			if(int_array[place] >= CHAR_ARRAY_LEN){int_array[place]=0;}
			else{(int_array[place])++;break;} 
		}
	}

	int_array[len]++;


*/
	
}

void convert(int array[], char * word){
	int i;
	for(i = 0; i < 8; i++){
		word[i] = characters[array[i]];
	}
	word[8] = '\0';

}


//ugly, fix!
int get_core_count(int nhost, struct pvmhostinfo *hostp){ 

	int i, bufid, numt, recv = 0, total_cores=0;
	int * tids;
	tids =  (int *)malloc(sizeof(int)*nhost);

	/* start up slave tasks, 1 per machine */
	for ( i=0; i<nhost; i++){
		numt+=pvm_spawn("getCores", (char**)0, 1, hostp[i].hi_name, 1, &tids[i]);
	}

    if( numt < nhost ){
       printf("\n Trouble spawning slaves. Aborting. Error codes are:\n");
       for( i=numt ; i<nhost ; i++ ) {
          printf("TID %d %d\n",i,tids[i]);
       }
       for( i=0 ; i<numt ; i++ ){
          pvm_kill( tids[i] );
       }
       pvm_exit();
       exit(1);
    }
//	printf("SUCCESSFUL\n");

	int host_num = nhost;

	while (host_num > 0) {
		
		for (i=0; i<nhost; i++){
			if(tids[i] != -1) {
				bufid = pvm_nrecv(tids[i], -1);
				if(bufid != 0){
					pvm_upkint(&recv, 1, 1);
					total_cores += recv;
					/* hi_speed is meaningless, now it indicates num of cores */
					hostp[i].hi_speed = recv; 
					host_num--;
				}
			}
		}
	}
	printf("%d cores \n", total_cores);
	return total_cores;
}


