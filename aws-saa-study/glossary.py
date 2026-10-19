"""Glossary: one entry per term. Used for tap-to-define popovers and the glossary topic.

Format of RAW (blank line between entries):
  id | 표시 이름 | English | 한국어 공식 표기 | 자세한 주제 id | 본문에서 찾을 표기(;로 구분) | 갈래
  뜻 (1~2문장, markdown 가능)
The detail topic is the topic that actually explains the term; inside that topic the term is not marked.
"""
import html
import markdown

CATEGORIES = [
    ('base', '클라우드와 AWS 기초'), ('iam', '계정, 권한, 보안'), ('compute', '컴퓨팅'), ('storage', '스토리지'),
    ('db', '데이터베이스'), ('net', '네트워크와 콘텐츠 전송'), ('int', '메시징과 애플리케이션 통합'),
    ('serverless', '서버리스와 컨테이너'), ('data', '데이터 분석과 AI'), ('ops', '모니터링, 운영, 비용'),
    ('dr', '마이그레이션과 재해 복구'), ('exam', '시험 용어'),
]

RAW = r"""
cloud | 클라우드 컴퓨팅 | Cloud computing | 클라우드 컴퓨팅 | start-terms | 클라우드 컴퓨팅 | base
서버, 저장소, 네트워크 같은 IT 자원을 인터넷으로 필요한 만큼 빌려 쓰고 쓴 만큼 내는 방식입니다.

region | 리전 | AWS Region | 리전 | c03-global | 리전;Region | base
AWS 데이터 센터들이 모여 있는 지리적 지역입니다(예: 서울 `ap-northeast-2`). 리전마다 쓸 수 있는 서비스와 요금이 조금씩 다르고, 데이터는 사용자가 옮기지 않으면 리전 밖으로 나가지 않습니다.

az | 가용 영역 | Availability Zone (AZ) | 가용 영역 | c03-global | 가용 영역;AZ;Availability Zone | base
리전 안에서 전원, 냉각, 네트워크가 분리된 하나 이상의 데이터 센터 묶음입니다. 대부분의 리전에 3개 이상 있고, 여러 AZ에 나눠 두면 한 곳이 멈춰도 서비스가 이어집니다.

edge | 엣지 로케이션 | Edge location (Point of Presence) | 엣지 로케이션 | c03-global | 엣지 로케이션;Edge location | base
사용자 가까이 있는 AWS 접속 지점입니다. CloudFront 캐시, Route 53, Global Accelerator가 여기서 동작해 지연 시간을 줄입니다.

latency | 지연 시간 | Latency | 지연 시간 | c03-global | 지연 시간 | base
요청을 보내고 응답이 오기까지 걸리는 시간입니다. 사용자와 서버가 멀수록 길어집니다.

iaas | IaaS, PaaS, SaaS | Infrastructure / Platform / Software as a Service |  | c03-global | IaaS;PaaS;SaaS | base
클라우드가 어디까지 대신 맡는지에 따른 구분입니다. IaaS는 가상 서버와 네트워크(EC2), PaaS는 실행 환경까지(Elastic Beanstalk), SaaS는 완성된 소프트웨어입니다.

managed | 관리형 서비스 | Managed service | 관리형 서비스 | start-terms | 관리형 서비스;완전 관리형 | base
설치, 패치, 백업, 확장 같은 운영을 AWS가 맡는 서비스입니다. 문제에 "운영 오버헤드 최소"가 나오면 관리형을 먼저 떠올립니다.

storage-types | 블록, 파일, 객체 스토리지 | Block / File / Object storage |  | start-terms | 블록 스토리지;파일 스토리지;객체 스토리지 | storage
블록은 디스크처럼 OS가 직접 포맷해 쓰고(EBS), 파일은 폴더 구조를 여럿이 함께 쓰며(EFS, FSx), 객체는 파일을 키로 통째로 넣고 꺼냅니다(S3).

shared-resp | 공동 책임 모델 | Shared responsibility model | 공동 책임 모델 | c04-role | 공동 책임 모델 | iam
AWS는 "클라우드 자체"(데이터 센터, 하드웨어, 가상화 계층)를, 고객은 "클라우드 안"(데이터, 계정과 권한, OS 패치, 보안 그룹 설정)을 책임진다는 원칙입니다.

ha | 고가용성 | High availability | 고가용성 | c08-ha | 고가용성 | base
일부가 고장 나도 서비스가 계속 동작하는 성질입니다. AWS에서는 보통 여러 AZ에 나눠 두는 것으로 만듭니다.

scalability | 확장성 | Scalability | 확장성 | c08-ha | 확장성 | base
부하가 늘어도 자원을 늘려 감당하는 능력입니다. 서버를 키우는 수직 확장과 대수를 늘리는 수평 확장이 있습니다.

horizontal | 수평 확장 | Horizontal scaling (scale out / in) | 수평 확장 | c08-ha | 수평 확장;스케일 아웃 | base
서버 대수를 늘리거나(scale out) 줄이는(scale in) 확장입니다. Auto Scaling 그룹이 이 일을 합니다.

vertical | 수직 확장 | Vertical scaling (scale up / down) | 수직 확장 | c08-ha | 수직 확장;스케일 업 | base
서버 한 대의 크기(CPU, 메모리)를 키우는 확장입니다. 한계가 있고 보통 재시작이 필요합니다.

stateless | 무상태 | Stateless |  | c11-stateless | 무상태;stateless | base
서버가 요청 사이에 사용자 정보를 기억하지 않는 구조입니다. 어느 서버가 받아도 결과가 같아 수평 확장이 쉽습니다.

decouple | 느슨한 결합 | Loose coupling (decoupling) |  | c17-sqs | 느슨한 결합;디커플링 | int
구성 요소가 서로를 직접 부르지 않고 대기열이나 이벤트로 이어져, 한쪽이 느려지거나 멈춰도 다른 쪽이 영향을 덜 받는 구조입니다.

op-overhead | 운영 오버헤드 | Operational overhead |  | x-keywords | 운영 오버헤드 | exam
사람이 직접 설치, 패치, 확장, 모니터링해야 하는 일의 양입니다. "최소 운영 오버헤드"는 관리형이나 서버리스를 고르라는 신호입니다.

quota | 서비스 할당량 | Service quotas |  | x-numbers | 서비스 할당량 | ops
계정과 리전마다 정해진 자원 한도입니다(예: 리전당 VPC 5개). 대부분 Service Quotas 콘솔에서 늘려 달라고 요청할 수 있습니다.

iam | IAM | AWS Identity and Access Management | IAM | c04-iam | IAM | iam
누가(인증) 무엇을 할 수 있는지(인가)를 관리하는 글로벌 서비스입니다. 사용자, 그룹, 역할, 정책으로 이루어집니다.

root | 루트 사용자 | Root user | 루트 사용자 | c04-iam | 루트 사용자;루트 계정 | iam
계정을 만들 때 쓴 이메일로 로그인하는, 모든 권한을 가진 사용자입니다. MFA를 걸어 두고 일상 업무에는 쓰지 않습니다.

iam-user | IAM 사용자 | IAM user | IAM 사용자 | c04-iam | IAM 사용자 | iam
계정 안에서 사람이나 프로그램 하나를 나타내는 장기 자격 증명입니다. 콘솔은 비밀번호로, CLI와 SDK는 액세스 키로 로그인합니다.

iam-group | IAM 그룹 | IAM user group | 사용자 그룹 | c04-iam | IAM 그룹;사용자 그룹 | iam
사용자를 묶어 같은 정책을 한 번에 주는 단위입니다. 그룹 안에 그룹을 넣을 수 없습니다.

iam-policy | IAM 정책 | IAM policy | IAM 정책 | c04-policy | IAM 정책;자격 증명 기반 정책 | iam
허용하거나 거부할 작업(Action), 대상(Resource), 조건(Condition)을 JSON으로 적은 문서입니다. 사용자, 그룹, 역할에 붙입니다.

least-priv | 최소 권한 원칙 | Principle of least privilege | 최소 권한 원칙 | c04-policy | 최소 권한 원칙;최소 권한 | iam
일에 꼭 필요한 권한만 주는 원칙입니다. 보안 문제의 보기 대부분이 이 원칙으로 갈립니다.

mfa | MFA | Multi-factor authentication | 멀티 팩터 인증(MFA) | c04-iam | MFA;다중 인증 | iam
비밀번호에 더해 휴대폰 앱이나 보안 키의 일회용 코드를 함께 요구하는 로그인 방식입니다.

access-key | 액세스 키 | Access key | 액세스 키 | c04-cli | 액세스 키 | iam
CLI와 SDK가 AWS API를 부를 때 쓰는 키 ID와 비밀 키 한 쌍입니다. 코드나 EC2에 넣어 두지 말고 IAM 역할을 씁니다.

cli | AWS CLI | AWS Command Line Interface | AWS CLI | c04-cli | AWS CLI | iam
터미널에서 `aws` 명령으로 AWS를 다루는 도구입니다. 콘솔과 같은 API를 부릅니다.

sdk | SDK | Software Development Kit | SDK | c04-cli | SDK | iam
Python, Java 같은 프로그래밍 언어에서 AWS API를 부르게 해 주는 라이브러리입니다.

iam-role | IAM 역할 | IAM role | IAM 역할 | c04-role | IAM 역할;IAM Role | iam
EC2, Lambda 같은 서비스나 다른 계정의 사용자가 잠시 맡는 권한 묶음입니다. 맡는 순간 STS가 임시 자격 증명을 발급합니다.

sts | STS | AWS Security Token Service | AWS STS | c04-role | STS;AssumeRole | iam
역할을 맡을 때 몇 분에서 몇 시간만 유효한 임시 자격 증명을 발급하는 서비스입니다.

instance-profile | 인스턴스 프로파일 | Instance profile | 인스턴스 프로파일 | c05-connect | 인스턴스 프로파일 | iam
EC2에 IAM 역할을 붙이는 통로입니다. 인스턴스 안의 프로그램은 액세스 키 없이 이 역할의 임시 자격 증명을 씁니다.

cred-report | 자격 증명 보고서 | IAM credential report | 자격 증명 보고서 | c04-role | 자격 증명 보고서 | iam
계정의 모든 IAM 사용자와 비밀번호, 액세스 키, MFA 상태를 CSV로 보여 주는 보고서입니다.

access-advisor | 마지막 액세스 정보 | IAM Access Advisor (last accessed information) | 마지막으로 액세스한 정보 | c04-role | Access Advisor | iam
사용자나 역할이 각 서비스를 마지막으로 언제 썼는지 보여 줍니다. 안 쓰는 권한을 걷어 내는 근거가 됩니다.

org | AWS Organizations | AWS Organizations | AWS Organizations | c25-org | Organizations | iam
여러 AWS 계정을 하나의 조직으로 묶어 결제를 합치고(통합 결제), 정책으로 한꺼번에 통제하는 서비스입니다.

ou | 조직 단위(OU) | Organizational unit | 조직 단위(OU) | c25-org | OU;조직 단위 | iam
Organizations 안에서 계정을 묶는 폴더입니다. OU에 SCP를 붙이면 그 아래 계정 모두에 적용됩니다.

scp | SCP | Service control policy | 서비스 제어 정책(SCP) | c25-org | SCP;서비스 제어 정책 | iam
조직의 계정이 가질 수 있는 최대 권한을 정하는 정책입니다. 권한을 주지는 않고 막기만 하며, 관리 계정에는 적용되지 않습니다.

rcp | RCP | Resource control policy | 리소스 제어 정책(RCP) | c25-org | RCP;리소스 제어 정책 | iam
조직 안 리소스(S3, KMS 등)에 누가 접근할 수 있는지의 최대치를 정하는 정책입니다(2024-11 출시). SCP는 주체를, RCP는 리소스를 제한합니다.

perm-boundary | 권한 경계 | Permissions boundary | 권한 경계 | c25-policy-adv | 권한 경계 | iam
사용자나 역할에 붙여 "이 이상은 못 한다"는 최대 권한을 정하는 정책입니다. 실제 권한은 자격 증명 정책과 권한 경계가 둘 다 허용하는 부분입니다.

resource-policy | 리소스 기반 정책 | Resource-based policy | 리소스 기반 정책 | c25-resource | 리소스 기반 정책 | iam
S3 버킷, SQS 대기열, KMS 키처럼 리소스 쪽에 붙이는 정책입니다. `Principal`로 누가 쓸 수 있는지 적어 다른 계정에 열어 줄 수 있습니다.

identity-center | IAM Identity Center | AWS IAM Identity Center | IAM Identity Center | c25-identity-center | IAM Identity Center;Identity Center | iam
여러 AWS 계정과 업무용 앱에 한 번 로그인(SSO)으로 들어가게 하는 서비스입니다. 옛 이름은 AWS SSO입니다.

sso | SSO | Single sign-on | 통합 인증(SSO) | c25-identity-center | SSO;싱글 사인온 | iam
한 번 로그인해서 여러 시스템을 쓰는 방식입니다.

federation | 페더레이션 | Identity federation | 자격 증명 연동 | c25-identity-center | 페더레이션 | iam
회사 디렉터리나 외부 IdP에서 로그인한 사람이 AWS 역할을 맡게 해, IAM 사용자를 따로 만들지 않는 방식입니다.

saml | SAML 2.0 | Security Assertion Markup Language 2.0 | SAML 2.0 | c25-identity-center | SAML | iam
회사 IdP가 "이 사람은 인증됐다"는 증명을 AWS에 넘겨 주는 표준입니다.

ad | Active Directory | Microsoft Active Directory |  | c25-identity-center | Active Directory | iam
회사의 사용자, 그룹, 컴퓨터를 관리하는 마이크로소프트의 디렉터리 서비스입니다.

directory-service | AWS Directory Service | AWS Directory Service | AWS Directory Service | c25-identity-center | Directory Service;Managed Microsoft AD;AD Connector;Simple AD | iam
AWS에서 Active Directory를 쓰는 세 방법(AWS Managed Microsoft AD, AD Connector, Simple AD)을 제공하는 서비스입니다.

control-tower | Control Tower | AWS Control Tower | AWS Control Tower | c25-control-tower | Control Tower | iam
모범 사례대로 여러 계정 환경(랜딩 존)을 자동으로 만들고, 통제(control)로 규칙 위반을 막거나 찾아 주는 서비스입니다.

cognito | Cognito | Amazon Cognito | Amazon Cognito | c19-cognito | Cognito;사용자 풀;자격 증명 풀 | iam
웹과 모바일 앱 사용자의 가입, 로그인(사용자 풀)과, 그 사용자에게 AWS 임시 자격 증명을 주는 기능(자격 증명 풀)을 제공합니다.

ec2 | EC2 | Amazon Elastic Compute Cloud | Amazon EC2 | c05-ec2 | EC2 | compute
AWS에서 빌려 쓰는 가상 서버입니다. 인스턴스 유형으로 CPU와 메모리를 고르고 초 단위로 요금을 냅니다.

instance | 인스턴스 | EC2 instance | 인스턴스 | c05-ec2 | 인스턴스 | compute
실행 중인 가상 서버 한 대입니다.

ami | AMI | Amazon Machine Image | Amazon 머신 이미지(AMI) | c07-snapshot-ami | AMI;머신 이미지 | compute
EC2를 띄울 때 쓰는 OS, 설정, 소프트웨어가 담긴 틀입니다. 리전마다 따로 있고 다른 리전으로 복사할 수 있습니다.

user-data | 사용자 데이터 | EC2 user data | 사용자 데이터 | c05-ec2 | 사용자 데이터;User Data | compute
인스턴스가 처음 부팅할 때 root 권한으로 한 번 실행되는 스크립트입니다. 패키지 설치 같은 초기 작업에 씁니다.

instance-type | 인스턴스 유형 | Instance type | 인스턴스 유형 | c05-types | 인스턴스 유형;인스턴스 패밀리 | compute
CPU, 메모리, 네트워크 조합의 규격입니다. `m5.large`는 패밀리(m), 세대(5), 크기(large)로 읽습니다.

sg | 보안 그룹 | Security group | 보안 그룹 | c05-sg | 보안 그룹;Security Group | net
인스턴스(정확히는 ENI)에 붙는 가상 방화벽입니다. 허용 규칙만 있고, 들어온 요청의 응답은 자동으로 나갑니다(상태 저장).

stateful | 상태 저장 방화벽 | Stateful firewall | 상태 저장 | c27-nacl | 상태 저장;상태 비저장 | net
상태 저장은 들어온 연결을 기억해 그 응답을 규칙 없이 통과시킵니다(보안 그룹). 상태 비저장은 응답도 규칙으로 따로 열어야 합니다(NACL).

ssh | SSH | Secure Shell | SSH | c05-connect | SSH | compute
원격 서버에 암호화된 터미널로 접속하는 방법입니다. 22번 포트를 씁니다.

instance-connect | EC2 Instance Connect | Amazon EC2 Instance Connect | EC2 Instance Connect | c05-connect | EC2 Instance Connect;Instance Connect | compute
브라우저에서 키 파일 없이 SSH로 접속하게 하는 기능입니다. 보안 그룹에서 22번 포트는 열려 있어야 합니다.

session-manager | Session Manager | AWS Systems Manager Session Manager | Session Manager | c30-ssm | Session Manager | ops
22번 포트와 배스천 없이 콘솔이나 CLI로 인스턴스에 접속하는 기능입니다. SSM 에이전트와 IAM 역할이 필요하고 접속 기록을 남길 수 있습니다.

on-demand | 온디맨드 인스턴스 | On-Demand Instances | 온디맨드 인스턴스 | c05-purchase | 온디맨드 | compute
약정 없이 쓴 시간만큼 내는 기본 요금 방식입니다. 가장 비싸지만 언제든 시작하고 멈출 수 있습니다.

ri | 예약 인스턴스 | Reserved Instances (RI) | 예약 인스턴스 | c05-purchase | 예약 인스턴스;Reserved Instance | compute
특정 인스턴스 속성을 1년 또는 3년 쓰겠다고 약정하고 크게 할인받는 방식입니다(최대 약 72%).

savings-plans | Savings Plans | Savings Plans | Savings Plans | c05-purchase | Savings Plans | compute
시간당 사용 금액(예: 시간당 10달러)을 1년 또는 3년 약정하고 할인받는 방식입니다. Compute Savings Plans는 인스턴스 패밀리, 리전, Fargate, Lambda까지 넘나들 수 있습니다.

spot | 스팟 인스턴스 | Spot Instances | 스팟 인스턴스 | c05-purchase | 스팟 인스턴스;스팟;Spot Instance | compute
AWS의 남는 용량을 최대 90% 싸게 빌리는 방식입니다. AWS가 용량이 필요하면 2분 전에 알리고 회수하므로 중단돼도 되는 일에 씁니다.

spot-fleet | 스팟 플릿 | Spot Fleet | 스팟 플릿 | c05-purchase | 스팟 플릿;Spot Fleet | compute
여러 인스턴스 유형과 AZ의 스팟(과 온디맨드)을 섞어 목표 용량을 채우는 기능입니다. 가격 우선, 용량 우선 같은 할당 전략을 고릅니다.

dedicated-host | 전용 호스트 | Dedicated Hosts | 전용 호스트 | c05-purchase | 전용 호스트;Dedicated Host | compute
물리 서버 한 대를 통째로 빌리는 방식입니다. 소켓·코어 단위 소프트웨어 라이선스(BYOL)나 규정 준수에 씁니다.

dedicated-instance | 전용 인스턴스 | Dedicated Instances | 전용 인스턴스 | c05-purchase | 전용 인스턴스 | compute
다른 고객과 하드웨어를 같이 쓰지 않는 인스턴스입니다. 물리 서버 자체를 고르거나 들여다보지는 못합니다.

capacity-reservation | 용량 예약 | On-Demand Capacity Reservations | 온디맨드 용량 예약 | c05-purchase | 용량 예약;Capacity Reservation | compute
특정 AZ에 인스턴스 자리를 미리 잡아 두는 기능입니다. 할인은 없고 쓰지 않아도 요금이 나갑니다.

eip | 탄력적 IP | Elastic IP address | 탄력적 IP 주소 | c06-ip | 탄력적 IP;Elastic IP | net
계정이 소유하는 고정 공인 IPv4 주소입니다. 인스턴스가 바뀌어도 같은 주소를 옮겨 붙일 수 있습니다.

public-ip | 공인 IP | Public IPv4 address | 퍼블릭 IPv4 주소 | c06-ip | 공인 IP;퍼블릭 IP | net
인터넷에서 찾아올 수 있는 주소입니다. EC2를 중지했다가 시작하면 바뀝니다. 2024-02부터 공인 IPv4는 쓰는 동안 시간당 요금이 붙습니다.

private-ip | 사설 IP | Private IPv4 address | 프라이빗 IPv4 주소 | c06-ip | 사설 IP;프라이빗 IP | net
VPC 안에서만 쓰는 주소입니다(10.x, 172.16–31.x, 192.168.x). 인터넷에서 바로 찾아오지 못합니다.

placement-group | 배치 그룹 | Placement group | 배치 그룹 | c06-placement | 배치 그룹;Placement Group | compute
인스턴스를 물리적으로 어떻게 놓을지 정하는 기능입니다. 모아 두기(클러스터), 흩어 두기(분산), 칸 나누기(파티션)가 있습니다.

eni | ENI | Elastic network interface | 탄력적 네트워크 인터페이스 | c06-eni-hibernate | ENI;네트워크 인터페이스 | net
VPC 안의 가상 랜카드입니다. 사설 IP와 보안 그룹이 여기에 붙고, 같은 AZ의 다른 인스턴스로 옮겨 붙일 수 있습니다.

hibernate | 최대 절전 모드 | EC2 Hibernate | 최대 절전 모드 | c06-eni-hibernate | 최대 절전 모드;Hibernate | compute
인스턴스를 멈출 때 메모리 내용을 암호화된 루트 EBS에 저장했다가, 다시 시작하면 그대로 이어 가는 기능입니다.

ebs | EBS | Amazon Elastic Block Store | Amazon EBS | c07-ebs | EBS | storage
EC2에 네트워크로 붙이는 블록 스토리지(가상 디스크)입니다. 한 AZ에 묶여 있고 인스턴스를 꺼도 데이터가 남습니다.

snapshot | EBS 스냅샷 | EBS snapshot | EBS 스냅샷 | c07-snapshot-ami | 스냅샷;Snapshot | storage
EBS 볼륨의 특정 시점 백업입니다. 증분으로 저장되고, 다른 AZ나 리전에서 새 볼륨을 만드는 데 씁니다.

instance-store | 인스턴스 스토어 | Instance store | 인스턴스 스토어 | c07-instance-store | 인스턴스 스토어;Instance Store | storage
호스트 서버에 직접 붙은 디스크입니다. 매우 빠르지만 인스턴스를 중지하거나 종료하면 데이터가 사라집니다.

iops | IOPS | Input/output operations per second | IOPS | c07-ebs-types | IOPS | storage
디스크가 1초에 처리하는 읽기·쓰기 횟수입니다. 작은 무작위 입출력이 많은 DB에서 중요합니다.

throughput | 처리량 | Throughput | 처리량 | c07-ebs-types | 처리량 | storage
1초에 옮기는 데이터 양(MiB/s)입니다. 큰 파일을 순서대로 읽는 로그·빅데이터 작업에서 중요합니다.

gp3 | gp3, gp2 | General Purpose SSD | 범용 SSD | c07-ebs-types | gp3;gp2 | storage
대부분의 작업에 쓰는 범용 SSD 볼륨입니다. gp3는 크기와 따로 IOPS와 처리량을 늘릴 수 있습니다.

io2 | io2 Block Express, io1 | Provisioned IOPS SSD | 프로비저닝된 IOPS SSD | c07-ebs-types | io2;io1;프로비저닝된 IOPS | storage
높은 IOPS를 보장해야 하는 DB용 SSD 볼륨입니다. 다중 연결(Multi-Attach)을 지원합니다.

st1 | st1, sc1 | Throughput Optimized HDD / Cold HDD | 처리량 최적화 HDD / 콜드 HDD | c07-ebs-types | st1;sc1 | storage
싸고 큰 HDD 볼륨입니다. st1은 자주 읽는 큰 순차 데이터, sc1은 거의 안 읽는 데이터용이고 둘 다 부팅 볼륨이 될 수 없습니다.

multi-attach | 다중 연결 | EBS Multi-Attach | 다중 연결 | c07-ebs | Multi-Attach;다중 연결 | storage
io1·io2 볼륨 하나를 같은 AZ의 인스턴스 최대 16대에 동시에 붙이는 기능입니다. 동시 쓰기를 다루는 클러스터 파일 시스템이 필요합니다.

efs | EFS | Amazon Elastic File System | Amazon EFS | c07-efs | EFS | storage
여러 AZ의 리눅스 인스턴스가 NFS로 동시에 마운트하는 관리형 파일 시스템입니다. 쓴 만큼 자동으로 늘고 줄어듭니다.

nfs | NFS | Network File System |  | c07-efs | NFS | storage
리눅스에서 네트워크 너머의 폴더를 내 폴더처럼 쓰는 프로토콜입니다. EFS가 이 방식을 씁니다.

smb | SMB | Server Message Block |  | c16-fsx | SMB | storage
윈도우 파일 공유 프로토콜입니다. FSx for Windows File Server가 이 방식을 씁니다.

elb | ELB | Elastic Load Balancing | Elastic Load Balancing | c08-elb | ELB;로드 밸런서;Elastic Load Balancing | compute
들어온 요청을 여러 대상(EC2, 컨테이너, IP, Lambda)에 나눠 보내고, 상태 확인으로 고장 난 대상을 빼는 관리형 서비스입니다.

alb | ALB | Application Load Balancer | Application Load Balancer | c08-alb | ALB;Application Load Balancer | compute
HTTP·HTTPS(7계층) 로드 밸런서입니다. 경로, 호스트, 헤더, 쿼리 문자열을 보고 대상 그룹을 골라 보냅니다.

nlb | NLB | Network Load Balancer | Network Load Balancer | c08-nlb-gwlb | NLB;Network Load Balancer | compute
TCP·UDP·TLS(4계층) 로드 밸런서입니다. 아주 낮은 지연으로 초당 수백만 요청을 처리하고, AZ마다 고정 IP(탄력적 IP 가능)를 가집니다.

gwlb | GWLB | Gateway Load Balancer | Gateway Load Balancer | c08-nlb-gwlb | GWLB;Gateway Load Balancer | net
방화벽, 침입 탐지 같은 가상 보안 장비 묶음 앞에 두고, 트래픽을 장비로 보냈다가 돌려받는 3계층 로드 밸런서입니다(GENEVE, 6081번 포트).

target-group | 대상 그룹 | Target group | 대상 그룹 | c08-alb | 대상 그룹;Target Group | compute
로드 밸런서가 요청을 보낼 대상(EC2, IP, Lambda, ALB)의 묶음입니다. 상태 확인도 대상 그룹 단위로 합니다.

health-check | 상태 확인 | Health check | 상태 확인 | c08-elb | 상태 확인;헬스 체크 | compute
대상에 주기적으로 요청을 보내 살아 있는지 확인하는 기능입니다. 실패한 대상에는 트래픽을 보내지 않습니다.

sticky | 고정 세션 | Sticky sessions | 고정 세션 | c08-elb-features | 고정 세션;Sticky Session | compute
같은 사용자의 요청을 쿠키로 같은 대상에 계속 보내는 기능입니다. 대상 사이 부하가 고르지 않을 수 있습니다.

cross-zone | 교차 영역 로드 밸런싱 | Cross-zone load balancing | 교차 영역 로드 밸런싱 | c08-elb-features | 교차 영역 로드 밸런싱 | compute
로드 밸런서 노드가 자기 AZ뿐 아니라 모든 AZ의 대상에 고르게 나눠 보내는 기능입니다. ALB는 기본으로 켜져 있고 NLB, GWLB는 꺼져 있습니다.

sni | SNI | Server Name Indication | 서버 이름 표시(SNI) | c08-elb-features | SNI | net
TLS 연결 첫머리에 접속할 도메인을 알려, 로드 밸런서 하나가 도메인마다 다른 인증서를 쓰게 하는 기능입니다(ALB, NLB, CloudFront 지원).

dereg-delay | 등록 취소 지연 | Deregistration delay (connection draining) | 등록 취소 지연 | c08-elb-features | 등록 취소 지연;연결 드레이닝;Connection Draining | compute
빠지는 대상에 새 요청은 보내지 않고, 처리 중인 요청이 끝날 때까지 기다리는 시간입니다(기본 300초, 0–3600초).

asg | Auto Scaling 그룹 | Amazon EC2 Auto Scaling group | Auto Scaling 그룹 | c08-asg | Auto Scaling 그룹;ASG | compute
최소, 최대, 원하는 개수 사이에서 EC2를 자동으로 늘리고 줄이며, 고장 난 인스턴스를 새것으로 바꾸는 기능입니다.

launch-template | 시작 템플릿 | Launch template | 시작 템플릿 | c08-asg | 시작 템플릿;Launch Template | compute
AMI, 인스턴스 유형, 보안 그룹, 사용자 데이터 같은 EC2 시작 설정을 저장한 틀입니다. ASG가 이 틀로 인스턴스를 만듭니다.

scaling-policy | 조정 정책 | Scaling policy | 조정 정책 | c08-scaling | 조정 정책;스케일링 정책;대상 추적 | compute
언제 몇 대를 늘리고 줄일지 정한 규칙입니다. 대상 추적, 단계·단순 조정, 예약, 예측 조정이 있습니다.

cooldown | 휴지 기간 | Cooldown period | 휴지 기간 | c08-scaling | 휴지 기간;쿨다운 | compute
조정 직후 지표가 안정될 때까지 다음 조정을 미루는 시간입니다(기본 300초).

rds | RDS | Amazon Relational Database Service | Amazon RDS | c09-rds | RDS | db
MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2를 관리형으로 운영하는 서비스입니다. 백업, 패치, 장애 조치를 AWS가 맡습니다.

read-replica | 읽기 전용 복제본 | Read replica | 읽기 전용 복제본 | c09-replica | 읽기 전용 복제본;Read Replica | db
원본 DB를 비동기로 복제한 읽기 전용 DB입니다. 읽기 부하를 나누고, 다른 리전에도 만들 수 있습니다.

multi-az | 다중 AZ 배포 | Multi-AZ deployment | 다중 AZ 배포 | c09-replica | 다중 AZ;Multi-AZ | db
다른 AZ에 대기 DB를 두고 동기식으로 복제해, 장애 때 자동으로 넘어가는 구성입니다. 대기 인스턴스 하나짜리 구성에서는 대기 DB를 읽기에 쓰지 않습니다.

failover | 장애 조치 | Failover | 장애 조치 | c09-replica | 장애 조치;페일오버 | db
주 시스템이 고장 나면 대기 시스템으로 자동 전환하는 것입니다.

sync-async | 동기·비동기 복제 | Synchronous / asynchronous replication |  | c09-replica | 동기식 복제;비동기 복제;동기식;비동기식 | db
동기는 복제본에 써질 때까지 기다려 손실이 없고, 비동기는 기다리지 않아 빠르지만 조금 늦게 따라옵니다(복제 지연).

aurora | Aurora | Amazon Aurora | Amazon Aurora | c09-aurora | Aurora | db
MySQL, PostgreSQL과 호환되는 AWS의 클라우드 DB입니다. 3개 AZ에 6벌 저장하고, 복제본은 최대 15개, 저장 공간은 자동으로 늘어납니다.

aurora-serverless | Aurora Serverless v2 | Amazon Aurora Serverless v2 | Aurora Serverless v2 | c09-aurora-adv | Aurora Serverless | db
부하에 따라 용량(ACU)을 자동으로 늘리고 줄이는 Aurora입니다. 쓰지 않을 때 0까지 줄이는 설정도 있습니다.

global-db | Aurora 글로벌 데이터베이스 | Amazon Aurora Global Database | Aurora Global Database | c09-aurora-adv | Global Database;글로벌 데이터베이스 | db
한 리전에서 쓰고 최대 10개 다른 리전으로 보통 1초 안에 복제하는 Aurora 구성입니다. 리전 장애 때 다른 리전을 승격합니다.

rds-proxy | RDS Proxy | Amazon RDS Proxy | Amazon RDS Proxy | c09-proxy | RDS Proxy | db
앱과 DB 사이에서 연결을 모아 재사용(풀링)하는 관리형 프록시입니다. Lambda처럼 연결을 많이 여는 경우와 장애 조치 시간을 줄일 때 씁니다.

elasticache | ElastiCache | Amazon ElastiCache | Amazon ElastiCache | c09-elasticache | ElastiCache | db
Valkey, Redis OSS, Memcached를 관리형으로 제공하는 인메모리 캐시입니다. 자주 읽는 데이터와 세션을 1밀리초 안팎으로 돌려줍니다.

cache | 캐시 | Cache | 캐시 | c09-elasticache | 캐시;캐싱 | db
자주 쓰는 데이터를 더 빠른 곳(메모리, 가까운 엣지)에 복사해 두고 꺼내 쓰는 것입니다.

lazy-loading | 지연 로딩 | Lazy loading (cache-aside) | 지연 로딩 | c09-elasticache | 지연 로딩;Lazy Loading | db
캐시에 없을 때만 DB에서 읽어 캐시에 넣는 전략입니다. 캐시에 오래된 값이 남을 수 있습니다.

write-through | 라이트 스루 | Write-through | 라이트 스루 | c09-elasticache | 라이트 스루;Write-through;Write Through | db
DB에 쓸 때 캐시에도 같이 쓰는 전략입니다. 캐시가 늘 최신이지만 읽지 않을 데이터도 캐시에 쌓입니다.

ttl | TTL | Time to live | TTL | c10-r53 | TTL | net
데이터를 얼마 동안 유효하게 둘지 정한 시간입니다. DNS 레코드, 캐시, DynamoDB 항목 만료에 쓰입니다.

dynamodb | DynamoDB | Amazon DynamoDB | Amazon DynamoDB | c19-dynamodb | DynamoDB | db
서버리스 키-값·문서형 NoSQL DB입니다. 규모와 상관없이 한 자릿수 밀리초로 응답하고, 온디맨드나 프로비저닝 용량으로 씁니다.

nosql | NoSQL | Non-relational database | 비관계형 데이터베이스 | c21-choose | NoSQL;비관계형 | db
조인 대신 키, 문서, 그래프처럼 접근 패턴에 맞춘 구조로 저장하는 DB입니다. 수평 확장이 쉽습니다.

rdbms | 관계형 데이터베이스 | Relational database | 관계형 데이터베이스 | c21-choose | 관계형 데이터베이스;관계형 DB | db
표(테이블)와 SQL로 데이터를 다루고 조인과 트랜잭션을 지원하는 DB입니다.

dax | DAX | DynamoDB Accelerator | DynamoDB Accelerator(DAX) | c19-dynamodb-adv | DAX | db
DynamoDB 앞에 두는 전용 인메모리 캐시입니다. 코드를 거의 바꾸지 않고 읽기 지연을 마이크로초 수준으로 줄입니다.

dynamodb-streams | DynamoDB Streams | DynamoDB Streams | DynamoDB Streams | c19-dynamodb-adv | DynamoDB Streams | db
테이블 항목의 생성, 수정, 삭제를 순서대로 24시간 보관하는 변경 흐름입니다. Lambda로 받아 후처리합니다.

global-tables | 글로벌 테이블 | DynamoDB global tables | 글로벌 테이블 | c19-dynamodb-adv | 글로벌 테이블;Global Tables | db
여러 리전에 같은 DynamoDB 테이블을 두고 서로 복제하는 기능입니다. 어느 리전에서나 읽고 쓸 수 있습니다(액티브-액티브).

vpc | VPC | Amazon Virtual Private Cloud | Amazon VPC | c27-vpc-subnet | VPC | net
AWS 안에 만드는 나만의 격리된 사설 네트워크입니다. 리전 하나에 걸치며, IP 범위(CIDR)와 서브넷을 정합니다.

subnet | 서브넷 | Subnet | 서브넷 | c27-vpc-subnet | 서브넷;Subnet | net
VPC를 나눈 IP 범위입니다. 한 AZ에만 속하고, 인터넷으로 가는 길이 있으면 퍼블릭, 없으면 프라이빗 서브넷입니다.

public-subnet | 퍼블릭 서브넷 | Public subnet | 퍼블릭 서브넷 | c27-igw | 퍼블릭 서브넷 | net
라우팅 테이블에 인터넷 게이트웨이로 가는 경로가 있는 서브넷입니다.

private-subnet | 프라이빗 서브넷 | Private subnet | 프라이빗 서브넷 | c27-igw | 프라이빗 서브넷 | net
인터넷 게이트웨이로 가는 경로가 없는 서브넷입니다. DB와 내부 서버를 둡니다.

cidr | CIDR | Classless Inter-Domain Routing | CIDR | c27-cidr | CIDR | net
`10.0.0.0/16`처럼 IP 주소 범위를 적는 방법입니다. 슬래시 뒤 숫자가 클수록 범위가 좁습니다(/16은 65,536개, /24는 256개).

igw | 인터넷 게이트웨이 | Internet gateway | 인터넷 게이트웨이 | c27-igw | 인터넷 게이트웨이;Internet Gateway;IGW | net
VPC와 인터넷을 잇는 관문입니다. VPC 하나에 하나만 붙고, 스스로 확장되는 관리형입니다.

route-table | 라우팅 테이블 | Route table | 라우팅 테이블 | c27-igw | 라우팅 테이블;Route Table | net
목적지 IP 범위별로 어느 관문으로 보낼지 적은 표입니다. 서브넷마다 하나가 연결됩니다.

nat-gw | NAT 게이트웨이 | NAT gateway | NAT 게이트웨이 | c27-nat | NAT 게이트웨이;NAT Gateway | net
프라이빗 서브넷의 인스턴스가 인터넷으로 나가게만 하는 관리형 장치입니다. 밖에서 먼저 들어오는 연결은 받지 않습니다.

nat-instance | NAT 인스턴스 | NAT instance | NAT 인스턴스 | c27-nat | NAT 인스턴스 | net
NAT 역할을 하는 EC2를 직접 운영하는 옛 방식입니다. 소스/대상 확인을 꺼야 하고 고가용성을 직접 만들어야 합니다.

bastion | 배스천 호스트 | Bastion host | 배스천 호스트 | c27-igw | 배스천 호스트;배스천 | net
퍼블릭 서브넷에 두고, 여기를 거쳐서만 프라이빗 인스턴스에 SSH로 들어가게 만든 관문 서버입니다.

nacl | 네트워크 ACL | Network ACL | 네트워크 ACL | c27-nacl | 네트워크 ACL;NACL | net
서브넷 경계에서 허용·거부 규칙을 번호 순서대로 검사하는 방화벽입니다. 상태를 기억하지 않아 응답 트래픽(임시 포트)도 따로 열어야 합니다.

ephemeral | 임시 포트 | Ephemeral ports | 임시 포트 | c27-nacl | 임시 포트 | net
클라이언트가 응답을 받으려고 잠시 여는 높은 번호 포트입니다(보통 1024–65535). NACL에서 응답 방향으로 열어 줘야 합니다.

peering | VPC 피어링 | VPC peering | VPC 피어링 | c27-peering | VPC 피어링;피어링 | net
두 VPC를 사설 IP로 직접 잇는 연결입니다. 이어진 연결을 거쳐 가지 못하고(비전이적), CIDR이 겹치면 만들 수 없습니다.

vpc-endpoint | VPC 엔드포인트 | VPC endpoint | VPC 엔드포인트 | c27-endpoints | VPC 엔드포인트;게이트웨이 엔드포인트;인터페이스 엔드포인트 | net
인터넷이나 NAT를 거치지 않고 VPC 안에서 AWS 서비스로 가는 통로입니다. 게이트웨이형(S3, DynamoDB, 무료)과 인터페이스형(ENI, 유료)이 있습니다.

privatelink | PrivateLink | AWS PrivateLink | AWS PrivateLink | c27-endpoints | PrivateLink | net
서비스를 다른 VPC에 인터페이스 엔드포인트로 사설 노출하는 기술입니다. 피어링 없이 서비스 하나만 열어 줄 수 있습니다.

flow-logs | VPC 흐름 로그 | VPC Flow Logs | VPC 흐름 로그 | c27-flowlogs | 흐름 로그;Flow Logs | net
ENI를 지나는 IP 트래픽의 출발지, 목적지, 포트, 허용·거부 결과를 기록하는 기능입니다. S3, CloudWatch Logs, Firehose로 보냅니다.

vpn | Site-to-Site VPN | AWS Site-to-Site VPN | AWS Site-to-Site VPN | c27-vpn | Site-to-Site VPN;VPN | net
회사 데이터 센터와 VPC를 인터넷 위의 암호화된 IPsec 터널 두 개로 잇는 연결입니다. 몇 분 만에 만들 수 있습니다.

vgw | 가상 프라이빗 게이트웨이 | Virtual private gateway | 가상 프라이빗 게이트웨이 | c27-vpn | 가상 프라이빗 게이트웨이;VGW | net
VPN과 Direct Connect가 VPC에 닿는 AWS 쪽 끝점입니다.

cgw | 고객 게이트웨이 | Customer gateway | 고객 게이트웨이 | c27-vpn | 고객 게이트웨이;CGW | net
VPN의 회사 쪽 장비(라우터, 방화벽)를 AWS에 등록한 정보입니다.

dx | Direct Connect | AWS Direct Connect | AWS Direct Connect | c27-dx | Direct Connect;DX | net
회사와 AWS를 인터넷이 아닌 전용 회선으로 잇는 서비스입니다. 대역폭이 일정하고 지연이 낮지만, 개통에 보통 한 달 이상 걸리고 기본으로 암호화되지 않습니다.

tgw | Transit Gateway | AWS Transit Gateway | AWS Transit Gateway | c27-tgw | Transit Gateway;TGW | net
많은 VPC와 VPN, Direct Connect를 허브 하나에 모아 잇는 라우터입니다. 피어링과 달리 전이적으로 라우팅합니다.

egress-igw | 송신 전용 인터넷 게이트웨이 | Egress-only internet gateway | 송신 전용 인터넷 게이트웨이 | c27-ipv6 | 송신 전용 인터넷 게이트웨이;Egress-only | net
IPv6 인스턴스가 인터넷으로 나가게만 하는 관문입니다. IPv6용 NAT 게이트웨이 역할을 합니다.

ipv6 | IPv6 | Internet Protocol version 6 | IPv6 | c27-ipv6 | IPv6 | net
주소가 매우 많은 새 인터넷 주소 체계입니다. VPC의 IPv6 주소는 모두 공인 주소입니다.

network-firewall | AWS Network Firewall | AWS Network Firewall | AWS Network Firewall | c27-firewall | Network Firewall | net
VPC 단위로 두는 관리형 방화벽입니다. 도메인 이름, 패턴(IDS/IPS) 규칙으로 들어오고 나가는 트래픽을 검사합니다.

route53 | Route 53 | Amazon Route 53 | Amazon Route 53 | c10-r53 | Route 53 | net
도메인 등록, DNS 응답, 상태 확인을 하는 AWS의 DNS 서비스입니다. 100% 가용성을 약정하는 유일한 AWS 서비스입니다.

dns | DNS | Domain Name System | DNS | c10-dns | DNS | net
`www.example.com` 같은 이름을 IP 주소로 바꿔 주는 인터넷의 전화번호부입니다.

hosted-zone | 호스팅 영역 | Hosted zone | 호스팅 영역 | c10-r53 | 호스팅 영역;Hosted Zone | net
한 도메인의 DNS 레코드를 담는 그릇입니다. 인터넷용 퍼블릭과 VPC 안에서만 쓰는 프라이빗이 있습니다.

alias | 별칭 레코드 | Alias record | 별칭 레코드 | c10-r53 | 별칭 레코드;Alias 레코드;Alias | net
도메인 이름을 ALB, CloudFront, S3 웹사이트 같은 AWS 리소스에 바로 잇는 Route 53 전용 레코드입니다. 루트 도메인에도 쓸 수 있고 조회 요금이 없습니다.

cname | CNAME | Canonical name record | CNAME | c10-r53 | CNAME | net
한 이름을 다른 이름으로 가리키는 DNS 레코드입니다. 루트 도메인(example.com)에는 쓸 수 없습니다.

routing-policy | 라우팅 정책 | Routing policy | 라우팅 정책 | c10-routing | 라우팅 정책 | net
Route 53이 DNS 질문에 어떤 답을 줄지 정하는 방식입니다(단순, 가중치, 지연 시간, 장애 조치, 지리적 위치, 지리 근접, IP 기반, 다중 값).

resolver | Route 53 Resolver | Amazon Route 53 Resolver | Route 53 Resolver | c10-resolver | Route 53 Resolver;인바운드 엔드포인트;아웃바운드 엔드포인트 | net
VPC의 기본 DNS 서버입니다. 인바운드·아웃바운드 엔드포인트로 회사 DNS와 질문을 주고받아 하이브리드 DNS를 만듭니다.

cloudfront | CloudFront | Amazon CloudFront | Amazon CloudFront | c15-cloudfront | CloudFront | net
전 세계 엣지 로케이션에 콘텐츠를 캐시해 빠르게 전달하는 CDN입니다. Shield와 WAF를 앞단에 붙일 수 있습니다.

cdn | CDN | Content delivery network | 콘텐츠 전송 네트워크 | c15-cloudfront | CDN | net
사용자 가까운 서버에 콘텐츠 복사본을 두고 대신 응답하는 네트워크입니다.

origin | 오리진 | Origin | 오리진 | c15-cloudfront | 오리진 | net
CloudFront가 캐시에 없을 때 원본을 가져오는 곳입니다(S3 버킷, ALB, EC2, 사용자 정의 HTTP 서버).

oac | OAC | Origin access control | 오리진 액세스 제어(OAC) | c15-cloudfront | OAC;OAI;오리진 액세스 제어 | net
S3 버킷을 CloudFront를 통해서만 읽게 잠그는 설정입니다. 예전 OAI를 대신합니다.

ga | Global Accelerator | AWS Global Accelerator | AWS Global Accelerator | c15-ga | Global Accelerator | net
고정 애니캐스트 IP 2개로 사용자를 가장 가까운 엣지로 받아, AWS 전용 네트워크로 가장 건강한 리전의 엔드포인트에 보내는 서비스입니다. TCP와 UDP 모두 됩니다.

anycast | 애니캐스트 IP | Anycast IP |  | c15-ga | 애니캐스트;Anycast | net
여러 장소가 같은 IP를 알려, 사용자가 가장 가까운 곳으로 연결되는 방식입니다.

s3 | S3 | Amazon Simple Storage Service | Amazon S3 | c12-s3 | S3 | storage
파일(객체)을 버킷에 저장하는 객체 스토리지입니다. 용량 제한이 없고 99.999999999%(11 nines) 내구성으로 설계됐습니다.

bucket | 버킷 | Bucket | 버킷 | c12-s3 | 버킷;Bucket | storage
S3 객체를 담는 최상위 그릇입니다. 범용 버킷 이름은 전 세계에서 하나뿐이어야 하고, 리전을 골라 만듭니다.

s3-object | 객체와 키 | Object, key | 객체, 키 | c12-s3 | 객체 키;S3 객체 | storage
S3에 저장한 파일 하나와 메타데이터입니다. 키(경로를 포함한 전체 이름)로 찾고, 하나에 최대 5TB입니다.

bucket-policy | 버킷 정책 | Bucket policy | 버킷 정책 | c12-policy | 버킷 정책;Bucket Policy | storage
버킷에 붙이는 리소스 기반 JSON 정책입니다. 다른 계정 허용, 공개 읽기, HTTPS 강제, 특정 VPC 엔드포인트만 허용 같은 규칙을 씁니다.

bpa | 퍼블릭 액세스 차단 | S3 Block Public Access | 퍼블릭 액세스 차단 | c12-policy | 퍼블릭 액세스 차단;Block Public Access | storage
정책이나 ACL이 실수로 버킷을 공개하지 못하게 막는 안전장치입니다. 새 버킷은 기본으로 켜져 있습니다.

versioning | 버전 관리 | S3 Versioning | 버전 관리 | c12-versioning-replication | 버전 관리;Versioning | storage
같은 키에 덮어쓰거나 지워도 이전 버전을 남기는 기능입니다. 지우면 삭제 마커가 생기고, 마커를 지우면 되살아납니다.

replication | S3 복제 | S3 Replication (CRR, SRR) | 복제 | c12-versioning-replication | CRR;SRR;교차 리전 복제;동일 리전 복제 | storage
버킷의 새 객체를 다른 버킷으로 비동기 복사하는 기능입니다. 다른 리전이면 CRR, 같은 리전이면 SRR이고, 양쪽 버킷에 버전 관리가 켜져 있어야 합니다.

storage-class | 스토리지 클래스 | S3 storage classes | 스토리지 클래스 | c12-classes | 스토리지 클래스;Storage Class | storage
접근 빈도와 꺼내는 속도에 따라 고르는 S3 요금 등급입니다(Standard, Standard-IA, One Zone-IA, Intelligent-Tiering, Glacier 세 종류 등).

glacier | S3 Glacier | Amazon S3 Glacier storage classes | S3 Glacier | c12-classes | Glacier;Deep Archive | storage
장기 보관용 저렴한 스토리지 클래스 묶음입니다. Instant Retrieval(밀리초), Flexible Retrieval(분~시간), Deep Archive(12–48시간)가 있습니다.

intelligent-tiering | S3 Intelligent-Tiering | S3 Intelligent-Tiering | S3 Intelligent-Tiering | c12-classes | Intelligent-Tiering | storage
접근 패턴을 보고 객체를 자동으로 싼 계층으로 옮기는 클래스입니다. 꺼내는 요금이 없고 객체당 소액 관리비가 붙습니다.

lifecycle | 수명 주기 규칙 | S3 Lifecycle configuration | 수명 주기 구성 | c13-lifecycle | 수명 주기;Lifecycle | storage
일정 기간이 지난 객체를 다른 클래스로 옮기거나(전환) 지우는(만료) 규칙입니다.

requester-pays | 요청자 지불 | Requester Pays | 요청자 지불 | c13-ops | 요청자 지불;Requester Pays | storage
다운로드 요청과 전송 비용을 버킷 주인 대신 내려받는 쪽 AWS 계정이 내게 하는 설정입니다.

event-notif | 이벤트 알림 | S3 Event Notifications | 이벤트 알림 | c13-events | 이벤트 알림;Event Notification | storage
객체 생성, 삭제 같은 일이 생기면 SNS, SQS, Lambda, EventBridge로 알리는 기능입니다.

multipart | 멀티파트 업로드 | Multipart upload | 멀티파트 업로드 | c13-performance | 멀티파트 업로드;Multipart | storage
큰 파일을 여러 조각으로 나눠 병렬로 올리는 방식입니다. 100MB 이상이면 권장하고, 5GB를 넘으면 반드시 써야 합니다.

transfer-accel | 전송 가속 | S3 Transfer Acceleration | Transfer Acceleration | c13-performance | 전송 가속;Transfer Acceleration | storage
먼 곳에서 올리는 파일을 가까운 엣지 로케이션에 먼저 보내고 AWS 내부망으로 버킷까지 옮겨 빠르게 하는 기능입니다.

presigned | 미리 서명된 URL | Presigned URL | 미리 서명된 URL | c14-cors-presigned | 미리 서명된 URL;Pre-signed URL;presigned URL | storage
만든 사람의 권한을 잠시 빌려, 정해진 시간 동안만 특정 객체를 올리거나 내려받게 하는 링크입니다.

cors | CORS | Cross-Origin Resource Sharing | CORS | c14-cors-presigned | CORS | storage
브라우저가 다른 출처(도메인)의 리소스를 불러오도록 허락하는 규칙입니다. 불려 가는 쪽 버킷에 설정합니다.

object-lock | 객체 잠금 | S3 Object Lock | 객체 잠금 | c14-lock | Object Lock;객체 잠금;WORM | storage
객체를 정해진 기간 동안 지우거나 덮어쓰지 못하게(WORM) 하는 기능입니다. 규정 준수 모드는 루트 사용자도 풀지 못합니다.

access-point | 액세스 포인트 | S3 Access Points | 액세스 포인트 | c14-access-points | 액세스 포인트;Access Point | storage
한 버킷에 팀이나 용도별 입구를 여러 개 만들고, 입구마다 정책을 따로 두는 기능입니다.

sse | 서버 측 암호화 | Server-side encryption | 서버 측 암호화 | c14-encryption | 서버 측 암호화;SSE-S3;SSE-KMS;SSE-C;DSSE-KMS | storage
S3가 저장할 때 암호화하고 읽을 때 풀어 주는 방식입니다. 키를 누가 관리하느냐에 따라 SSE-S3, SSE-KMS, DSSE-KMS, SSE-C로 나뉩니다.

mfa-delete | MFA Delete | S3 MFA Delete | MFA 삭제 | c14-mfa-logs | MFA Delete | storage
객체 버전을 영구 삭제하거나 버전 관리를 멈출 때 MFA 코드를 요구하는 설정입니다. 루트 사용자만 켤 수 있습니다.

snow | Snow Family | AWS Snow Family (Snowball Edge) | AWS Snow Family | c16-snow | Snowball Edge;Snowball;Snow Family | storage
데이터를 담아 택배로 보내는 물리 장비입니다. 지금은 신규 고객에게 제공되지 않고 기존 고객만 주문할 수 있습니다.

fsx | FSx | Amazon FSx | Amazon FSx | c16-fsx | FSx | storage
Windows File Server, Lustre, NetApp ONTAP, OpenZFS 같은 파일 시스템을 관리형으로 제공하는 서비스입니다.

lustre | FSx for Lustre | Amazon FSx for Lustre | Amazon FSx for Lustre | c16-fsx | Lustre | storage
HPC와 머신러닝용 초고속 병렬 파일 시스템입니다. S3 버킷과 연결해 데이터를 읽고 결과를 다시 쓸 수 있습니다.

sgw | Storage Gateway | AWS Storage Gateway | AWS Storage Gateway | c16-sgw | Storage Gateway;S3 File Gateway;Volume Gateway;Tape Gateway | storage
회사 서버가 쓰는 파일, 볼륨, 테이프 방식을 그대로 두고 뒤에서 S3와 Glacier에 저장하게 하는 하이브리드 스토리지입니다.

transfer-family | Transfer Family | AWS Transfer Family | AWS Transfer Family | c16-sgw | Transfer Family | storage
SFTP, FTPS, FTP, AS2로 S3나 EFS에 파일을 주고받는 관리형 서버입니다.

datasync | DataSync | AWS DataSync | AWS DataSync | c16-datasync | DataSync | storage
회사 NFS, SMB, HDFS나 다른 클라우드의 데이터를 S3, EFS, FSx로 예약 복사하는 온라인 전송 서비스입니다. 권한과 메타데이터를 보존합니다.

sqs | SQS | Amazon Simple Queue Service | Amazon SQS | c17-sqs | SQS | int
메시지를 대기열에 맡겨 두면 소비자가 가져가 처리하는 완전 관리형 대기열입니다. 생산자와 소비자를 떼어 놓습니다.

queue | 대기열 | Queue | 대기열 | c17-sqs | 대기열 | int
처리할 일을 쌓아 두는 곳입니다.

visibility | 가시성 제한 시간 | Visibility timeout | 가시성 제한 시간 | c17-sqs | 가시성 제한 시간;Visibility Timeout | int
소비자가 메시지를 가져가면 다른 소비자에게 잠시 숨기는 시간입니다(기본 30초). 그 안에 지우지 않으면 다시 보입니다.

long-polling | 긴 폴링 | Long polling | 긴 폴링 | c17-sqs | 긴 폴링;Long Polling | int
대기열이 비어 있으면 최대 20초까지 기다렸다가 응답하는 방식입니다. 빈 응답과 API 호출 비용을 줄입니다.

dlq | DLQ | Dead-letter queue | 배달 못한 편지 대기열 | c17-sqs | DLQ;배달 못한 편지 대기열 | int
여러 번 처리에 실패한 메시지를 따로 모아 두는 대기열입니다. 원인을 조사한 뒤 다시 보냅니다.

fifo | FIFO 대기열 | SQS FIFO queue | FIFO 대기열 | c17-fifo | FIFO | int
보낸 순서대로 정확히 한 번 처리하는 대기열입니다. 이름이 `.fifo`로 끝나고 메시지 그룹 ID 단위로 순서를 지킵니다.

sns | SNS | Amazon Simple Notification Service | Amazon SNS | c17-sns-fanout | SNS | int
주제(topic)에 메시지를 한 번 보내면 모든 구독자(SQS, Lambda, 이메일, HTTP, SMS)에게 밀어 주는 발행·구독 서비스입니다.

pubsub | 발행·구독 | Publish/subscribe | 게시/구독 | c17-sns-fanout | 발행·구독;pub/sub | int
보내는 쪽은 주제에 발행만 하고, 관심 있는 쪽이 구독해 받는 방식입니다.

fanout | 팬아웃 | Fan-out pattern | 팬아웃 | c17-sns-fanout | 팬아웃;Fan-out;Fan Out | int
SNS 주제 하나에 SQS 대기열 여러 개를 구독시켜, 메시지 하나를 여러 처리기로 동시에 보내는 패턴입니다.

kinesis | Kinesis Data Streams | Amazon Kinesis Data Streams | Amazon Kinesis Data Streams | c17-kinesis | Kinesis Data Streams;Kinesis | int
클릭, 로그, IoT 같은 실시간 데이터를 샤드에 순서대로 담아 여러 소비자가 다시 읽게 하는 스트리밍 서비스입니다(보관 최대 365일).

shard | 샤드 | Shard | 샤드 | c17-kinesis | 샤드;Shard | int
Kinesis 스트림의 처리 단위입니다. 샤드 하나가 초당 1MB(1,000건) 쓰기, 2MB 읽기를 맡습니다.

firehose | Data Firehose | Amazon Data Firehose | Amazon Data Firehose | c17-firehose | Data Firehose;Firehose | int
스트리밍 데이터를 받아 묶고 변환해 S3, Redshift, OpenSearch 등에 자동으로 싣는 서비스입니다. 코드 없이 쓰며, 버퍼 시간만큼 늦는 거의 실시간입니다.

mq | Amazon MQ | Amazon MQ | Amazon MQ | c17-compare-mq | Amazon MQ;ActiveMQ;RabbitMQ | int
ActiveMQ와 RabbitMQ를 관리형으로 제공합니다. MQTT, AMQP, STOMP 같은 표준 프로토콜을 쓰던 앱을 코드 변경 없이 옮길 때 씁니다.

eventbridge | EventBridge | Amazon EventBridge | Amazon EventBridge | c24-eventbridge | EventBridge | int
AWS 서비스, SaaS, 내 앱의 이벤트를 규칙에 맞춰 대상(Lambda, SQS, Step Functions 등)으로 보내는 서버리스 이벤트 버스입니다. 일정 실행도 합니다.

stepfunctions | Step Functions | AWS Step Functions | AWS Step Functions | c19-stepfunctions | Step Functions | int
여러 단계(Lambda, ECS 작업, 사람 승인 등)를 순서, 분기, 재시도, 병렬로 묶어 워크플로로 실행하는 서비스입니다.

appflow | AppFlow | Amazon AppFlow | Amazon AppFlow | c30-misc | AppFlow | int
Salesforce, SAP, Slack 같은 SaaS 앱과 S3, Redshift 사이의 데이터를 코드 없이 주고받는 통합 서비스입니다.

serverless | 서버리스 | Serverless | 서버리스 | c19-lambda | 서버리스 | serverless
서버를 만들거나 관리하지 않고 코드나 설정만 올리면 AWS가 실행하고 확장하는 방식입니다. 쓴 만큼만 냅니다.

lambda | Lambda | AWS Lambda | AWS Lambda | c19-lambda | Lambda | serverless
이벤트가 오면 함수 코드를 실행하고 실행 시간만큼 내는 서버리스 컴퓨팅입니다. 한 번 실행은 최대 15분입니다.

concurrency | 동시성 | Lambda concurrency | 동시성 | c19-concurrency | 동시성;예약된 동시성;프로비저닝된 동시성 | serverless
같은 순간에 실행 중인 Lambda 실행 환경 수입니다. 계정 기본 한도는 리전당 1,000이고, 예약 동시성으로 나누거나 프로비저닝된 동시성으로 미리 데워 둡니다.

cold-start | 콜드 스타트 | Cold start | 콜드 스타트 | c19-concurrency | 콜드 스타트;Cold Start | serverless
새 실행 환경을 만들고 코드를 처음 불러오느라 첫 요청이 느려지는 현상입니다. 프로비저닝된 동시성이나 SnapStart로 줄입니다.

lambda-edge | Lambda@Edge, CloudFront Functions | Lambda@Edge / CloudFront Functions | Lambda@Edge | c19-edge | Lambda@Edge;CloudFront Functions | serverless
CloudFront 엣지에서 요청과 응답을 고치는 함수입니다. 가벼운 헤더·URL 처리는 더 싸고 빠른 CloudFront Functions를 씁니다.

apigw | API Gateway | Amazon API Gateway | Amazon API Gateway | c19-apigw | API Gateway | serverless
REST, HTTP, WebSocket API를 만들고 인증, 사용량 제한, 캐시, 버전 관리를 맡는 관리형 API 관문입니다.

throttling | 스로틀링 | Throttling | 제한 | c19-apigw | 스로틀링;Throttling | serverless
초당 요청 수가 한도를 넘으면 거절(HTTP 429)해 뒤쪽 시스템을 보호하는 것입니다.

container | 컨테이너 | Container | 컨테이너 | c18-docker-ecr | 컨테이너 | serverless
앱과 실행에 필요한 라이브러리를 한 묶음으로 담아 어디서나 똑같이 실행되게 한 것입니다. 이미지를 실행하면 컨테이너가 됩니다.

docker | Docker | Docker |  | c18-docker-ecr | Docker;도커 | serverless
컨테이너를 만들고 실행하는 대표 도구입니다. Dockerfile로 이미지를 만들고 레지스트리에 올립니다.

ecs | ECS | Amazon Elastic Container Service | Amazon ECS | c18-ecs | ECS | serverless
AWS의 컨테이너 오케스트레이션 서비스입니다. 작업 정의대로 컨테이너(작업)를 EC2나 Fargate에서 실행하고 로드 밸런서에 붙입니다.

fargate | Fargate | AWS Fargate | AWS Fargate | c18-ecs | Fargate | serverless
서버 없이 컨테이너를 실행하는 서버리스 실행 방식입니다. ECS와 EKS에서 쓰고 CPU와 메모리만 정하면 됩니다.

task-role | 작업 역할 | ECS task role / task execution role | 태스크 IAM 역할 | c18-ecs | 작업 역할;작업 실행 역할 | serverless
작업 역할은 컨테이너 안의 앱이 AWS를 부를 때 쓰는 권한이고, 작업 실행 역할은 ECS가 이미지를 받고 로그를 보내는 데 쓰는 권한입니다.

ecr | ECR | Amazon Elastic Container Registry | Amazon ECR | c18-docker-ecr | ECR | serverless
컨테이너 이미지를 저장하는 AWS의 레지스트리입니다. 이미지는 S3에 저장되고 IAM으로 접근을 통제합니다.

eks | EKS | Amazon Elastic Kubernetes Service | Amazon EKS | c18-eks | EKS;쿠버네티스;Kubernetes | serverless
관리형 쿠버네티스입니다. 이미 쿠버네티스를 쓰거나 여러 클라우드에서 같은 도구를 써야 할 때 고릅니다.

beanstalk | Elastic Beanstalk | AWS Elastic Beanstalk | AWS Elastic Beanstalk | c11-beanstalk | Elastic Beanstalk;Beanstalk | compute
코드만 올리면 EC2, ASG, ELB, 모니터링을 알아서 꾸려 주는 PaaS입니다. 웹 서버 환경과 작업자(worker) 환경이 있습니다.

batch | AWS Batch | AWS Batch | AWS Batch | c30-outposts-batch | AWS Batch | compute
대량의 일괄 작업을 대기열에 넣으면 EC2, 스팟, Fargate를 자동으로 띄워 처리하는 서비스입니다. 15분을 넘는 작업에 Lambda 대신 씁니다.

outposts | Outposts | AWS Outposts | AWS Outposts | c30-outposts-batch | Outposts | compute
AWS가 랙이나 서버를 고객 데이터 센터에 설치해, 같은 API로 온프레미스에서 EC2, EBS 등을 쓰게 하는 서비스입니다.

amplify | Amplify | AWS Amplify | AWS Amplify | c30-misc | Amplify | serverless
웹·모바일 앱의 호스팅, 인증, API, 저장소를 한 번에 꾸려 주는 프런트엔드 개발 도구입니다.

athena | Athena | Amazon Athena | Amazon Athena | c22-athena | Athena | data
S3에 있는 파일(CSV, JSON, Parquet 등)을 서버 없이 SQL로 바로 조회하는 서비스입니다. 스캔한 데이터 양만큼 냅니다.

parquet | Parquet | Apache Parquet (columnar format) |  | c22-athena | Parquet;ORC;열 형식 | data
열 단위로 압축해 저장하는 파일 형식입니다. 필요한 열만 읽어 Athena와 Redshift의 비용과 시간을 줄입니다.

redshift | Redshift | Amazon Redshift | Amazon Redshift | c22-redshift | Redshift | data
큰 정형 데이터를 열 기반으로 빠르게 분석하는 데이터 웨어하우스입니다(OLAP). Spectrum으로 S3 데이터도 함께 조회합니다.

olap | OLTP와 OLAP | Online transaction / analytical processing |  | c21-choose | OLTP;OLAP | data
OLTP는 주문, 결제처럼 짧은 읽기·쓰기를 많이 처리하는 업무용 DB(RDS)이고, OLAP는 쌓인 데이터를 모아 분석하는 용도(Redshift)입니다.

opensearch | OpenSearch | Amazon OpenSearch Service | Amazon OpenSearch Service | c22-opensearch | OpenSearch;Elasticsearch | data
부분 일치 검색과 로그 분석·시각화를 하는 관리형 검색 엔진입니다. Elasticsearch에서 갈라져 나왔습니다.

emr | EMR | Amazon EMR | Amazon EMR | c22-emr | EMR;Hadoop;Spark | data
Hadoop, Spark 같은 빅데이터 프레임워크를 EC2 클러스터(또는 서버리스)로 띄워 대량 데이터를 처리하는 서비스입니다.

glue | Glue | AWS Glue | AWS Glue | c22-glue-lake | Glue;크롤러;데이터 카탈로그 | data
서버리스 ETL 서비스입니다. 크롤러가 데이터 구조를 찾아 데이터 카탈로그에 등록하고, 작업이 형식을 바꿉니다(예: CSV를 Parquet으로).

etl | ETL | Extract, transform, load | ETL | c22-glue-lake | ETL | data
데이터를 꺼내고(Extract) 모양을 바꾸어(Transform) 분석 저장소에 싣는(Load) 과정입니다.

lake-formation | Lake Formation | AWS Lake Formation | AWS Lake Formation | c22-glue-lake | Lake Formation | data
S3 데이터 레이크를 빠르게 만들고, 테이블·열·행 단위 권한을 한곳에서 관리하는 서비스입니다.

datalake | 데이터 레이크 | Data lake | 데이터 레이크 | c22-glue-lake | 데이터 레이크;Data Lake | data
정형·비정형 데이터를 원래 형식 그대로 S3 같은 곳에 모아 두고 여러 분석 도구로 꺼내 쓰는 저장소입니다.

quick | Amazon Quick Sight | Amazon Quick Sight (formerly Amazon QuickSight) | Amazon Quick Sight | c22-quick | QuickSight;Quick Sight;Amazon Quick | data
데이터를 대시보드와 차트로 보여 주는 서버리스 BI 도구입니다. 2025년 10월 Amazon Quick Suite로 바뀌며 이름이 Quick Sight가 됐습니다.

flink | Managed Service for Apache Flink | Amazon Managed Service for Apache Flink | Amazon Managed Service for Apache Flink | c22-streaming | Apache Flink;Flink | data
스트리밍 데이터를 실시간으로 집계·분석하는 Flink 애플리케이션을 관리형으로 실행합니다. 옛 이름은 Kinesis Data Analytics입니다.

msk | MSK | Amazon Managed Streaming for Apache Kafka | Amazon MSK | c22-streaming | MSK;Kafka | data
Apache Kafka 클러스터를 관리형(또는 서버리스)으로 제공하는 서비스입니다. Kafka를 그대로 쓰고 싶을 때 고릅니다.

documentdb | DocumentDB | Amazon DocumentDB (with MongoDB compatibility) | Amazon DocumentDB | c21-others | DocumentDB;MongoDB | db
MongoDB와 호환되는 관리형 문서 DB입니다(JSON 문서 저장).

neptune | Neptune | Amazon Neptune | Amazon Neptune | c21-others | Neptune;그래프 데이터베이스 | db
소셜 관계, 추천, 사기 탐지처럼 관계가 많은 데이터를 다루는 관리형 그래프 DB입니다.

keyspaces | Keyspaces | Amazon Keyspaces (for Apache Cassandra) | Amazon Keyspaces | c21-others | Keyspaces;Cassandra | db
Apache Cassandra와 호환되는 서버리스 와이드 컬럼 DB입니다(CQL 사용).

timestream | Timestream | Amazon Timestream | Amazon Timestream | c21-others | Timestream;시계열 | db
시간 순서로 쌓이는 측정값(IoT, 지표)을 저장·분석하는 시계열 DB입니다. LiveAnalytics는 2025-06부터 신규 고객을 받지 않고 InfluxDB 버전을 권합니다.

rekognition | Rekognition | Amazon Rekognition | Amazon Rekognition | c23-ai-media | Rekognition | data
이미지와 영상에서 사물, 얼굴, 글자, 부적절한 콘텐츠를 찾아내는 서비스입니다.

transcribe | Transcribe | Amazon Transcribe | Amazon Transcribe | c23-ai-media | Transcribe | data
음성을 텍스트로 바꾸는 서비스입니다. 개인 정보를 자동으로 가릴 수 있습니다.

polly | Polly | Amazon Polly | Amazon Polly | c23-ai-media | Polly | data
텍스트를 사람 목소리로 읽어 주는 서비스입니다(TTS).

translate | Translate | Amazon Translate | Amazon Translate | c23-ai-media | Amazon Translate | data
텍스트를 다른 언어로 번역하는 서비스입니다.

lex | Lex, Connect | Amazon Lex / Amazon Connect | Amazon Lex | c23-ai-media | Lex;Amazon Connect | data
Lex는 음성·텍스트 챗봇을 만드는 서비스이고, Connect는 클라우드 콜센터입니다. 둘을 함께 써서 전화 상담을 자동화합니다.

comprehend | Comprehend | Amazon Comprehend | Amazon Comprehend | c23-ai-text | Comprehend;Comprehend Medical | data
텍스트에서 감정, 핵심어, 개체, 언어를 찾아내는 자연어 처리 서비스입니다. Comprehend Medical은 의료 정보를 뽑습니다.

textract | Textract | Amazon Textract | Amazon Textract | c23-ai-text | Textract | data
스캔한 문서와 양식에서 글자, 표, 양식 항목을 뽑아내는 서비스입니다.

kendra | Kendra | Amazon Kendra | Amazon Kendra | c23-ai-text | Kendra | data
회사 문서에서 자연어 질문에 맞는 답을 찾아 주는 지능형 검색 서비스입니다.

sagemaker | SageMaker AI | Amazon SageMaker AI | Amazon SageMaker AI | c23-ai-text | SageMaker | data
머신러닝 모델을 만들고 학습시키고 배포하는 완전 관리형 플랫폼입니다(2024-12에 이름이 SageMaker AI로 바뀜).

personalize | Personalize | Amazon Personalize | Amazon Personalize | c23-ai-text | Personalize | data
사용자별 실시간 추천을 만들어 주는 서비스입니다. SAA-C03 공식 범위 밖 목록에 있습니다.

cloudwatch | CloudWatch | Amazon CloudWatch | Amazon CloudWatch | c24-metrics | CloudWatch | ops
AWS 자원과 앱의 지표, 로그, 경보, 대시보드를 모으는 모니터링 서비스입니다.

metric | 지표 | CloudWatch metric | 지표 | c24-metrics | 지표;메트릭 | ops
CPU 사용률처럼 시간에 따라 기록되는 숫자 값입니다. 네임스페이스와 차원(dimension)으로 구분합니다.

alarm | CloudWatch 경보 | Amazon CloudWatch alarm | 경보 | c24-alarms | CloudWatch 경보;경보 | ops
지표가 기준을 넘으면 상태를 바꾸고 SNS 알림, Auto Scaling, EC2 복구 같은 동작을 하는 규칙입니다.

logs | CloudWatch Logs | Amazon CloudWatch Logs | CloudWatch Logs | c24-logs | CloudWatch Logs;로그 그룹;Logs Insights | ops
앱과 AWS 서비스의 로그를 모아 보관, 검색, 분석하는 서비스입니다. 구독 필터로 다른 서비스에 실시간으로 넘깁니다.

cw-agent | CloudWatch 에이전트 | CloudWatch agent | CloudWatch 에이전트 | c24-metrics | CloudWatch 에이전트;통합 에이전트 | ops
EC2나 온프레미스 서버에 설치해 메모리, 디스크 같은 OS 지표와 로그 파일을 CloudWatch로 보내는 프로그램입니다. 기본 EC2 지표에는 메모리가 없습니다.

xray | X-Ray | AWS X-Ray | AWS X-Ray | c20-micro | X-Ray | ops
요청이 여러 서비스를 거치는 경로와 구간별 지연·오류를 추적해 보여 주는 분산 추적 서비스입니다.

cloudtrail | CloudTrail | AWS CloudTrail | AWS CloudTrail | c24-cloudtrail | CloudTrail | ops
계정에서 일어난 API 호출(누가, 언제, 어디서, 무엇을)을 기록하는 감사 서비스입니다. 이벤트 기록은 기본 90일 동안 볼 수 있습니다.

config | AWS Config | AWS Config | AWS Config | c24-config | AWS Config;Config 규칙 | ops
리소스 설정과 그 변경 이력을 기록하고, 규칙에 맞는지 계속 평가하는 서비스입니다.

cfn | CloudFormation | AWS CloudFormation | AWS CloudFormation | c30-cfn | CloudFormation | ops
YAML이나 JSON 템플릿에 인프라를 적어 스택으로 한꺼번에 만들고 바꾸고 지우는 IaC 서비스입니다.

iac | IaC | Infrastructure as Code | 코드형 인프라 | c30-cfn | IaC;코드형 인프라 | ops
서버와 네트워크를 코드로 적어 버전 관리하고 같은 환경을 반복해서 만드는 방식입니다.

ssm | Systems Manager | AWS Systems Manager | AWS Systems Manager | c30-ssm | Systems Manager;SSM | ops
많은 서버를 한꺼번에 관리하는 도구 모음입니다(명령 실행, 패치, Session Manager, Parameter Store, Automation).

param-store | Parameter Store | AWS Systems Manager Parameter Store | Parameter Store | c26-secrets | Parameter Store | iam
설정값과 비밀번호를 계층형 이름으로 저장하는 서비스입니다. KMS로 암호화한 SecureString을 쓸 수 있고 표준 등급은 무료입니다.

secrets-manager | Secrets Manager | AWS Secrets Manager | AWS Secrets Manager | c26-secrets | Secrets Manager | iam
DB 비밀번호 같은 비밀을 저장하고 자동으로 교체(로테이션)하는 서비스입니다. RDS, Aurora와 바로 연동되고 다른 리전에 복제할 수 있습니다.

cost-explorer | Cost Explorer | AWS Cost Explorer | AWS Cost Explorer | c30-cost | Cost Explorer | ops
과거 비용을 그래프로 나눠 보고 앞으로 12개월을 예측하며, Savings Plans와 예약 인스턴스 추천을 주는 도구입니다.

budgets | AWS Budgets | AWS Budgets | AWS Budgets | c30-cost | AWS Budgets;Budgets | ops
비용, 사용량, 예약 인스턴스나 Savings Plans 사용률이 정한 기준을 넘거나 넘을 것으로 예상되면 알리고, 정해 둔 조치를 실행합니다.

cur | Cost and Usage Report | AWS Cost and Usage Report (CUR) | AWS 비용 및 사용 보고서 | c30-cost | Cost and Usage Report;CUR | ops
가장 자세한 비용·사용량 데이터를 S3로 내보내는 보고서입니다(지금은 Data Exports의 CUR 2.0). Athena나 Quick Sight로 분석합니다.

anomaly | Cost Anomaly Detection | AWS Cost Anomaly Detection | AWS 비용 이상 탐지 | c30-cost | Cost Anomaly Detection;비용 이상 탐지 | ops
머신러닝으로 평소와 다른 비용 증가를 찾아 알려 주는 기능입니다.

cost-tags | 비용 할당 태그 | Cost allocation tags | 비용 할당 태그 | c30-cost | 비용 할당 태그 | ops
리소스에 붙인 태그(예: `project=shop`)로 비용을 나눠 보는 기능입니다. 결제 콘솔에서 활성화해야 보고서에 나타납니다.

compute-optimizer | Compute Optimizer | AWS Compute Optimizer | AWS Compute Optimizer | c30-cost | Compute Optimizer | ops
사용 기록을 분석해 EC2, EBS, Lambda, ECS의 크기를 줄이거나 바꾸라고 권하는 서비스입니다.

trusted-advisor | Trusted Advisor | AWS Trusted Advisor | AWS Trusted Advisor | c31-wa | Trusted Advisor | ops
계정을 점검해 비용, 성능, 보안, 내결함성, 서비스 한도, 운영 우수성 항목을 권고합니다. 전체 점검은 Business 지원 이상에서 열립니다.

well-architected | Well-Architected 프레임워크 | AWS Well-Architected Framework | AWS Well-Architected 프레임워크 | c31-wa | Well-Architected | ops
운영 우수성, 보안, 안정성, 성능 효율성, 비용 최적화, 지속 가능성 6개 기둥으로 아키텍처를 점검하는 모범 사례 모음입니다.

enc-rest | 저장 시·전송 중 암호화 | Encryption at rest / in transit | 저장 데이터 암호화 / 전송 중 데이터 암호화 | c26-enc101 | 저장 시 암호화;전송 중 암호화 | iam
저장 시 암호화는 디스크나 S3에 쓸 때 암호화하는 것이고, 전송 중 암호화는 네트워크로 오갈 때 TLS(HTTPS)로 감싸는 것입니다.

tls | TLS | Transport Layer Security | TLS | c26-enc101 | TLS;HTTPS | iam
네트워크로 오가는 데이터를 암호화하는 표준입니다(HTTPS의 S). 인증서로 서버가 진짜인지도 확인합니다.

kms | KMS | AWS Key Management Service | AWS KMS | c26-kms | KMS | iam
암호화 키를 만들고 보관하며, 누가 키를 쓸 수 있는지 키 정책과 IAM으로 통제하는 관리형 서비스입니다. 키 사용은 모두 CloudTrail에 남습니다.

cmk | 고객 관리형 키 | Customer managed key | 고객 관리형 키 | c26-kms | 고객 관리형 키;AWS 관리형 키 | iam
내가 만들고 키 정책과 교체 주기를 정하는 KMS 키입니다. AWS 관리형 키(`aws/s3` 등)는 서비스가 대신 만들고 해마다 자동 교체합니다.

key-policy | 키 정책 | Key policy | 키 정책 | c26-kms | 키 정책;Key Policy | iam
KMS 키에 붙는 리소스 기반 정책입니다. 키 정책이 허락하지 않으면 IAM 정책만으로는 키를 쓸 수 없습니다.

envelope | 봉투 암호화 | Envelope encryption | 봉투 암호화 | c26-kms | 봉투 암호화;데이터 키 | iam
데이터를 데이터 키로 암호화하고, 그 데이터 키를 다시 KMS 키로 암호화해 함께 보관하는 방식입니다. KMS가 직접 암호화하는 4KB보다 큰 데이터에 씁니다.

mrk | 다중 리전 키 | KMS multi-Region keys | 다중 리전 키 | c26-kms-mr | 다중 리전 키 | iam
여러 리전에 같은 키 ID와 키 재료를 가진 복제본을 두는 KMS 키입니다. 한 리전에서 암호화한 데이터를 다른 리전에서 바로 풉니다.

acm | ACM | AWS Certificate Manager | AWS Certificate Manager(ACM) | c26-acm-hsm | ACM;Certificate Manager | iam
TLS 인증서를 발급하고 자동 갱신해 ELB, CloudFront, API Gateway에 붙이는 서비스입니다. 이 서비스들에 붙이는 공인 인증서는 무료입니다.

cloudhsm | CloudHSM | AWS CloudHSM | AWS CloudHSM | c26-acm-hsm | CloudHSM;HSM | iam
나만 쓰는 하드웨어 보안 모듈(HSM)을 빌리는 서비스입니다. 키를 고객이 단독으로 관리합니다.

waf | WAF | AWS WAF | AWS WAF | c26-waf | WAF;웹 ACL | iam
7계층(HTTP) 웹 방화벽입니다. SQL 주입, XSS, 특정 IP·국가, 요청 비율 규칙으로 ALB, API Gateway, CloudFront 등의 앞에서 요청을 거릅니다.

shield | Shield | AWS Shield | AWS Shield | c26-shield | Shield;Shield Advanced | iam
DDoS 공격을 막는 서비스입니다. Standard는 모든 고객에게 무료로 켜져 있고, Advanced는 유료로 대응팀과 비용 보호를 줍니다.

ddos | DDoS | Distributed denial of service | 분산 서비스 거부(DDoS) | c26-shield | DDoS | iam
여러 곳에서 한꺼번에 트래픽을 쏟아 서비스를 멈추게 하는 공격입니다.

sqli | SQL 주입, XSS | SQL injection / Cross-site scripting | SQL 주입 | c26-waf | SQL 주입;SQL injection;XSS | iam
SQL 주입은 입력값에 SQL 조각을 넣어 DB를 조작하는 공격이고, XSS는 남의 페이지에 악성 스크립트를 심는 공격입니다. WAF 규칙으로 막습니다.

firewall-manager | Firewall Manager | AWS Firewall Manager | AWS Firewall Manager | c26-shield | Firewall Manager | iam
Organizations의 모든 계정에 WAF 규칙, Shield Advanced, 보안 그룹, Network Firewall 정책을 한꺼번에 적용하는 서비스입니다.

guardduty | GuardDuty | Amazon GuardDuty | Amazon GuardDuty | c26-detect | GuardDuty | iam
CloudTrail, VPC 흐름 로그, DNS 로그 등을 머신러닝으로 분석해 위협(암호화폐 채굴, 이상 접속 등)을 찾아내는 서비스입니다.

inspector | Inspector | Amazon Inspector | Amazon Inspector | c26-detect | Inspector | iam
EC2, ECR 컨테이너 이미지, Lambda 함수의 소프트웨어 취약점(CVE)과 의도치 않은 네트워크 노출을 계속 스캔하는 서비스입니다.

macie | Macie | Amazon Macie | Amazon Macie | c26-detect | Macie | iam
S3 버킷에서 개인 정보(PII) 같은 민감한 데이터를 머신러닝으로 찾아 알려 주는 서비스입니다.

security-hub | Security Hub | AWS Security Hub | AWS Security Hub | c26-detect | Security Hub | iam
여러 보안 서비스의 결과를 한곳에 모으고 보안 표준 점검을 하는 서비스입니다.

detective | Detective | Amazon Detective | Amazon Detective | c26-detect | Amazon Detective | iam
보안 결과의 원인을 로그 그래프로 거슬러 조사하도록 돕는 서비스입니다.

dr-strategy | 재해 복구 전략 | Backup & restore / Pilot light / Warm standby / Multi-site |  | c28-dr | 파일럿 라이트;웜 스탠바이;Pilot Light;Warm Standby;액티브-액티브 | dr
재해 복구 전략 네 가지(백업 및 복원, 파일럿 라이트, 웜 스탠바이, 다중 사이트 액티브-액티브)입니다. 뒤로 갈수록 RPO와 RTO가 짧아지고 비용이 커집니다.

rpo | RPO | Recovery point objective | 복구 시점 목표(RPO) | c28-dr | RPO;복구 시점 목표 | dr
장애가 났을 때 잃어도 되는 데이터의 최대 시간 범위입니다. RPO 1시간은 최대 1시간 치 데이터 손실을 허용한다는 뜻입니다.

rto | RTO | Recovery time objective | 복구 시간 목표(RTO) | c28-dr | RTO;복구 시간 목표 | dr
장애가 난 뒤 서비스를 다시 살리기까지 허용하는 최대 시간입니다.

drs | Elastic Disaster Recovery | AWS Elastic Disaster Recovery | AWS Elastic Disaster Recovery | c28-drs | Elastic Disaster Recovery;DRS | dr
온프레미스나 다른 클라우드의 서버를 블록 단위로 계속 AWS에 복제해 두었다가, 재해 때 몇 분 안에 EC2로 띄우는 서비스입니다.

dms | DMS | AWS Database Migration Service | AWS DMS | c28-dms | DMS;Database Migration Service | dr
원본 DB를 계속 쓰는 동안 데이터를 다른 DB로 옮기고, 이후 바뀐 내용(CDC)까지 따라잡게 하는 서비스입니다.

sct | SCT | AWS Schema Conversion Tool | AWS SCT | c28-dms | SCT;Schema Conversion | dr
Oracle에서 PostgreSQL처럼 엔진이 다른 이전에서 스키마와 코드를 변환하는 도구입니다. 같은 엔진이면 필요 없습니다.

cdc | CDC | Change data capture | 변경 데이터 캡처 | c28-dms | CDC;변경 데이터 캡처 | dr
처음 전체를 복사한 뒤, 원본에서 바뀌는 내용만 계속 따라 옮기는 방식입니다.

mgn | Application Migration Service | AWS Application Migration Service (MGN) | AWS Application Migration Service | c28-onprem | Application Migration Service;MGN | dr
서버를 그대로 들어 옮기는(rehost, lift-and-shift) 주력 서비스입니다. 원본 서버를 계속 복제하다가 전환(cutover)합니다.

backup | AWS Backup | AWS Backup | AWS Backup | c28-backup | AWS Backup;백업 계획;백업 볼트 | dr
EC2, EBS, RDS, DynamoDB, EFS, FSx, S3 등의 백업을 계획(빈도, 보관 기간)으로 한곳에서 관리하고 다른 리전·계정으로 복사하는 서비스입니다.

vault-lock | 볼트 잠금 | Vault Lock | 볼트 잠금 | c28-backup | Vault Lock;볼트 잠금 | dr
백업이나 보관 데이터를 정해진 기간 동안 아무도 지우지 못하게 잠그는 기능입니다(WORM).

vmware | VMware Cloud on AWS | VMware Cloud on AWS | VMware Cloud on AWS | c28-onprem | VMware Cloud on AWS;VMware | dr
회사의 VMware vSphere 환경을 AWS 베어메탈 서버에서 그대로 운영하는 서비스입니다.

distractor | 오답 보기 | Distractor |  | x-howto | 오답 보기 | exam
지식이 덜 갖춰진 사람이 고를 만하게 만든 그럴듯한 틀린 보기입니다.

unscored | 비채점 문항 | Unscored content |  | start-exam | 비채점 문항 | exam
점수에 들어가지 않는 15문항입니다. 어느 문항인지 표시되지 않으므로 모든 문항을 똑같이 풉니다.
"""

