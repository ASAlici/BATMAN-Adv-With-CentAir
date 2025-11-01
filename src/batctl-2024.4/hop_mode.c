




#include <errno.h>
#include <getopt.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "batman_adv.h"
#include "functions.h"
#include "main.h"
#include "netlink.h"
#include "sys.h"

static uint16_t hop_number=0;
static uint8_t hop_command;



static int set_attrs_hopmode(struct nl_msg *msg, void *arg __maybe_unused)
{
    nla_put_u8(msg, BATADV_ATTR_HOPMODE_COMMAND, hop_command);
    nla_put_u16(msg, BATADV_ATTR_HOPMODE_PENALTY, hop_number);

	return 0;
}




static int get_hopmode_input(struct state *state, int argc, char **argv){
	char *endptr;

    if(argc==2){
        if(strcmp(argv[1],"stop")==0){
            hop_command=HOPMODE_STOP;
        }
    }

    if(argc==3){
        if(strcmp(argv[1],"uniform")==0){
            hop_command=HOPMODE_UNIFORM;
            hop_number = (uint16_t)strtoul(argv[2], &endptr, 10);
            if (!endptr || *endptr != '\0') {
                fprintf(stderr, "I cannot parse this thing as hop penalty.\n");
                return -EINVAL;
	        }
        }
        else if(strcmp(argv[1],"centair")==0){
            hop_command=HOPMODE_CENTAIR;
            hop_number = (uint16_t)strtoul(argv[2], &endptr, 10);
            if (!endptr || *endptr != '\0') {
                fprintf(stderr, "I cannot parse this thing as hop penalty.\n");
                return -EINVAL;
	        }
        }
        else{
            fprintf(stderr, "I do not understand what you are trying to say.\n");
            return -EINVAL;
        }
    }
    return 0;
}


static int hop_mode(struct state *state, int argc, char **argv){
    
    int res = EXIT_FAILURE;

    if(argc<2){
        fprintf(stderr,"Only writing the command not going to work.\n");
        return res;
    }

    res=get_hopmode_input(state,argc,argv);

    if (res < 0)
		return EXIT_FAILURE;

    res=sys_simple_nlquery(state, BATADV_CMD_HOPMODE, set_attrs_hopmode,
        NULL);
    
    return res;
}












COMMAND(SUBCOMMAND_MIF, hop_mode, "hopmod",
	COMMAND_FLAG_MESH_IFACE | COMMAND_FLAG_NETLINK, NULL,
	"set the hop mode in the network");