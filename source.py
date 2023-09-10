import platform, socket, psutil, wmi, time, GPUtil
import paho.mqtt.client as mqtt
import json

import logging

logging.basicConfig(filename="infrastructure-analyzer.log",
                    level=logging.DEBUG)


# Read MQTT broker information from config.json file
with open("config.json") as config_file:
    config = json.load(config_file)

broker_ip = config["mqtt"]["broker_ip"]
broker_port = config["mqtt"]["broker_port"]

# MQTT client
client = mqtt.Client()


# MQTT callback function for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("connected OK")
    else:
        logging.info("conneted Fail", rc)


# MQTT callback function for disconnection
def on_disconnect(client, userdata, flags, rc=0):
    logging.info(str(rc))


# MQTT callback function for subscription
def on_subscribe(client, userdata, mid, granted_qos):
    logging.debug("subscribed: " + str(mid) + " " + str(granted_qos))


# MQTT callback function for receiving a message
def on_message(client, userdata, msg):
    received_topic = str(msg.topic)
    received_message = msg.payload.decode("utf-8")

    logging.info("received_topic: " + received_topic)
    logging.debug("received_message: " + received_message)

    # Handle by topic
    # All information
    if received_topic == "request/infra-info/host/":
        logging.info("Extract all information")
        # TBD: Extract all information

    # OS
    elif received_topic == "request/infra-info/host/os":
        os_object = {}
        os_object["os_name"] = os_name
        os_object["os_version"] = os_version
        os_object["os_architecture"] = architecture
        os_object["os_platform"] = platform_name
        response_object = {}
        response_object["os"] = os_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/os", response_message, 1)

    # Processor
    elif received_topic == "request/infra-info/host/process":
        process_object = {}
        process_object["processor_info"] = processor_info
        response_object = {}
        response_object["process"] = process_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/process", response_message, 1)

    # Computer
    elif received_topic == "request/infra-info/host/computer":
        computer_object = {}
        computer_object["hostname"] = hostname
        computer_object["ip_address"] = ip_address
        computer_object["window_edition"] = get_windows_edition()
        computer_object["computer_model"] = computer_model
        computer_object["computer_domain"] = computer_domain
        computer_object["computer_manufacturer"] = computer_manufacturer
        computer_object["physical_cores"] = physical_cores
        computer_object["logical_cores"] = logical_cores
        response_object = {}
        response_object["computer"] = computer_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/computer", response_message, 1)

    # Memory
    elif received_topic == "request/infra-info/host/memory":
        memory_object = {}
        memory_object["total_memory"] = total_memory
        memory_object["available_memory"] = available_memory
        memory_object["using_memory_percent"] = f"{memory_percent}%"
        memory_object["Total_Swap memory"] = total_swap
        memory_object["Used Swap memory"] = used_swap
        memory_object["Free Swap memory"] = free_swap
        memory_object["Swap Percent memory"] = f"{swap_percent}%"

        response_object = {}
        response_object["memory"] = memory_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/memory", response_message, 1)

    # Disk
    elif received_topic == "request/infra-info/host/disk":
        disk_object = {}
        disk_object["total_disk"] = total_disk
        disk_object["used_disk"] = used_disk
        disk_object["free_disk"] = free_disk
        disk_object["disk_percent"] = f"{disk_percent}%"

        response_object = {}
        response_object["disk"] = disk_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/disk", response_message, 1)

    # GPU
    elif received_topic == "request/infra-info/host/gpu":
        gpus = GPUtil.getGPUs()
        gpu_obejct_list = []
        for gpu in gpus:
            gpu_object = {}
            gpu_object["gpu_name"] = gpu.name
            gpu_object["gpu_driver"] = gpu.driver
            gpu_object["gpu_memoryTotal"] = gpu.memoryTotal
            gpu_object["gpu_memoryUsed"] = gpu.memoryUsed
            gpu_object["gpu_memoryFree"] = gpu.memoryFree
            gpu_object["gpu_load"] = gpu.load
            gpu_object["gpu_temperature"] = gpu.temperature
            gpu_obejct_list.append(gpu_object)

        response_object = {}
        response_object["gpus"] = gpu_obejct_list

        response_message = json.dumps(response_object)
        client.publish("info/infra/gpu", response_message, 1)

    # Processes
    elif received_topic == "request/infra-info/host/runningprocesses":
        runningprocesses_object = {}
        process_info = []

        for process in psutil.process_iter():
            try:
                process_info.append(
                    {
                        "PID": process.pid,
                        "Name": process.name(),
                        "Status": process.status(),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        runningprocesses_object["Processes"] = process_info
        response_object = {"runningprocesses": runningprocesses_object}

        response_message = json.dumps(response_object)
        client.publish("info/infra/runningprocesses", response_message, 1)

    # Network
    elif received_topic == "request/infra-info/host/network":
        network_object = {}
        for interface_name, interface_info in interfaces_info.items():
            interface_data = []
            for info in interface_info:
                interface_info_dict = {}
                if info.family == psutil.AF_LINK:
                    interface_info_dict["MAC_address"] = info.address
                elif info.family == socket.AF_INET:
                    interface_info_dict["IPv4_address"] = info.address
                    interface_info_dict["netmask"] = info.netmask
                elif info.family == socket.AF_INET6:
                    interface_info_dict["IPv6_address"] = info.address
                    interface_info_dict["CIDR_prefix"] = info.netmask
                interface_data.append(interface_info_dict)
            network_object[interface_name] = interface_data

        response_object = {}
        response_object["network"] = network_object

        response_message = json.dumps(response_object)
        client.publish("info/infra/network", response_message, 1)


# Assign the callback functions to its client
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message


#######################################################
# Extraction of Computing Infrastructure Information
os_name = platform.system()
os_version = platform.release()
architecture = platform.architecture()
platform_name = platform.platform()

hostname = socket.gethostname()
processor_info = platform.processor()
computer_model = platform.machine()

wmi_obj = wmi.WMI()
computer_domain = wmi_obj.Win32_ComputerSystem()[0].Domain

gpus = GPUtil.getGPUs()

computer_manufacturer = platform.system()
physical_cores = psutil.cpu_count(logical=False)
logical_cores = psutil.cpu_count(logical=True)

memory = psutil.virtual_memory()
total_memory = memory.total
available_memory = memory.available
memory_percent = memory.percent

swap_memory = psutil.swap_memory()
total_swap = swap_memory.total
used_swap = swap_memory.used
free_swap = swap_memory.free
swap_percent = swap_memory.percent

disk = psutil.disk_usage("/")
total_disk = disk.total
used_disk = disk.used
free_disk = disk.free
disk_percent = disk.used / disk.total * 100

running_processes = psutil.process_iter()


interfaces_info = psutil.net_if_addrs()
interfaces_info.items()

ip_address = socket.gethostbyname(hostname)


# 시스템 정보 출력 함수
def print_system_info():
    print(f"OS: {os_name}")
    print(f"OS version: {os_version}")
    print(f"OS architecture: {architecture}")
    print(f"OS platform: {platform_name}")
    print(f"Hostname: {hostname}")


# 프로세서 정보 추출 함수
def print_processor_info():
    print(f"\nProcessor info: {processor_info}")


# 윈도우 정보 추출 함수
def get_windows_edition():
    if platform.system() != "Windows":
        return "Windows 운영체제가 아닙니다."

    try:
        wmi_obj = wmi.WMI()
        version_info = wmi_obj.Win32_OperatingSystem()[0].Caption
        edition = version_info.split("|")[-1].strip()
        return edition
    except wmi.x_wmi:
        return "Windows 에디션 정보를 얻을 수 없습니다."


# 컴퓨터 모델 추출 함수
def get_computer_info():
    computer_model = platform.machine()

    if platform.system() == "Windows":
        try:
            wmi_obj = wmi.WMI()
            computer_domain = wmi_obj.Win32_ComputerSystem()[0].Domain
        except wmi.x_wmi:
            computer_domain = "도메인 정보를 얻을 수 없습니다."
    else:
        computer_domain = "Windows 운영체제가 아닙니다."

    computer_manufacturer = platform.system()
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)

    print(f"\nComputer Model: {computer_model}")
    print(f"Computer Domain: {computer_domain}")  # 오류
    print(f"Computer Manufacturer : {computer_manufacturer}")
    print(f"Pygical cores: {physical_cores}")
    print(f"Logical cores: {logical_cores}")


# 메모리 정보 추출 함수
def print_memory_info():
    total_memory = memory.total
    available_memory = memory.available
    memory_percent = memory.percent
    print(f"\nMemory_total: {total_memory} bytes")
    print(f"Available_Memory: {available_memory} bytes")
    print(f"Memory_usage: {memory_percent}%")
    print(f"Total_Swap memory: {total_swap} bytes")
    print(f"Used Swap: {used_swap} bytes")
    print(f"Free Swap: {free_swap} bytes")
    print(f"Swap Percent: {swap_percent}%")


# 그래픽 정보 추출 함수
def print_all_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("사용 가능한 GPU 정보가 없습니다.")
            return

        # GPU 정보를 리스트에 저장
        for gpu in gpus:
            gpu_info = {
                "Gpu_name": gpu.name,
                "Gpu_driver": gpu.driver,
                "Gpu_memory": gpu.memoryTotal,
                "Gpu_memory in use": gpu.memoryUsed,
                "GPu_available memory": gpu.memoryFree,
                "GPU_usage": gpu.load * 100,
                "Gpu_temperature": gpu.temperature,
            }

    except ImportError:
        print("Unable to get GPU information.")

    print(gpu_info)


# 디스크 정보 추출 함수#
def print_disk_info():
    total_disk = disk.total
    used_disk = disk.used
    free_disk = disk.free
    disk_percent = disk.used / disk.total * 100
    print(f"\nDisk_total: {total_disk} bytes")
    print(f"Disk_used: {used_disk} bytes")
    print(f"Disk_available: {free_disk} bytes")
    print(f"Disk_usage: {disk_percent}%")


# 네트워크 정보 추출 함수#
def print_network_info():
    print(f"\nIP addreses: {ip_address}")

    for interface_name, interface_info in interfaces_info.items():
        print_interface_info(interface_name, interface_info)


# 실행중인 프로세스 정보 추출 함수
def print_runnigprocess_info():
    running_processes = psutil.process_iter()
    process_info = []

    for process in running_processes:
        try:
            process_info.append({
                "PID": process.pid,
                "Name": process.name(),
                "Status": process.status()
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print("\nRunning Processes Information :", process_info)


# 인터페이스 정보 추출 함수
def print_interface_info(interface_name, interface_info):
    network_object = {}
    print(f"\nInterface --{interface_name}-- Information")
    for info in interface_info:
        if info.family == psutil.AF_LINK:
            print(f"MAC address: {info.address}")
        elif info.family == socket.AF_INET:
            print(f"IPv4 address: {info.address}")
            print(f"Netmask: {info.netmask}")
        elif info.family == socket.AF_INET6:
            print(f"IPv6 address: {info.address}")
    return network_object


def main():
    print("========== Computing Infrastructure Shape Analysis ==========")
    # 시스템 정보
    print_system_info()

    # 프로세서 정보
    print_processor_info()

    # 컴퓨터 모델 정보
    get_computer_info()

    # 메모리 정보
    print_memory_info()

    # GPU 정보
    print_all_gpu_info()

    # 디스크 정보
    print_disk_info()

    # 실행중인 프로세스 정보
    print_runnigprocess_info()

    # 네트워크 정보
    print_network_info()

    # 실행파일화면 출력 시간
    time.sleep(5)

    print("=" * 61)

    # 로컬 아닌, 원격 mqtt broker에 연결
    # port: 1883 에 연결
    client.connect(broker_ip, broker_port)
    # request/infra-info/host/# 라는 topic 구독
    client.subscribe("request/infra-info/host/#", 1)
    client.loop_forever()


if __name__ == "__main__":
    main()
