#!/bin/bash

bandwidth="${1:-10}"
client_bw="${2:-1}"
centair="${3:-false}"
duration="${4:-60}"


timestamp_basic=$(date +"%Y-%m-%d_%H-%M-%S")

foldername="bw_${bandwidth}M_centair_${centair}_${duration}_clientBW_${client_bw}_${timestamp_basic}"

(
cd /home/ahmet/Desktop/okul/bitirme_uzerine/tuntap_yontemi/scriptler
./remote_exec "pkill iperf3" \
&& ./remote_exec "rm -f *log*" \
&& ./remote_exec "rm -f coll_stats*" \
&& ./remote_exec "batctl collmod reset" 
if [[ "$centair" == "true" ]]; then
    ./remote_exec -h "192.168.102.16" "batctl hopmod stop"
    sleep 1
    ./remote_exec "batctl hp 30"
fi
)


(

cd /home/ahmet/Desktop/okul/bitirme_uzerine/tuntap_yontemi/scriptler/

if [[ "$centair" == "true" ]]; then
    ./remote_exec -h "192.168.102.16" "batctl hopmod centair 350"
    sleep 5
fi

#./remote_exec "batctl it 200"
./remote_exec "batctl collmod set_mode 1" \
&& ./remote_exec "batctl collmod set_threshold 1000" \
&& ./remote_exec -h "192.168.102.16" "batctl collmod set_threshold 10000" \
&& ./remote_exec -h "192.168.102.13" "(iperf3 -s -J --logfile server_log_${timestamp_basic} > cmd_log 2>&1 &) && exit" \
&& ./remote_exec -h "192.168.102.14" "(iperf3 -s --logfile server_log > cmd_log 2>&1 &) && exit" \
&& ./remote_exec -h "192.168.102.15" "(iperf3 -s --logfile server_log > cmd_log 2>&1 &) && exit"

sleep 5

./remote_exec -h "192.168.102.11" "(iperf3 -c 192.168.101.14 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit" \
&& ./remote_exec -h "192.168.102.12" "(iperf3 -c 192.168.101.15 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit"




while true; do 
    sleep 3
    tainted=0
    
    output=$(./remote_exec -h "192.168.102.11" "cat client_log")
    echo "$output"
    if echo "$output" | grep -q "Empty output"; then 
        ./remote_exec -h "192.168.102.11" "pkill iperf3"
        ./remote_exec -h "192.168.102.11" "rm -f client_log"
        sleep 1
        ./remote_exec -h "192.168.102.11" "(iperf3 -c 192.168.101.14 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit"
        tainted=1
        echo "192.168.102.11, something is not right..."
    fi

    output=$(./remote_exec -h "192.168.102.12" "cat client_log")
    echo "$output"
    if echo "$output" | grep -q "Empty output"; then 
        ./remote_exec -h "192.168.102.12" "pkill iperf3"
        ./remote_exec -h "192.168.102.12" "rm -f client_log"
        sleep 1
        ./remote_exec -h "192.168.102.12" "(iperf3 -c 192.168.101.14 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit"
        echo "192.168.102.12, something is not right..."
        tainted=1
    fi

    if [[ $tainted -eq 0 ]]; then
        echo "Is everything okay? (y/n): "
        read -r answer
        if [[ "$answer" == "y" || "$answer" == "yes" || "$answer" == "Y" || "$answer" == "Yes" ]]; then
            echo "Great, let's continue..."
            break
        else
            echo "Here wo go again"
            ./remote_exec -h "192.168.102.11" "pkill iperf3"
            ./remote_exec -h "192.168.102.11" "rm -f client_log"
            ./remote_exec -h "192.168.102.12" "pkill iperf3"
            ./remote_exec -h "192.168.102.12" "rm -f client_log"
            sleep 1
            ./remote_exec -h "192.168.102.11" "(iperf3 -c 192.168.101.14 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit" \
            && ./remote_exec -h "192.168.102.12" "(iperf3 -c 192.168.101.15 -u -t 600 -b ${bandwidth}M --logfile client_log > cmd_log 2>&1 &) && exit"
        fi
    fi
done

sleep 2


./remote_exec -h "192.168.102.10" "(iperf3 -c 192.168.101.13 -u -t ${duration} -b ${client_bw}M --logfile client_log > cmd_log 2>&1 &) && exit" \
&& ./remote_exec "(python3 collect_collision.py -t ${duration} > pylog 2>&1 &) && exit"



while true; do
    sleep 3
    ./remote_exec -h "192.168.102.10" "cat client_log"  
    echo "Is everything okay? (y/n): "
    read -r answer

    if [[ "$answer" == "y" || "$answer" == "yes" || "$answer" == "Y" || "$answer" == "Yes" ]]; then
        
        echo "Nice, let's continue..."
        break

    else
        
        # Continue with your script
        #Test edilen client'i oldur ve collision data'larini toplayan
        #script'i tum node'larda oldur ve loglarini temizle.
        ./remote_exec -h "192.168.102.10" "pkill iperf3" \
        && ./remote_exec "pkill -f collect_collision.py"
        ./remote_exec "rm -f coll_stats*"
        ./remote_exec -h "192.168.102.10" "rm -f client_log"
        #Server'i oldur ve log'larini temizle
        ./remote_exec -h "192.168.102.13" "pkill iperf3"
        ./remote_exec -h "192.168.102.13" "rm -f server_log*"

        sleep 1
        #Test edilen server'i tekrar baslat
        ./remote_exec -h "192.168.102.13" "(iperf3 -s -J --logfile server_log_${timestamp_basic} > cmd_log 2>&1 &) && exit"

        sleep 2
        #Test edilen client'i ve collision collector'i her node'da tekrar baslat
        ./remote_exec -h "192.168.102.10" "(iperf3 -c 192.168.101.13 -u -t ${duration} -b ${client_bw} --logfile client_log > cmd_log 2>&1 &) && exit" \
        && ./remote_exec "(python3 collect_collision.py -t ${duration} > pylog 2>&1 &) && exit"
    fi
done

wait=$((duration + 10))
duration=15
for ((i=wait; i>0; i--)); do echo -ne "\r$i seconds remaining..."; sleep 1; done; echo -e "\rFinished!            "

)

mkdir -p "${foldername}"


cd "${foldername}"

scp ahmet3@192.168.102.13:/home/ahmet3/server_log* . \
&& scp ahmet3@192.168.102.10:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.11:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.12:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.13:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.14:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.15:/home/ahmet3/coll_stats*.csv . \
&& scp ahmet3@192.168.102.16:/home/ahmet3/coll_stats*.csv . 




(
cd /home/ahmet/Desktop/okul/bitirme_uzerine/tuntap_yontemi/scriptler
./remote_exec "pkill iperf3" \
&& ./remote_exec "rm -f *log*" \
&& ./remote_exec "rm -f coll_stats*" \
&& ./remote_exec "batctl collmod reset" 
if [[ "$centair" == "true" ]]; then
    ./remote_exec -h "192.168.102.16" "batctl hopmod stop"
    sleep 1
    ./remote_exec "batctl hp 30"
fi
)