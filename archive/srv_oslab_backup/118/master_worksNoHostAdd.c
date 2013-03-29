
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <openssl/sha.h>

#include "pvm3.h"
#include "common.h"

#define CHAR_SET_SIZE 62

static int prefix[] = {0,0,0};

void crack(int total_cores, int nhost, struct pvmhostinfo *hostp, unsigned char * hashed_pass){

	/* bunch of bullshit. Tids holds the task ids of the remote programs, needed by PVM for PVM to get messages to them. (the messages we will send each is a prefix to work o) */
	int i, j, id=0, recv, info;
	int bytes, msgtag, source;
	int tids[100];

	/* sending as args to crackr_slave (on remote machines) 
	1) an identification number 
	and 2) the hash of the password we are trying to match */
	char * args[3];
	char * tmp_str;
	tmp_str = malloc(4);
	args[1] = (char *)hashed_pass;
	args[2] = (char *)0;

	//for each machine
	for ( i=0; i< nhost; i++ ){
		//for each core on that machine
		for ( j=0; j<hostp[i].hi_speed; j++){
			sprintf(tmp_str, "%d", id);
			args[0] = tmp_str;
		
			//spawn 1 instance of crackr_slave with args
			pvm_spawn("crackr_slave", args, 1, hostp[i].hi_name, 1, &tids[id]);
			id++;

			//printf("%s \n", args[0]);
		}	

	//	printf("%s has %d cores woot \n", hostp[i].hi_name, hostp[i].hi_speed);
		
	}

	/* here we tell each instance of crackr_slave to check all the 
	possible 8-character alphanumeric passwords for a given 3-character
	prefix. */
	for ( i=0; i< total_cores; i++ ){
	
		//printf("%d%d%d,  %d\n", prefix[0], prefix[1], prefix[2], tids[i]);
		for (j=0; j<3; j++){
			info = pvm_initsend(PvmDataDefault);
			info = pvm_pkint(&prefix[j], 1, 1);
			if(info<0){perror("pvm_pkint: ");}
			info = pvm_send(tids[i], 1);
			if(info<0){perror("pvm_send: ");}
		}

		/* increment is described in common.c, it increments an array 
		as if it were a counter */
		increment(prefix, 3);
	}

	int done = 0;
	char * answer;
	answer = malloc(9);

	/* if we haven't either gotten an answer, exhausted the search space, 
	or encountered some error then we're not done. */
	while(done == 0) {
		/* pvm_recv(-1,-1) waits for any message from anyone */
		info = pvm_recv(-1,-1);
		if(info<0){
			perror("pvm_recv: ");
		} else {

			/* here we determine who sent the message,
			and what it means. */
			pvm_bufinfo(info, &bytes, &msgtag, &source);
			pvm_upkint(&recv, 1, 1);
			//printf("%d returned %d \n", source, recv);

			/* if it returned 1 then it found an answer! we're done */
			if (recv == 1) {
				pvm_recv(source, -1);
				pvm_upkstr(answer);
				printf("answer %s \n", answer);
				done=1;
			} else {
			/* otherwise it is done searching under a given 
			prefix, and it didn't find a match. So there are
			more prefixes to search, have it start on another */
				printf("%d%d%d,  %d\n", prefix[0], prefix[1], prefix[2], source);
				for (j=0; j<3; j++){
					info = pvm_initsend(PvmDataDefault);
					info = pvm_pkint(&prefix[j], 1, 1);
					if(info<0){perror("pvm_pkint: ");}
					info = pvm_send(source, 1);
					if(info<0){perror("pvm_send: ");}
				}
				//increment returns 1 when we've searched all prefixes
				done = increment(prefix, 3);
			}
		}	
	}

	//if we're done, then we don't need to do anymore. kill all processes everywhere
	for (j=0; j<total_cores;j++){
		info = pvm_kill(tids[j]);	
		if(info<0){perror("killing error: ");}
	}
	
}

int main(int argc, char * argv[]){

	//needed for pvm
	int me;
	me = pvm_mytid();
	int info, nhost, narch;
	struct pvmhostinfo * hostp;
	
	//pvm_catchout(stdout);

	//used to determine how many crackrs to spawn
	int total_cores;

	//for now this takes an plaintext password as an arg, SHA1s it, and passes the hash to the slaves
	unsigned char * hashed_pass;
	hashed_pass = malloc(20); 
	SHA1((unsigned char *)argv[1], 8, hashed_pass);
	
	//pvm_config tells us how many nodes and fills the hostp structs with info about each
	info = pvm_config( &nhost, &narch, &hostp );
	
	//get number of cores on cluster, put # of cores for each machine in hostp.hi_speed
	total_cores = get_core_count(nhost, hostp);

	//spawn crackrs
	crack(total_cores, nhost, hostp, hashed_pass);
	pvm_exit();
	//fflush(stdout);
	return 0;
}

