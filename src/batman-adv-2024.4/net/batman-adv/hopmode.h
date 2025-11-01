/* SPDX-License-Identifier: GPL-2.0 */
/* Copyright (C) B.A.T.M.A.N. contributors:
 *
 * Marek Lindner
 */

 #ifndef _NET_BATMAN_ADV_HOPMODE_COMMON_H_
 #define _NET_BATMAN_ADV_HOPMODE_COMMON_H_
    


 #include "main.h"
 
 enum hopmode_commands{
    HOPMODE_STOP,
    HOPMODE_UNIFORM,
    HOPMODE_CENTAIR,
 };

 
 void batadv_hopmode_tvlv_container_update(struct batadv_priv *bat_priv, u16 neigh_penalty, u8 hopmode_command);
 void batadv_hopmode_init(struct batadv_priv *bat_priv);
 void batadv_hopmode_free(struct batadv_priv *bat_priv);
 int get_neigh_number(struct batadv_priv *bat_priv);
 int get_orig_number(struct batadv_priv *bat_priv);
 u8 calculate_penalty(struct batadv_priv *bat_priv, u16 max_penalty);

 #endif /* _NET_BATMAN_ADV_HOPMODE_COMMON_H_ */
 