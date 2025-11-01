import json
import matplotlib.pyplot as plt
import numpy as np
import csv 
import argparse
import traceback
import os
import datetime
from pathlib import Path


def parse_iperf3_json(dir_name_prefix):
    """
    Parse iperf3 JSON output and extract time series data
    """
    total_bytes=0
    total_lost_packets=0
    total_packets=0
    jitter_values = []
    lost_packets = []
    lost_percent = []
    packet_counts = []
    bitrates = []

    current_dir = Path('.')
    target_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name.startswith(dir_name_prefix)]
    server_log_number=0
    for dir_path in target_dirs:
        server_log_files = list(dir_path.glob('server_log*'))

        for file_path in server_log_files:
            server_log_number+=1
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            intervals = data['intervals']
            
            for interval in intervals:
                # Get the stream data (first stream if multiple)
                stream = interval['sum']
                
                jitter_values.append(stream['jitter_ms'])
                lost_packets.append(stream['lost_packets'])
                lost_percent.append(stream['lost_percent'])
                packet_counts.append(stream['packets'])
                bitrates.append(stream['bits_per_second'])

            total_bytes += sum(interval['sum']['bytes'] for interval in intervals)
            total_lost_packets += sum(interval['sum']['lost_packets'] for interval in intervals)
            total_packets += sum(interval['sum']['packets'] for interval in intervals)
        
    end_stats = {
        'test_number': server_log_number,
        'bytes_per_second': (total_bytes / server_log_number) / data['end']['sum']['seconds'],
        'lost_packets': total_lost_packets / server_log_number,
        'total_packets': total_packets/server_log_number,
        'lost_percent': (total_lost_packets / total_packets) * 100 if total_packets > 0 else 0,
        'jitter_ms': sum(jitter_values) / len(jitter_values)
    }

    return jitter_values, packet_counts, lost_percent, bitrates, end_stats



def parse_collision_array(collision_file_path):
    with open(collision_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        
        # Skip header if needed
        header = next(csv_reader)
        collisions=[]
        # Read each row
        for row in csv_reader:
            # row is a list: ['value1', 'value2', 'value3']
            if(row==[]):
                continue
            time = row[0]
            col = row[1]
            collisions.append(int(col))
    return collisions

#Tum collision stat file'larinin ayni satir sayisina sahip oldugunu var sayiyorum.
def read_all_coll_stat_files(dir_name_prefix):
    current_dir = Path('.')
    target_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name.startswith(dir_name_prefix)]
    
    all_colls_total = []
    for dir_path in target_dirs:
        csv_files = list(dir_path.glob('coll_stats*.csv'))
        colls_total=[]

        for file_path in csv_files:
            colls=parse_collision_array(file_path)
            if colls_total==[]:
                colls_total=colls
            else:
                colls_total=[a + b for a, b in zip(colls_total, colls)]
    
        if colls_total:  # Only add if we found files in this directory
            all_colls_total.extend(colls_total)

    return all_colls_total

