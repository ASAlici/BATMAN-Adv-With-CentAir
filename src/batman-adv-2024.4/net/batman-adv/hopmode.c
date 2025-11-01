// SPDX-License-Identifier: GPL-2.0
/* Copyright (C) B.A.T.M.A.N. contributors:
 *
 * Marek Lindner
 */

 #include "gateway_common.h"
 #include "main.h"
 
 #include <linux/atomic.h>
 #include <linux/byteorder/generic.h>
 #include <linux/stddef.h>
 #include <linux/types.h>
 #include <linux/rculist.h>
 #include <linux/rcupdate.h>
 #include <uapi/linux/batadv_packet.h>
 #include <uapi/linux/batman_adv.h>
 
 #include "hopmode.h"
 #include "tvlv.h"
 #include "hard-interface.h"
 #include "hash.h"
 
 /**
  * batadv_sth_tvlv_container_update() - update the hopmode tvlv container after
  *  
  * @bat_priv: the bat priv with all the soft interface information
  */
 void batadv_hopmode_tvlv_container_update(struct batadv_priv *bat_priv, u16 neigh_penalty, u8 hopmode_command)
 {
   u8 old_penalty;
   u8 calculated_penalty;

   struct batadv_tvlv_hopmode_data hopmode;

   if(hopmode_command==HOPMODE_STOP){
      printk("Let's unregister then!\n");
      batadv_tvlv_container_unregister(bat_priv, BATADV_TVLV_HOPMODE, 1);
      }
   else if(hopmode_command==HOPMODE_UNIFORM){
      hopmode.neigh_penalty=htons(neigh_penalty);
      hopmode.command_type=HOPMODE_UNIFORM;

      batadv_tvlv_container_register(bat_priv, BATADV_TVLV_HOPMODE, 1,
         &hopmode, sizeof(hopmode));

      old_penalty=atomic_read(&bat_priv->hop_penalty);
      if(neigh_penalty>255)
         calculated_penalty=255;
      else
         calculated_penalty=neigh_penalty;
      atomic_set(&bat_priv->hop_penalty, calculated_penalty);
   }
   else if(hopmode_command==HOPMODE_CENTAIR){
      //printk("We register to to the OGM!\n");
      hopmode.neigh_penalty=htons(neigh_penalty);
      hopmode.command_type=HOPMODE_CENTAIR;


      batadv_tvlv_container_register(bat_priv, BATADV_TVLV_HOPMODE, 1,
                        &hopmode, sizeof(hopmode));



      old_penalty=atomic_read(&bat_priv->hop_penalty);
      calculated_penalty=calculate_penalty(bat_priv,neigh_penalty);

      atomic_set(&bat_priv->hop_penalty, calculated_penalty);

      //printk("Old penalty was %d, new should be %d, you should check it.\n"
      //,old_penalty,calculated_penalty);
      }
 }
 
 /**
  * batadv_hopmode_tvlv_ogm_handler_v1() - process incoming HOPMODE tvlv container
  * @bat_priv: the bat priv with all the soft interface information
  * @orig: the orig_node of the ogm
  * @flags: flags indicating the tvlv state (see batadv_tvlv_handler_flags)
  * @tvlv_value: tvlv buffer containing the gateway data
  * @tvlv_value_len: tvlv buffer length
  */
 static void batadv_hopmode_tvlv_ogm_handler_v1(struct batadv_priv *bat_priv,
                       struct batadv_orig_node *orig,
                       u8 flags,
                       void *tvlv_value, u16 tvlv_value_len)
{
   struct batadv_tvlv_hopmode_data hopmode;
   u8 old_penalty;
   u8 calculated_penalty;

   if (tvlv_value_len < sizeof(hopmode)) {
   printk("There is no data!\n");
   } else {
      hopmode=*(struct batadv_tvlv_hopmode_data *)tvlv_value;
      //printk("Before ntohs, penalty number: %d\n",hopmode.neigh_penalty);
      hopmode.neigh_penalty=ntohs(hopmode.neigh_penalty);
      //printk("After ntohs, penalty number: %d\n",hopmode.neigh_penalty);
      //printk("Hop command: %d\n",hopmode.command_type);
      //printk("Received command:%d\nReceived hop number:%d\n",hopmode.command_type,hopmode.neigh_penalty);
      
      if(hopmode.command_type==HOPMODE_UNIFORM){

         old_penalty=atomic_read(&bat_priv->hop_penalty);
         if(hopmode.neigh_penalty>255)
            calculated_penalty=255;
         else
            calculated_penalty=hopmode.neigh_penalty;

         atomic_set(&bat_priv->hop_penalty, calculated_penalty);
      }
      else if(hopmode.command_type==HOPMODE_CENTAIR){

         old_penalty=atomic_read(&bat_priv->hop_penalty);
         calculated_penalty=calculate_penalty(bat_priv,hopmode.neigh_penalty);

         //printk("Calculated penalty: %d\n",calculated_penalty);
         atomic_set(&bat_priv->hop_penalty, calculated_penalty);

      }

   }
}
 

 void batadv_hopmode_init(struct batadv_priv *bat_priv)
 {

    batadv_tvlv_handler_register(bat_priv, batadv_hopmode_tvlv_ogm_handler_v1,
                      NULL, NULL, BATADV_TVLV_HOPMODE, 1,
                      BATADV_NO_FLAGS);
 }
 

 void batadv_hopmode_free(struct batadv_priv *bat_priv)
 {
    batadv_tvlv_container_unregister(bat_priv, BATADV_TVLV_HOPMODE, 1);
    batadv_tvlv_handler_unregister(bat_priv, BATADV_TVLV_HOPMODE, 1);
 }
 


u8 calculate_penalty(struct batadv_priv *bat_priv, u16 max_penalty){
   int orig_number;
   int neigh_number;
   u16 calculated_penalty;
   
   orig_number=get_orig_number(bat_priv);
   neigh_number=get_neigh_number(bat_priv);

   //printk("Number of originators: %d\n", orig_number);
   //printk("Number of neighbors: %d\n",neigh_number);

   if(orig_number==0)
      return -1;
   
   calculated_penalty=max_penalty*neigh_number/orig_number;
   
   if(calculated_penalty>255)
      calculated_penalty=255;

   return (u8)calculated_penalty;

}


int get_orig_number(struct batadv_priv *bat_priv){
   struct batadv_hashtable *hash = bat_priv->orig_hash;
	struct hlist_head *head;
   struct batadv_orig_node *orig_node;
   int bucket=0;

   //It counts itself too.
   int orig_number=1;
   
   while (bucket < hash->size) {
		head = &hash->table[bucket];

      rcu_read_lock();
      hlist_for_each_entry_rcu(orig_node, head, hash_entry) {
         orig_number++;
      }
      rcu_read_unlock();

		bucket++;
	}

   return orig_number;
}



int get_neigh_number(struct batadv_priv *bat_priv){
   struct batadv_hard_iface *primary_hardif;

   struct batadv_hardif_neigh_node *hardif_neigh;
   int neigh_number=0;

   primary_hardif=batadv_primary_if_get_selected(bat_priv);

   rcu_read_lock();
   hlist_for_each_entry_rcu(hardif_neigh, &primary_hardif->neigh_list, list) {
      neigh_number++;
   }
   rcu_read_unlock();

   batadv_hardif_put(primary_hardif);

   return neigh_number;
}