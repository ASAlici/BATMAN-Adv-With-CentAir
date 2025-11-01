




#include <errno.h>
#include <getopt.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "batman_adv.h"
#include "functions.h"
#include "main.h"
#include "netlink.h"
#include "sys.h"

static int64_t collision_threshold;
static uint8_t collision_mode_flag; 
static uint8_t collision_reset_flag=0; 

static uint8_t reset_input=0; 
static uint8_t mode_input=0;
static uint8_t threshold_input=0;  

static int set_attrs_collmode(struct nl_msg *msg, void *arg __maybe_unused)
{
	if(mode_input)
    	nla_put_u8(msg, BATADV_ATTR_COLLMODE_MODE, collision_mode_flag);
	if(reset_input)
		nla_put_u8(msg, BATADV_ATTR_COLLMODE_RESET_STAT, collision_reset_flag);
    if(threshold_input)
		nla_put_s64(msg, BATADV_ATTR_COLLMODE_THRESHOLD, collision_threshold);
    
	return 0;
}




static int parse_collmode(struct state *state, int argc, char **argv){
	char *endptr;

	if(argc==2){
		if( strcmp(argv[1],"reset")==0 ){
			collision_reset_flag=1;
		}
		reset_input=1;
	}

    if(argc==3){
        if( strcmp(argv[1],"set_mode")==0 ){
            
			collision_mode_flag = (uint8_t)strtoul(argv[2], &endptr, 10);
            if (!endptr || *endptr != '\0') {
                fprintf(stderr, "I cannot parse this thing as mode flag.\n");
                return -EINVAL;
	        } 
			mode_input=1;
        }

		else if(strcmp(argv[1],"set_threshold")==0 ){
			
			collision_threshold = (int64_t)strtoul(argv[2], &endptr, 10);
            if (!endptr || *endptr != '\0') {
                fprintf(stderr, "I cannot parse this thing as threshold.\n");
                return -EINVAL;
	        }
			threshold_input=1;
		}

        else{
            fprintf(stderr, "I do not understand what you are trying to say.\n");
            return -EINVAL;
        }
    }
	return 0;
}

static int print_collmode(struct nl_msg *msg, void *arg)
{
	static const int mandatory[] = {
		BATADV_ATTR_COLLMODE_THRESHOLD,
	    BATADV_ATTR_COLLMODE_MODE,
	    BATADV_ATTR_COLLMODE_LAST_DIFFERENCE,
		//BATADV_ATTR_COLLMODE_MAX_DIFF,
		//BATADV_ATTR_COLLMODE_MIN_DIFF,
	};

	struct nlattr *attrs[BATADV_ATTR_MAX + 1];
	struct nlmsghdr *nlh = nlmsg_hdr(msg);
	struct genlmsghdr *ghdr;
	int *result = arg;
	
	uint8_t collmode;
	int64_t threshold;
	int64_t last_difference;
	//int64_t min_difference;
	//int64_t max_difference;
	

	if (!genlmsg_valid_hdr(nlh, 0))
		return NL_OK;

	ghdr = nlmsg_data(nlh);

	if (nla_parse(attrs, BATADV_ATTR_MAX, genlmsg_attrdata(ghdr, 0),
		      genlmsg_len(ghdr), batadv_netlink_policy)) {
		return NL_OK;
	}

	/* ignore entry when attributes are missing */
	if (missing_mandatory_attrs(attrs, mandatory, ARRAY_SIZE(mandatory)))
		return NL_OK;

	collmode = nla_get_u8(attrs[BATADV_ATTR_COLLMODE_MODE]);
	switch (collmode) {
	case BATADV_COLLMODE_OFF:
		printf("Collision mode: %d\n\n",BATADV_COLLMODE_OFF);
		break;
	case BATADV_COLLMODE_ON:

		threshold = nla_get_s64(attrs[BATADV_ATTR_COLLMODE_THRESHOLD]);
        last_difference = nla_get_s64(attrs[BATADV_ATTR_COLLMODE_LAST_DIFFERENCE]);
		//min_difference = nla_get_s64(attrs[BATADV_ATTR_COLLMODE_MIN_DIFF]);
		//max_difference = nla_get_s64(attrs[BATADV_ATTR_COLLMODE_MAX_DIFF]);
        printf("Collision mode: %d\n\n",BATADV_COLLMODE_ON);
		if(threshold!=-1)
			printf("Collision threshold: %" PRId64 "\n", threshold);
        else
			printf("Collision threshold: INVALID\n");
		printf("Difference between last two packets: %" PRId64 "\n", last_difference);
		//printf("Maximum difference until now: %" PRId64 "\n", max_difference);
		//printf("Minimum difference until now: %" PRId64 "\n", min_difference);

		break;
	default:
		printf("unknown\n");
		break;
	}

	*result = 0;
	return NL_STOP;
}


static int collmode_read_setting(struct state *state)
{
	int res;

	res = sys_simple_nlquery(state, BATADV_CMD_GET_MESH, NULL, print_collmode);
	if (res < 0)
		return EXIT_FAILURE;
	else
		return EXIT_SUCCESS;
}


static int collmode_write_setting(struct state *state)
{
	int res = EXIT_FAILURE;

	res = sys_simple_nlquery(state, BATADV_CMD_SET_MESH, set_attrs_collmode,
				  NULL);
	if (res < 0)
		return EXIT_FAILURE;
	else
		return EXIT_SUCCESS;
}


static int collision_mode(struct state *state, int argc, char **argv){
    
	int res = EXIT_FAILURE;


	if (argc == 1)
		return collmode_read_setting(state);

	res = parse_collmode(state, argc, argv);
	if (res < 0)
		return EXIT_FAILURE;

	return collmode_write_setting(state);
}


COMMAND(SUBCOMMAND_MIF, collision_mode, "collmod",
	COMMAND_FLAG_MESH_IFACE | COMMAND_FLAG_NETLINK, NULL,
	"collision mode in the network");