def plot_iperf3_metrics( bandwidth, duration,client_bw, save_path=None):
    #"bw_${bandwidth}M_centair_${centair}_${duration}_clientBW_${client_bw}_$
    dir_name_prefix_true=f"bw_{bandwidth}M_centair_true_{duration}_clientBW_{client_bw}_"
    dir_name_prefix_false=f"bw_{bandwidth}M_centair_false_{duration}_clientBW_{client_bw}_"

    # Parse the data
    jitter_values_true, packet_counts_true, lost_percent_true, bitrates_true, end_stats_true = parse_iperf3_json(dir_name_prefix_true)
    total_colls_true=read_all_coll_stat_files(dir_name_prefix_true)

    jitter_values_false, packet_counts_false, lost_percent_false, bitrates_false, end_stats_false = parse_iperf3_json(dir_name_prefix_false)
    total_colls_false=read_all_coll_stat_files(dir_name_prefix_false)

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(25, 25))
    #centair_title="Without"
    #if(centair=="True"):
    #    centair_title="With"
    fig.suptitle(f'CDFs of iperf3 UDP Performance Metrics \n{bandwidth} MB/s UDP Storm, Client Bandwidth {client_bw}MB/s \nBatman-Adv CentAir Versus Normal Batman', fontsize=35, fontweight='bold')
    


    xt, yt = empirical_cdf(lost_percent_true)
    xf, yf = empirical_cdf(lost_percent_false)

    # Plot both functions on the same axis (use consistent axis reference)
    ax1.plot(xt, yt, 'b-o', linewidth=5, markersize=10, label='True')
    ax1.plot(xf, yf, 'r-o', linewidth=5, markersize=10, label='False')

    # Set labels and formatting (use same axis - ax1)
    ax1.set_ylabel('Probability', fontsize=25)
    ax1.set_xlabel('Percentage of Lost Packets In The Tested Client Per Second', fontsize=25)
    ax1.set_title('CDF of Percentage of Lost Packets In The Tested Client Per Second',fontweight='bold', fontsize=30)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=0)
    ax1.legend(fontsize=25)   # Add legend to show which line is which
    ax1.tick_params(axis='both', 
                labelsize=25,        # Font size
                width=2,             # Tick width
                length=8,            # Tick length
                labelcolor='black')  # Tick label color


    xt,yt=empirical_cdf(total_colls_true)
    xf,yf=empirical_cdf(total_colls_false)
    # Plot both functions on the same axis (use consistent axis reference)
    ax2.plot(xt, yt, 'b-o', linewidth=5, markersize=10, label='True')
    ax2.plot(xf, yf, 'r-o', linewidth=5, markersize=10, label='False')
    # Set labels and formatting (use same axis - ax1)
    #ax2.plot(xt+xf, yf, 'r-x', linewidth=2, markersize=4)
    ax2.set_ylabel('Probability', fontsize=25)
    ax2.set_xlabel('Collisions In The Network Per Second', fontsize=25)
    ax2.set_title('CDF of Collisions In The Network Per Second', fontweight='bold', fontsize=30)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0)
    ax2.legend(fontsize=25)
    ax2.tick_params(axis='both', 
                labelsize=25,        # Font size
                width=2,             # Tick width
                length=8,            # Tick length
                labelcolor='black')  # Tick label color
    
    """xt,yt=empirical_cdf(jitter_values_true)
    xf,yf=empirical_cdf(jitter_values_false)
    # Plot both functions on the same axis (use consistent axis reference)
    ax3.plot(xt, yt, 'b-o', linewidth=5, markersize=10, label='True')
    ax3.plot(xf, yf, 'r-o', linewidth=5, markersize=10, label='False')
    # Set labels and formatting (use same axis - ax1)
    #ax2.plot(xt+xf, yf, 'r-x', linewidth=2, markersize=4)
    ax3.set_ylabel('Probability', fontweight='bold', fontsize=20)
    ax3.set_xlabel(' Jitter Per Second', fontweight='bold', fontsize=20)
    ax3.set_title('CDF of Jitter Per Second', fontweight='bold', fontsize=25)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(bottom=0)
    ax3.legend(fontsize=20)
    ax3.tick_params(axis='both', 
                labelsize=20,        # Font size
                width=2,             # Tick width
                length=8,            # Tick length
                labelcolor='black')  # Tick label color"""

    # Adjust layout
    plt.tight_layout(rect=[0, 0.10, 1, 0.95])
    
    stats_text_true = f"""Statistics:
Expected Total Number of Collisions In The Network: {sum(total_colls_true) / end_stats_true['test_number']:.2f}
Expected Total Number of Packets From Tested Client: {end_stats_true['total_packets'] / end_stats_true['test_number']:.2f}
Expected Percentage of Lost Packets In The Client: {end_stats_true['lost_percent']:.2f}%
"""
#Number of Tests: {end_stats_true['test_number']}
 
 
    stats_text_false = f"""Statistics:
Expected Total Number of Collisions In The Network: {sum(total_colls_false) / end_stats_false['test_number']:.2f}
Expected Total Number of Packets From Tested Client: {end_stats_false['total_packets'] / end_stats_false['test_number']:.2f}
Expected Percentage of Lost Packets In The Client: {end_stats_false['lost_percent']:.2f}%
"""
#Number of Tests: {end_stats_false['test_number']}
    
    fig.text(0.02, 0.02, stats_text_false, fontsize=25, 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8))
    fig.text(0.98, 0.02, stats_text_true, fontsize=25, 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8), horizontalalignment='right')
    
    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=600, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()
    
    return fig





def pdf_histogram(data, bins=50):
    unique_values = np.unique(data)
    probabilities = []
    
    for value in unique_values:
        prob = np.sum(data == value) / len(data)
        probabilities.append(prob)
    
    return unique_values, probabilities

# Method 1: Manual CDF calculation
def empirical_cdf(data):

    sorted_data = np.sort(data)
    y = np.arange(1, len(sorted_data) + 1) / (len(sorted_data))
    
    return sorted_data, y


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect collision statistics')
    # Optional arguments
    parser.add_argument('-c', '--client', type=int, default=1, help='PDFs or CDFs as graph')
    parser.add_argument('-bw', '--bandwidth', type=int, default=1, help='Bandwidth in Mbytes')
    #parser.add_argument('-c', '--centair', action='store_true',default=False, help='With or without CentAir')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Duration of the test')
    args = parser.parse_args()
    
    bandwidth=args.bandwidth
    #centair=args.centair
    #graph_kind=args.graph
    dur=args.duration


    try:
        # Create the plots
        #cdf ya da pdf olduguna gore graph'lari ciz.
        dir_name=f"iperf3_analyses_{bandwidth}MB_centair_{dur}seconds_versus_client{args.client}MB"
        os.makedirs(dir_name,exist_ok=True)
        plot_iperf3_metrics( bandwidth,dur, args.client, save_path = f"{dir_name}/{dir_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()