ENTRIES = []
for block in [b.strip() for b in RAW.strip().split('\n\n') if b.strip()]:
    head, _, d = block.partition('\n')
    f = [x.strip() for x in head.split('|')]
    if len(f) != 7:
        raise ValueError('bad glossary line: ' + head)
    ENTRIES.append(dict(id=f[0], label=f[1], en=f[2], ko=f[3], topic=f[4],
                        forms=[x.strip() for x in f[5].split(';') if x.strip()], cat=f[6], def_=d.strip(), **{'def': d.strip()}))
BY_ID = {e['id']: e for e in ENTRIES}
if len(BY_ID) != len(ENTRIES):
    raise ValueError('duplicate glossary id')

# very common terms: marked once per part instead of once per topic
CORE = {'region', 'az', 'ec2', 's3', 'iam', 'vpc', 'instance', 'cloudwatch', 'lambda', 'cache', 'container', 'rds', 'serverless'}
# reference topics: no popovers
NO_MARK = {'ap-glossary', 'x-numbers', 'x-compare', 'ap-analogy-map'}
# topics that need no diagram
NO_FIG = {'start-plan', 'ap-glossary', 'ap-changes'}


def render_table(numfn):
    out = []
    for cat, cname in CATEGORIES:
        es = sorted([e for e in ENTRIES if e['cat'] == cat], key=lambda e: e['label'].lower())
        if not es:
            continue
        out.append(f'<h4 class="gl-cat">{html.escape(cname)}</h4><div class="table-wrap"><table><thead><tr><th>용어</th><th>뜻</th></tr></thead><tbody>')
        for e in es:
            no, title = numfn(e['topic']) if e['topic'] else ('', '')
            ko = f'<br><small>공식 표기: {html.escape(e["ko"])}</small>' if e['ko'] else ''
            link = f' <a href="#{e["topic"]}">자세히: {html.escape((no + " " + title).strip())}</a>' if e['topic'] and title else ''
            d = markdown.markdown(e['def'])[3:-4]
            out.append(f'<tr><td data-label="용어"><b>{html.escape(e["label"])}</b><br><small>{html.escape(e["en"])}</small>{ko}</td>'
                       f'<td data-label="뜻">{d}{link}</td></tr>')
        out.append('</tbody></table></div>')
    return ''.join(out)
