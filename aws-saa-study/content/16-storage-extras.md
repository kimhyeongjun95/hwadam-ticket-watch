@part ch16 | AWS Storage Extras: 대용량 이전과 하이브리드 스토리지 | 강의 섹션 16 | 16. 스토리지 추가 서비스
S3, EBS, EFS 말고도 시험에 자주 나오는 스토리지 서비스가 있습니다. 데이터를 기기에 담아 옮기는 Snow Family, 상용 파일 시스템을 그대로 쓰는 FSx, 회사 전산실과 AWS 스토리지를 잇는 Storage Gateway, FTP로 S3에 넣는 Transfer Family, 데이터를 자동으로 옮기는 DataSync입니다. 이 장의 문제는 "어떤 프로토콜인가", "온라인인가 오프라인인가", "윈도우인가 HPC인가" 같은 단서로 답이 갈립니다.

@topic c16-snow | Snow Family: 기기로 대용량 데이터 옮기기 | dom=3,4 | prio=2 | les=AWS Snow Family Overview; AWS Snow Family Hands On; Architecture: Snowball into Glacier
**Snow Family**는 AWS가 보내 준 **기기에 데이터를 담아 택배로 돌려보내면** AWS가 S3에 넣어 주는 오프라인 이전 방식입니다. 네트워크가 느리거나 비싸거나 불안정할 때, 수십 TB에서 PB 규모를 옮길 때 씁니다.

#### 네트워크로 옮기면 얼마나 걸리나

| 데이터 양 | 100Mbps | 1Gbps | 10Gbps |
|---|---|---|---|
| 10TB | 약 9일 | 약 1일 | 약 2시간 |
| 100TB | 약 93일 | 약 9일 | 약 1일 |
| 1PB | 약 2.5년 | 약 93일 | 약 9일 |

(회선을 100% 쓴다고 가정한 값입니다. 실제로는 더 걸립니다.) 강의의 기준은 **네트워크로 1주일 넘게 걸리면 기기**를 쓰라는 것입니다.

#### 기기와 쓰임

| 기기 | 특징 |
|---|---|
| Snowball Edge Storage Optimized | 210TB NVMe. 대용량 이전 |
| Snowball Edge Compute Optimized | vCPU 104개, 메모리 416GB, 28TB. 인터넷이 없는 현장의 **엣지 컴퓨팅**(EC2, Lambda 실행) |

- **데이터 이전**: 콘솔에서 기기 주문 → 기기에 데이터 복사(Snowball 클라이언트, OpsHub) → 반송 → AWS가 S3에 넣음 → 기기 데이터 완전 삭제
- **엣지 컴퓨팅**: 배, 광산, 트럭처럼 네트워크가 약한 곳에서 데이터를 미리 처리
- **OpsHub**: 기기를 다루는 데스크톱 GUI 프로그램

#### Snowball에서 Glacier로

Snowball은 데이터를 **Glacier로 바로 넣지 못합니다**. 먼저 S3에 넣고, **수명 주기 규칙**으로 Glacier 클래스로 옮깁니다.

> **바뀐 점** AWS Snowcone은 2024년 11월에, Snowmobile은 2024년에 서비스를 끝냈고, **Snowball Edge를 포함한 모든 Snow 기기는 2025년 11월 7일부터 새 고객이 주문할 수 없습니다**(기존 고객은 계속 사용). AWS는 대안으로 온라인 이전은 **DataSync**, 물리적 이전은 **AWS Data Transfer Terminal**(AWS 시설에 직접 저장 장치를 가져가 고속으로 올림)이나 파트너 서비스, 엣지 컴퓨팅은 **Outposts**를 안내합니다. 시험 문제에는 여전히 "네트워크로 몇 주 걸리는 수십 TB → Snowball"로 나올 수 있습니다.

