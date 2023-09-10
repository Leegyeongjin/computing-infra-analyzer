<img src="https://img.shields.io/badge/python-3776AB?style=flat&logo=python&logoColor=white"/><img src="https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=HTML5&logoColor=white"/><img src="https://img.shields.io/badge/flask-000000?style=flat&logo=flask&logoColor=white"/><img src="https://img.shields.io/badge/eclipsemosquitto-3C5280?style=flat&logo=eclipsemosquitto&logoColor=white"/><img src="https://img.shields.io/badge/socket.io-010101?style=flat&logo=socket.io&logoColor=white"/><img src="https://img.shields.io/badge/json-000000?style=flat&logo=json&logoColor=white"/>

# Computing Infra Analysis

## Introduction

클라우드 유연성을 바탕으로 비즈니스 민첩성을 극대화 하고자
물리 환경, 가상 환경, 사설 클라우드(Private Cloud) 등을 상용 클라우드(Public Cloud)로 마이그레이션하는 니즈가 점차 확대되고 있다.

컴퓨팅 인프라 정보를 추출, 분석 및 활용이 가능해질 경우, 클라우드 마이그레이션을 더욱 효율적으로 수행할 수 있을 것이라 전망한다.

이를 위해, 컴퓨팅 인프라 형상 분석 시스템을 연구 개발하고 있으며, 시스템 구성도(초안)은 아래와 같다.

<p align="center">
  <img src="https://github.com/cloud-barista/poc-infra-analysis/assets/7975459/0b446a1b-ea66-4459-aeb6-92cd78aed68d" width="80%" height="80%"/>
</p>


## 시스템 실행 가이드

시스템을 실행하기 위한 전반적인 순서는 다음과 같다.
1. MQTT Broker 설치 및 구동
2. Infrastructure Magnifier (IM) 배포 및 구동
3. Infrastructure Analyzer (Agent) 배포 및 구동

### 1. MQTT Broker 설치 및 구동

Ubuntu 20.04에 설치를 수행한다.

#### Mosquitto Broker 설치
```bash
sudo apt-get update -y
sudo apt-get install mosquitto -y
```

#### Mosquitto 상태 확인
```bash
sudo /etc/init.d/mosquitto status
```

#### 출력 메시지
```bash
 * mosquitto is not running
```

중요 - Mosquitto Broker의 기본 Port는 `1883`이며, 이후 과정을 위해 물리/가상머신의 Public IP 또는 Domain이 필요하다.


### 2. Infrastructure Magnifier (IM) 배포 및 구동

1번과 같은 물리/가상머신에 소스코드를 기반으로 구동한다.

#### 선행사항

1. Python 설치
소스코드 실행을 위해 Python을 설치한다.
```bash
sudo apt-get update
sudo apt-get install python3.11 -y
```

2. Personal Access Token 생성
Private 저장소 이므로, Personal Access Token (PAT)이 필요하다.

생성 방법 참고: [Managing your personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

3. git 설치 (선택사항)
git이 설치되이 있지 않은경우, 설치한다.
```bash
sudo apt-get update
sudo apt-get install git -y
```
설치 확인
```bash
git --version
```

#### 소스코드 가져오기
아래 명령어를 통해 GitHub 저장소를 클론(Clone)하며, Username과 PAT가 필요하다.
```bash
git clone https://github.com/cloud-barista/poc-infra-analysis.git
```

#### config.json 설정

config-template.json을 복사하여 config.json을 생성한다.
```bash
cp config-template.json config.json
```

과정 1에서 파악해 놓은 물리/가상머신의 Public IP 또는 Domain 주소를 입력한다.
```json
{
  "mqtt": {
    "broker_ip": "<YOUR_BROKER_ENDPOINT>",
    "broker_port": 1883
  }
}
```

#### 필요 Python module 설치
```bash
pip install -r requirements.txt 
```

#### Infrastructure Magnifier 실행
```bash
python3 server.py
```

#### 웹사이트 접속 
물리/가상머신의 Public IP 및 5000번 포트로 웹사이트에 접속한다(예, http://PublicIP:Port)

<p align="center">
  <img src="https://github.com/cloud-barista/poc-infra-analysis/assets/7975459/933eab60-5087-4bea-8fd4-cf12139869c5" width="80%" height="80%"/>
</p>


### 3. Infrastructure Analyzer (Agent) 배포 및 구동

컴퓨팅 인프라의 형상을 분석해야하는 물리/가상머싱에 배포 및 구동되며(예, Ubuntu, Windows), 
여기에서는 Ubuntu 20.04에 배포 및 구동 방법을 설명한다.

선행사항을 포함한 대부분의 과정이 2번과 동일하여 실행에 대해서만 설명한다.

#### Infrastructure Analyzer (Agent) 실행
```bash
python3 source.py
```