> **시험 포인트** "회선이 느려 네트워크로 옮기면 몇 주, 수십~수백 TB" → Snowball Edge(오프라인 이전). "인터넷이 없는 현장에서 데이터를 미리 처리" → Snowball Edge Compute Optimized. "Snowball 데이터를 Glacier에" → S3에 넣은 뒤 수명 주기 규칙. "지속적으로 동기화" → 오프라인 기기가 아니라 DataSync([16.4](#c16-datasync)).

> **후기에서** 2026년 2월 정리 노트는 "1주일 안에 50TB를 옮겨야 하는데 회사 인터넷이 느리다 → Snowball", "온라인 전송, 지속적 동기화 → DataSync"로 갈랐습니다.

@practice
- **데이터 센터 철수**: 전산실을 정리하며 파일 서버와 백업 수백 TB를 옮기는데 회선이 느리면, 기기에 담아 보내고 이후 바뀐 부분만 DataSync로 맞추는 방식이 흔했습니다.
- **영상·연구 데이터**: 방송사나 영화 제작사의 원본 영상, 연구소 장비가 만든 대용량 데이터를 클라우드로 옮길 때 썼습니다.
- **현장 엣지 컴퓨팅**: 선박, 광산, 군 작전처럼 네트워크가 약한 곳에서 데이터를 미리 처리하는 데 Compute Optimized를 썼습니다.
- **지금 새로 시작한다면**: 2025년 11월부터 새 고객은 기기를 주문할 수 없으므로, 회선이 허락하면 DataSync, 물리 이전이 필요하면 AWS Data Transfer Terminal이나 파트너 서비스, 현장 컴퓨팅은 Outposts를 검토합니다.

@easy
Snow Family는 인터넷 대신 택배로 데이터를 옮기는 방법입니다. 데이터가 너무 많아 회선으로 보내면 몇 달이 걸릴 때, AWS가 보내 준 대용량 저장 장치에 데이터를 담아 돌려보내면 AWS가 S3에 넣어 줍니다. 이사할 때 짐이 많으면 택배로 하나씩 부치지 않고 트럭을 부르는 것과 같습니다.

@topic c16-fsx | Amazon FSx: Windows, Lustre, NetApp ONTAP, OpenZFS | dom=2,3 | prio=3 | les=Amazon FSx; Amazon FSx - Hands On
**FSx**는 서드파티 고성능 파일 시스템을 AWS가 관리해 주는 서비스입니다. EFS가 "리눅스용 NFS"라면, FSx는 **윈도우, HPC, NetApp, ZFS** 같은 특정 파일 시스템이 필요할 때 씁니다.

| FSx 종류 | 프로토콜 | 특징 | 언제 |
|---|---|---|---|
| **FSx for Windows File Server** | **SMB**, NTFS | **Microsoft Active Directory** 연동, ACL, 사용자 할당량. 리눅스 EC2에서도 마운트. DFS 네임스페이스로 여러 파일 시스템을 묶음. 다중 AZ, 매일 S3로 백업, SSD·HDD | 윈도우 파일 공유, 회사 AD 사용자 권한 |
| **FSx for Lustre** | Lustre(POSIX) | 병렬 분산 파일 시스템. 밀리초 미만 지연, 수백 GB/s, 수백만 IOPS. **S3와 연동**(S3를 파일 시스템처럼 읽고 결과를 S3에 씀) | **HPC**, 머신러닝, 동영상 처리, 금융 모델링 |
| **FSx for NetApp ONTAP** | **NFS, SMB, iSCSI** | NetApp ONTAP을 그대로. 리눅스, 윈도우, macOS, VMware Cloud on AWS 등 폭넓게 호환. 용량 자동 확장, 스냅샷, 복제, 압축, 중복 제거, **즉시 복제(클론)** | 온프레미스 NetApp을 옮길 때, 여러 프로토콜이 함께 필요할 때 |
| **FSx for OpenZFS** | **NFS**(v3–v4.2) | ZFS 워크로드 이전. 최대 수백만 IOPS, 밀리초 미만 지연. 스냅샷, 압축, 즉시 복제 | 온프레미스 ZFS를 옮길 때 |

#### FSx for Lustre의 배포 방식

| | 스크래치(Scratch) | 영구(Persistent) |
|---|---|---|
| 데이터 복제 | 없음(서버가 고장 나면 데이터 잃음) | **같은 AZ 안에서 복제**, 고장 난 파일은 몇 분 안에 교체 |
| 성능 | 순간 성능이 높음 | 꾸준함 |
| 쓰임 | **단기 처리**, 비용 절감 | **장기 처리**, 민감한 데이터 |

#### FSx for Windows File Server의 배포

단일 AZ와 **다중 AZ**(대기 파일 서버를 다른 AZ에 두고 자동 장애 조치)가 있습니다. 온프레미스에서도 VPN이나 Direct Connect로 접근할 수 있습니다.

> **시험 포인트** "윈도우 앱, SMB, Active Directory 권한" → FSx for Windows File Server. "HPC·ML, S3 데이터를 고속 파일 시스템으로" → FSx for Lustre(단기면 스크래치, 장기면 영구). "NFS·SMB·iSCSI를 함께, 온프레미스 NetApp" → FSx for NetApp ONTAP. "온프레미스 ZFS" → FSx for OpenZFS. "리눅스 여러 대가 NFS로 공유, 용량 자동 확장" → EFS([7.6](#c07-efs)).

> **후기에서** 2026년 2월 정리 노트의 키워드: "파일 공유(SMB) + 윈도우 + AD 통합 → FSx for Windows File Server", "고성능 컴퓨팅 + 병렬 파일 시스템 → FSx for Lustre".

@practice
- **FSx for Windows File Server**: 사내 부서 공유 드라이브(`\\fileserver\영업팀`)를 클라우드로 옮기면서 Active Directory 권한을 그대로 유지합니다. .NET 앱이나 SQL Server가 SMB 공유를 쓰는 경우에도 씁니다.
- **FSx for Lustre**: 반도체 설계 시뮬레이션, 유전체 분석, 대규모 ML 학습처럼 수많은 서버가 같은 데이터를 매우 빠르게 읽어야 하는 일에 씁니다. 학습 데이터는 S3에 두고 Lustre로 연결해 빠르게 읽습니다.
- **FSx for NetApp ONTAP**: 사내에서 NetApp 스토리지를 쓰던 기업이 같은 기능(스냅샷, SnapMirror 복제, 즉시 클론)을 유지하며 옮길 때 고릅니다. 리눅스와 윈도우 서버가 같은 데이터를 함께 쓰는 환경에도 맞습니다.
- **FSx for OpenZFS**: ZFS 기반 NAS를 쓰던 리눅스 워크로드를 옮길 때 씁니다.

@easy
EFS가 리눅스용 범용 공유 드라이브라면, FSx는 특정 업계에서 쓰던 전문 파일 서버를 그대로 빌려주는 서비스입니다. 윈도우 회사망에서 쓰던 파일 서버, 연구소 슈퍼컴퓨터가 쓰는 초고속 병렬 파일 시스템, 기업용 NetApp 스토리지, ZFS 스토리지 중 원래 쓰던 것과 같은 종류를 고르면, 앱을 거의 고치지 않고 옮길 수 있습니다.

@topic c16-sgw | Storage Gateway와 Transfer Family | dom=2,3 | prio=3 | les=Storage Gateway Overview; Storage Gateway Hands On; AWS Transfer Family
**하이브리드 클라우드**는 회사 전산실(온프레미스)과 AWS를 함께 쓰는 형태입니다. 클라우드 이전 중이거나, 보안·규정상 일부를 전산실에 둬야 하거나, 클라우드를 백업·용량 확장에 쓰고 싶을 때입니다. S3는 HTTP API로만 다루므로, 전산실 서버가 익숙한 **NFS·SMB·iSCSI**로 AWS 스토리지를 쓰게 해 주는 것이 **Storage Gateway**입니다.

#### AWS 스토리지의 세 갈래

| 종류 | 서비스 |
|---|---|
| 블록 | EBS, EC2 인스턴스 스토어 |
| 파일 | EFS, FSx |
| 객체 | S3, Glacier |

#### 게이트웨이 종류

| 게이트웨이 | 전산실 쪽 프로토콜 | AWS 쪽 저장 | 특징 |
|---|---|---|---|
| **S3 File Gateway** | **NFS, SMB** | S3(Standard, IA 등) | 자주 쓰는 데이터는 게이트웨이에 **캐시**. 파일 하나 = 객체 하나. SMB는 Active Directory로 사용자 인증. 수명 주기로 Glacier에 보관 가능 |
| FSx File Gateway | SMB | FSx for Windows File Server | 윈도우 파일 서버를 전산실에서 낮은 지연으로 캐시 접근. **2024년 10월 28일부터 새 고객 불가** |
| **Volume Gateway** | **iSCSI**(블록) | S3 + **EBS 스냅샷** | **캐시 볼륨**: 데이터는 S3, 자주 쓰는 것만 로컬. **저장 볼륨**: 데이터 전체는 로컬, S3로 비동기 백업. 온프레미스 서버 볼륨 백업·복원 |
| **Tape Gateway** | iSCSI **가상 테이프 라이브러리(VTL)** | S3 + Glacier | 기존 **테이프 백업 소프트웨어를 그대로** 쓰면서 물리 테이프를 없앰 |

게이트웨이는 전산실의 VM(VMware, Hyper-V, KVM)이나 EC2로 실행합니다. 전용 **하드웨어 어플라이언스**는 2025년 5월 12일부터 판매하지 않습니다(기존 기기는 2028년 5월까지 지원).

#### AWS Transfer Family

**FTP, FTPS, SFTP**(그리고 AS2)로 S3나 EFS에 파일을 넣고 빼게 해 주는 완전 관리형 서비스입니다.

- 고객사나 협력사가 **기존 FTP·SFTP 클라이언트와 스크립트를 바꾸지 않고** 파일을 보낼 때 씁니다.
- 엔드포인트 시간당 요금 + 전송량 요금입니다.
- 사용자 인증을 직접 관리하거나 Active Directory, LDAP, Okta, Cognito, 사용자 지정 방식과 연동합니다.
- 다중 AZ로 가용성이 높고, 자동으로 확장합니다.

> **시험 포인트** "온프레미스 파일 서버가 NFS·SMB로 S3에 저장, 자주 쓰는 파일은 빠르게" → S3 File Gateway. "온프레미스 서버의 iSCSI 볼륨을 클라우드에 백업, 저지연 접근" → Volume Gateway(전체 데이터를 로컬에 두면 저장 볼륨, 일부만 두면 캐시 볼륨). "테이프 백업 소프트웨어를 유지하며 테이프를 클라우드로" → Tape Gateway. "협력사가 SFTP로 S3에 파일 업로드" → Transfer Family.

> **후기에서** 2026년 2월 합격 후기는 문제를 풀며 막혔던 예로 Storage Gateway를 들었습니다. "종류(S3 File, FSx File, Tape, Volume)를 물어보고, 각각의 대략적인 특징이 답을 고르는 근거가 된다"고 적었습니다. 온프레미스가 윈도우라는 단서가 있으면 FSx File Gateway 쪽으로 기울 수 있다는 예도 들었는데, FSx File Gateway는 이제 새 고객을 받지 않으므로 보기의 다른 단서도 함께 봅니다.

@practice
- **S3 File Gateway**: 사내 파일 서버의 오래된 자료를 클라우드로 옮기면서도 직원들은 원래 쓰던 공유 폴더로 접근하게 하거나, 지점 사무실 NAS를 대신합니다. 온프레미스 백업 소프트웨어의 저장 대상으로도 씁니다.
- **Volume Gateway**: 온프레미스 서버의 디스크를 클라우드에 백업해 두고, 재해 때 그 스냅샷으로 AWS에서 EC2를 띄워 복구합니다.
- **Tape Gateway**: 금융·공공기관처럼 테이프 백업 절차가 규정에 들어 있는 곳이, 백업 소프트웨어와 절차는 그대로 두고 물리 테이프 보관·운반만 없앱니다.
- **Transfer Family**: 협력사·고객사와 정산 파일, 주문 파일을 SFTP로 주고받는 오래된 배치 연동을 서버 운영 없이 이어 갑니다. 받은 파일은 S3에 들어오므로 이벤트 알림으로 후속 처리를 시작합니다.

@easy
Storage Gateway는 사내에 두는 클라우드 연결 장치입니다. 사내 서버와 직원들은 원래 쓰던 방식(공유 폴더, 디스크, 테이프)대로 저장하고, 장치가 뒤에서 그 데이터를 AWS에 넣어 줍니다. 자주 쓰는 데이터는 장치에 복사본을 남겨 빨리 꺼냅니다.

Transfer Family는 협력사가 쓰는 오래된 파일 전송 방식(FTP, SFTP)을 받아 주는 접수 창구입니다. 상대방은 아무것도 바꾸지 않아도 되고, 받은 파일은 S3나 EFS에 쌓입니다.

@topic c16-datasync | DataSync와 스토리지 한눈에 비교 | dom=2,3,4 | prio=3 | les=DataSync - Overview; All AWS Storage Options Compared
#### AWS DataSync

대용량 데이터를 **온라인으로 옮기고 정기적으로 동기화**하는 서비스입니다.

- **어디서 어디로**: 온프레미스·다른 클라우드(NFS, SMB, HDFS, S3 호환 API 등) → AWS. 이때 전산실에 **DataSync 에이전트**를 설치합니다. AWS 서비스 사이(S3 ↔ EFS ↔ FSx)는 에이전트 없이 옮깁니다.
- **대상**: S3(Glacier 포함 모든 클래스), EFS, FSx(Windows, Lustre, NetApp ONTAP, OpenZFS)
- **일정**: 매시간, 매일, 매주처럼 예약해서 동기화합니다(실시간 연속 복제가 아님).
- **권한과 메타데이터 보존**: NFS의 POSIX 권한, SMB의 권한, 타임스탬프를 그대로 옮깁니다. **이 점이 시험 단서**입니다.
- 에이전트 하나가 최대 10Gbps를 씁니다. 대역폭 제한을 걸어 업무 회선을 지킬 수 있습니다.
- 네트워크가 너무 느리면 기기(Snowball)와 함께 씁니다.

#### 스토리지 한눈에 비교

| 서비스 | 형태 | 한 줄 요약 |
|---|---|---|
| S3 | 객체 | 무제한, 싸고 튼튼함, HTTP API |
| S3 Glacier | 객체(보관) | 아카이브, 꺼내는 데 시간·요금 |
| EBS | 블록(네트워크) | EC2 한 대에 붙임(io1·io2 다중 연결 예외), AZ 안 |
| 인스턴스 스토어 | 블록(물리) | 가장 빠른 IOPS, 인스턴스가 멈추면 사라짐 |
| EFS | 파일(NFS) | 리눅스 여러 대가 여러 AZ에서 공유, POSIX |
| FSx for Windows | 파일(SMB) | 윈도우, Active Directory |
| FSx for Lustre | 파일(병렬) | HPC, 리눅스, S3 연동 |
| FSx for NetApp ONTAP | 파일·블록 | NFS·SMB·iSCSI 모두, 넓은 호환 |
| FSx for OpenZFS | 파일(NFS) | ZFS 이전 |
| Storage Gateway | 하이브리드 | 온프레미스 ↔ S3·FSx(파일, 볼륨, 테이프) |
| Transfer Family | 전송 | FTP·FTPS·SFTP로 S3·EFS |
| DataSync | 전송 | 예약 동기화, 권한·메타데이터 보존 |
| Snow Family | 오프라인 전송 | 기기에 담아 이전, 엣지 컴퓨팅(새 고객 불가) |
| DB | 구조화 데이터 | 인덱스와 쿼리가 필요한 데이터([21.1](#c21-choose)) |

> **시험 포인트** "온프레미스 NFS 파일 서버를 EFS로 옮기고 매일 동기화, 권한 유지" → DataSync. "S3 버킷에서 EFS로 데이터 복사" → DataSync(에이전트 불필요). "50TB를 네트워크로 옮기면 몇 주" → Snowball(+ 이후 증분은 DataSync). "온프레미스 앱이 계속 쓰면서 저장은 S3로" → Storage Gateway(이전이 아니라 연결).

@practice
- **데이터 센터 이전**: NAS 데이터를 먼저 전체 복사해 두고, 전환 당일까지 매일 밤 바뀐 부분만 동기화한 뒤 마지막 동기화와 함께 전환합니다. 파일 권한과 타임스탬프가 그대로 옮겨져 사용자가 차이를 느끼지 못합니다.
- **정기 백업**: 온프레미스 파일 서버를 매일 밤 S3로 동기화해 오프사이트 백업으로 씁니다.
- **AWS 안에서 옮기기**: S3 버킷의 데이터를 EFS나 FSx로 옮기거나, 다른 계정의 버킷으로 대량 이동할 때 에이전트 없이 씁니다.
- **회선 보호**: 업무 시간에는 대역폭 제한을 낮게 걸어 회사 인터넷이 느려지지 않게 합니다.

@easy
DataSync는 정기 이사 서비스입니다. 사내에 이사 담당자(에이전트)를 두면, 정한 시간마다 새로 생기거나 바뀐 파일을 AWS로 옮깁니다. 파일에 붙은 권한과 날짜까지 그대로 옮기는 점이 일반 복사와 다릅니다.

스토리지를 고를 때는 세 가지를 묻습니다. 블록(디스크), 파일(공유 폴더), 객체(S3) 중 무엇이 필요한가. 한 서버가 쓰나 여러 서버가 함께 쓰나. 리눅스인가 윈도우인가.

@quiz
Q: 회선이 100Mbps인 전산실에서 200TB를 2주 안에 AWS로 옮겨야 합니다. 새로 설계한다면 무엇을 고려하나요? 시험 보기라면 무엇인가요?
A: 네트워크로는 몇 달이 걸리므로 물리적 이전이 필요합니다. 시험 보기라면 Snowball Edge이고, 새 고객이라면 AWS Data Transfer Terminal이나 파트너 서비스를 검토합니다.
Q: Snowball로 가져온 데이터를 비용이 가장 싼 보관 클래스에 두려면?
A: Snowball이 S3에 넣은 뒤 수명 주기 규칙으로 Glacier Deep Archive로 옮깁니다.
Q: 윈도우 앱이 SMB 파일 공유와 Active Directory 권한을 필요로 합니다.
A: FSx for Windows File Server입니다.
Q: S3에 있는 대량의 학습 데이터를 고속 파일 시스템으로 읽어 며칠 동안 ML 학습을 돌리고, 끝나면 버립니다. 가장 싼 구성은?
A: FSx for Lustre 스크래치 배포를 S3와 연동합니다.
Q: 온프레미스 앱이 NFS로 파일을 쓰는데, 저장은 S3에 하고 최근 파일은 빠르게 읽어야 합니다.
A: S3 File Gateway입니다.
Q: 기존 테이프 백업 소프트웨어를 바꾸지 않고 물리 테이프를 없애려 합니다.
A: Tape Gateway(가상 테이프 라이브러리)입니다.
Q: 협력사가 SFTP로만 파일을 보낼 수 있는데, 파일은 S3에 저장돼야 합니다.
A: AWS Transfer Family의 SFTP 엔드포인트를 S3에 연결합니다.
Q: 온프레미스 NFS 서버의 파일을 매일 밤 EFS로 동기화하고 POSIX 권한을 유지해야 합니다.
A: DataSync 에이전트를 설치하고 매일 실행되는 DataSync 작업을 만듭니다.
