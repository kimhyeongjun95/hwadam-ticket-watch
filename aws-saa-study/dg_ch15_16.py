from dg import Diagram, reg


@reg('c15-cloudfront')
def _():
    D = Diagram('c15-cloudfront', w=600, at='오리진(Origin)의 종류',
                cap='캐시가 있는 엣지는 바로 응답하고, 없는 엣지는 오리진에서 가져와 TTL 동안 캐시합니다. OAC를 쓰면 버킷 정책이 이 배포만 허용하므로 S3 URL로 직접 오는 요청은 거부됩니다.',
                kcap='물건이 있는 편의점은 바로 팔고, 없는 편의점은 본점에서 가져와 진열해요. 본점 창고는 편의점 직원만 들어갈 수 있어요.')
    D.group(156, 8, 178, 206, '전 세계 엣지', k='동네 편의점들', solid=True)
    D.node('u1', 8, 40, 130, 56, '사용자', '뉴욕', 'user', k='손님', ksub='뉴욕')
    D.node('u2', 8, 144, 130, 56, '사용자', '부산', 'user', k='손님', ksub='부산')
    D.node('e1', 170, 40, 150, 56, 'CloudFront 엣지', '캐시 있음 → 바로', t='ok', k='편의점', ksub='물건 있음 → 바로')
    D.node('e2', 170, 144, 150, 56, 'CloudFront 엣지', '캐시 없음 → 오리진', t='warn', k='편의점', ksub='물건 없음 → 본점')
    D.node('s3', 420, 100, 172, 80, 'S3 버킷', 'OAC로 이 배포만 허용', 'bucket', t='hl', k='본점 창고', ksub='편의점 직원만')
    D.node('u3', 8, 236, 130, 56, '사용자', 'S3 URL 직접', 'user', k='손님', ksub='본점에 직접')
    D.edge('u1', 'e1', t='acc')
    D.edge('u2', 'e2', t='acc')
    D.edge('e2', 's3', '가져와 캐시', k='가져와 진열', t='acc')
    D.edge('u3', 's3', '거부 (403)', k='못 들어감', t='bad', dash=True, sa='r', sb='b')
    D.text(156, 318, 'Shield Standard로 DDoS 방어 · WAF 연동', k='편의점이 문 앞에서 몰려드는 손님을 막아 줘요')
    return D


@reg('c15-cf-origins')
def _():
    D = Diagram('c15-cf-origins', w=600, at='지리적 제한(Geo Restriction)',
                cap='공개 ALB 오리진은 ALB 보안 그룹이 CloudFront IP 대역만, EC2 보안 그룹이 ALB만 허용합니다. VPC 오리진은 ALB까지 프라이빗 서브넷에 두고 CloudFront만 닿게 합니다.',
                kcap='데스크를 길가에 두면 "편의점 직원만" 문지기를 세우고, 뒷문 통로를 쓰면 데스크까지 안쪽에 숨겨요.')
    D.group(8, 8, 584, 108, '공개 ALB 오리진', k='데스크를 길가에', solid=True)
    D.node('cf', 20, 44, 130, 56, 'CloudFront', None, 'cloud', t='hl', k='편의점')
    D.node('alb', 200, 44, 170, 56, 'ALB (공개)', 'SG: CloudFront 대역만', t='warn', k='안내 데스크 (길가)', ksub='편의점 직원만')
    D.node('ec2', 420, 44, 160, 56, 'EC2 (프라이빗)', 'SG: ALB만', t='ok', k='작업실 (안쪽)', ksub='데스크만')
    D.edge('cf', 'alb', t='acc')
    D.edge('alb', 'ec2', t='acc')
    D.group(8, 128, 584, 140, 'VPC 오리진 (2024년 11월~)', k='뒷문 통로', solid=True)
    D.group(186, 156, 398, 104, '프라이빗 서브넷', k='단지 안쪽', lpos='bl')
    D.node('cf2', 20, 176, 130, 56, 'CloudFront', None, 'cloud', t='hl', k='편의점')
    D.node('alb2', 200, 166, 170, 56, 'ALB (프라이빗)', '공개 IP 없음', t='ok', k='안내 데스크 (안쪽)', ksub='길가 문 없음')
    D.node('ec2b', 420, 166, 160, 56, 'EC2 (프라이빗)', 'SG: ALB만', t='ok', k='작업실 (안쪽)', ksub='데스크만')
    D.edge('cf2', 'alb2', t='acc')
    D.edge('alb2', 'ec2b', t='acc')
    return D


@reg('c15-cf-origins:geo')
def _():
    D = Diagram('c15-cf-origins:geo', w=560, at='end:지리적 제한(Geo Restriction)',
                cap='허용 목록에 한국과 일본만 넣으면 그 나라에서 온 요청만 콘텐츠를 받고, 다른 나라의 요청은 403을 받습니다.',
                kcap='"한국과 일본 손님에게만 팔아요" 목록을 걸면 다른 나라 손님은 못 사요.')
    D.node('kr', 8, 16, 130, 50, '한국 사용자', None, 'user', t='ok', k='한국 손님')
    D.node('jp', 8, 84, 130, 50, '일본 사용자', None, 'user', t='ok', k='일본 손님')
    D.node('us', 8, 152, 130, 50, '미국 사용자', None, 'user', t='warn', k='미국 손님')
    D.node('cf', 220, 60, 150, 100, 'CloudFront', '허용: KR, JP', 'cloud', t='hl', k='편의점', ksub='한국·일본만')
    D.node('ok', 430, 40, 122, 50, '콘텐츠 제공', t='ok', k='팔아요')
    D.node('no', 430, 130, 122, 50, '403 거부', t='warn', k='못 사요')
    D.edge('kr', 'cf', t='acc', sb=('l', 0.2))
    D.edge('jp', 'cf', t='acc', sb=('l', 0.45))
    D.edge('us', 'cf', t='bad', dash=True, sb=('l', 0.85))
    D.edge('cf', 'ok', t='ok')
    D.edge('cf', 'no', t='bad', dash=True)
    return D


@reg('c15-cf-origins:inval')
def _():
    D = Diagram('c15-cf-origins:inval', w=560, at='end:캐시 무효화(Invalidation)',
                cap='오리진에서 v2로 바꿔도 엣지는 TTL이 끝날 때까지 v1을 줍니다. 무효화를 만들면 다음 요청부터 v2를 가져옵니다.',
                kcap='본점이 새 물건을 내놔도 편의점은 진열 기간 동안 옛 물건을 팔아요. "다 내려!" 공지를 하면 바로 새 물건을 받아 와요.')
    D.text(8, 37, '오리진', k='본점', cls='lbl')
    D.bar(130, 16, 120, 30, 'v1', k='옛 물건', t='muted')
    D.bar(252, 16, 300, 30, 'v2 업로드', k='새 물건', t='ok')
    D.text(8, 85, 'TTL 기다림', k='진열 기간까지', cls='lbl')
    D.bar(130, 64, 300, 30, 'v1 (옛 파일 계속)', k='옛 물건 계속', t='warn')
    D.bar(432, 64, 120, 30, 'v2', k='새 물건', t='ok')
    D.text(8, 133, '무효화', k='"다 내려!"', cls='lbl')
    D.bar(130, 112, 120, 30, 'v1', k='옛 물건', t='muted')
    D.bar(252, 112, 80, 30, '무효화', k='공지', t='acc')
    D.bar(334, 112, 218, 30, 'v2', k='새 물건', t='ok')
    D.text(130, 168, '시간 →  (경로 1,000개/월 무료 · 파일 이름에 버전을 넣으면 무효화 불필요)', k='시간 →  (새 물건에 "2호" 이름을 붙이면 공지가 필요 없어요)')
    return D


@reg('c15-ga')
def _():
    D = Diagram('c15-ga', w=600, at='CloudFront와 비교',
                cap='세 대륙의 사용자가 모두 같은 고정 IP로 접속하지만 각자 가장 가까운 엣지로 들어오고, 그 뒤로는 AWS 전용망으로 엔드포인트 그룹(리전)까지 갑니다. 트래픽 다이얼로 리전별 비율을 정하고, 상태 확인에 실패한 리전은 바로 빠집니다.',
                kcap='세 나라 손님이 같은 입구 번호로 가지만 각자 가장 가까운 입구로 들어가고, 전용 고속도로로 지점까지 가요.')
    for i, (c, kc) in enumerate([('미국', '미국'), ('유럽', '유럽'), ('한국', '한국')]):
        y = 20 + i * 90
        D.node(f'u{i}', 8, y, 120, 52, '사용자', c, 'user', k='손님', ksub=kc)
        D.node(f'e{i}', 170, y, 130, 52, '엣지', '1.2.3.4', t='hl', k='고속도로 입구', ksub='같은 번호')
        D.edge(f'u{i}', f'e{i}', t='acc')
    D.group(360, 8, 232, 110, 'us-east-1', k='버지니아 도시', solid=True, lpos='bl')
    D.node('a1', 376, 20, 200, 56, 'ALB', '엔드포인트 그룹 · 50%', 'lb', lay='side', k='안내 데스크', ksub='손님 절반')
    D.group(360, 178, 232, 110, 'ap-northeast-2', k='서울 도시', solid=True, lpos='bl')
    D.node('a2', 376, 192, 200, 56, 'ALB', '엔드포인트 그룹 · 50%', 'lb', lay='side', k='안내 데스크', ksub='손님 절반')
    D.edge('e0', 'a1', t='acc')
    D.edge('e1', 'a1', t='acc', sa='r', sb='b', lp=0)
    D.edge('e2', 'a2', t='acc')
    D.text(170, 318, '고정 애니캐스트 IP 2개 · 엣지부터는 AWS 전용망 · TCP·UDP', k='어디서나 같은 입구 번호 두 개 · 입구부터는 전용 고속도로')
    return D


@reg('c16-snow')
def _():
    D = Diagram('c16-snow', w=600, at='end:Snowball에서 Glacier로',
                cap='전산실 데이터를 Snowball Edge에 복사해 반송하면 AWS가 S3에 넣고, 수명 주기 규칙으로 Glacier에 옮깁니다. 2025년 11월부터 새 고객은 아래 대안을 씁니다.',
                kcap='트럭에 짐을 싣고 돌려보내면 창고에 넣고, 정리 규칙으로 지하로 옮겨요. 새 손님은 아래 방법을 써요.')
    D.node('dc', 8, 30, 120, 80, '전산실', '수십 TB', 'building', k='사무실', ksub='이삿짐 많음')
    D.node('sb', 180, 30, 130, 80, 'Snowball Edge', '복사 후 반송', 'truck', t='hl', k='이삿짐 트럭', ksub='싣고 돌려보냄')
    D.node('s3', 362, 30, 110, 80, 'S3', '자동 적재', 'bucket', k='큰 창고', ksub='넣어 줌')
    D.node('gl', 524, 30, 68, 80, 'Glacier', '보관', 'tape', t='store', k='지하', ksub='보관실')
    D.edge('dc', 'sb', '① 복사', k='① 싣기', t='acc')
    D.edge('sb', 's3', '② 반송', k='② 배달', t='acc')
    D.edge('s3', 'gl', '③ 전환', k='③ 정리', t='acc')
    D.text(8, 150, '2025년 11월 7일부터 새 고객 대안', k='이제 새 손님은 이렇게 해요', cls='lbl')
    D.node('a1', 8, 166, 184, 64, 'DataSync', '온라인 이전·동기화', 'sync', t='muted', lay='side', k='정기 이사 서비스', ksub='인터넷으로 옮기기')
    D.node('a2', 204, 166, 192, 64, 'Data Transfer Terminal', '장치를 들고 가서 업로드', t='muted', k='도시 하역장', ksub='짐 들고 직접 가기')
    D.node('a3', 408, 166, 184, 64, 'Outposts', '현장 엣지 컴퓨팅', 'server', t='muted', lay='side', k='건물 안 도시 설비', ksub='현장에서 일하기')
    return D


@reg('c16-fsx')
def _():
    D = Diagram('c16-fsx', w=600, at='FSx for Lustre의 배포 방식',
                cap='쓰는 쪽과 함께 붙는 것으로 고릅니다. 윈도우와 AD는 FSx for Windows, HPC와 S3 연동은 Lustre, 여러 프로토콜과 NetApp 이전은 ONTAP, ZFS 이전은 OpenZFS입니다.',
                kcap='손님 종류에 맞는 전문 서류실을 골라요.')
    rows = [
        ('윈도우 서버', 'SMB', '윈도우 손님', '윈도우 방식', 'server', 'FSx for Windows', 'NTFS · 다중 AZ', '윈도우 서류실', '두 동네에 대기',
         'Active Directory', '사용자 권한', '회사 출입증 명단', '누가 열지', '인증', '확인'),
        ('HPC·ML 클러스터', 'Lustre', '연구실 손님', '슈퍼컴퓨터', 'chip', 'FSx for Lustre', '스크래치 / 영구', '초고속 서류실', '임시 / 튼튼한',
         'S3 버킷', '읽고 다시 씀', '큰 창고', '꺼내고 다시 넣음', 'S3 연동', '연결'),
        ('여러 OS', 'NFS · SMB · iSCSI', '여러 손님', '여러 방식', 'users', 'FSx for NetApp ONTAP', '클론 · 중복 제거', '만능 서류실', '순식간에 복제',
         'NetApp', '온프레미스에서 이전', '원래 서류실', '복사해 옮김', '복제', '복사'),
        ('ZFS 워크로드', 'NFS', '원래 방식 손님', '그대로', 'server', 'FSx for OpenZFS', 'NFS · 즉시 복제', '같은 방식 서류실', '순식간에 복제',
         'ZFS', '온프레미스에서 이전', '원래 서류실', '그대로 옮김', '이전', '옮김'),
    ]
    for i, (cl, cs, kcl, kcs, ci, fl, fs, kfl, kfs, xl, xs, kxl, kxs, el, kel) in enumerate(rows):
        y = 16 + i * 76
        D.node(f'c{i}', 8, y, 150, 56, cl, cs, k=kcl, ksub=kcs)
        D.node(f'f{i}', 210, y, 190, 56, fl, fs, t='hl', k=kfl, ksub=kfs)
        D.node(f'x{i}', 456, y, 136, 56, xl, xs, t='muted', k=kxl, ksub=kxs)
        D.edge(f'c{i}', f'f{i}', t='acc')
        D.edge(f'f{i}', f'x{i}', el, k=kel, both=True, dash=True)
    return D


@reg('c16-sgw')
def _():
    D = Diagram('c16-sgw', w=600, at='AWS Transfer Family',
                cap='전산실 서버는 익숙한 프로토콜(NFS·SMB, iSCSI, 가상 테이프)로 게이트웨이에 쓰고, 게이트웨이가 AWS의 S3, EBS 스냅샷, Glacier에 저장합니다. 자주 쓰는 데이터는 게이트웨이에 캐시합니다.',
                kcap='사무실 직원은 늘 쓰던 방식대로 창구에 맡기고, 창구가 도시 창고로 보내요.')
    D.group(8, 8, 250, 300, '온프레미스 전산실', k='회사 사무실', solid=True)
    D.group(318, 8, 274, 300, 'AWS', k='도시', solid=True)
    rows = [
        ('f', '파일 서버', 'NFS·SMB', '서류 담당', '공유 폴더 방식', 'g1', 'S3 File\nGateway', '서류\n창구', 's3', 'S3', '파일 = 객체', 'bucket', '큰 창고', '서류 보관'),
        ('v', '앱 서버', 'iSCSI', '업무 컴퓨터', '디스크 방식', 'g2', 'Volume\nGateway', '디스크\n창구', 'ebs', 'EBS 스냅샷', 'S3에 저장', 'camera', '디스크 사진', '창고에 보관'),
        ('t', '백업 SW', '가상 테이프', '백업 담당', '테이프 방식', 'g3', 'Tape\nGateway', '테이프\n창구', 'gl', 'S3·Glacier', '가상 테이프', 'tape', '창고·지하', '테이프 대신'),
    ]
    for i, (ak, al, asub, kal, kasub, gk, gl, kgl, sk, sl, ss, si, ksl, kss) in enumerate(rows):
        y = 40 + i * 88
        D.node(ak, 20, y, 110, 64, al, asub, k=kal, ksub=kasub)
        D.node(gk, 148, y, 98, 64, gl, t='hl', k=kgl)
        D.node(sk, 334, y, 160, 64, sl, ss, si, lay='side', t='store', k=ksl, ksub=kss)
        D.edge(ak, gk, t='acc')
        D.edge(gk, sk, t='acc')
    D.text(8, 332, 'FSx File Gateway(SMB → FSx for Windows)는 2024년 10월 28일부터 새 고객 불가',
           k='윈도우 서류실 창구는 이제 새 손님을 받지 않아요')
    return D


@reg('c16-sgw:transfer')
def _():
    D = Diagram('c16-sgw:transfer', w=600, at='end:AWS Transfer Family',
                cap='협력사는 기존 SFTP 클라이언트를 그대로 쓰고, Transfer Family가 파일을 S3나 EFS에 저장합니다. 사용자 인증은 서비스 자체나 AD, LDAP, Cognito 등과 연동합니다.',
                kcap='협력 회사가 옛날 택배 방식으로 보내도 창구가 받아 큰 창고나 서류실에 넣어 줘요.')
    D.node('p', 8, 60, 150, 64, '협력사', 'SFTP 클라이언트', 'building', lay='side', k='협력 회사', ksub='옛날 택배')
    D.node('tf', 210, 52, 166, 80, 'Transfer Family', 'FTP · FTPS · SFTP', 'gateway', t='hl', k='택배 창구', ksub='옛날 방식 받기')
    D.node('s3', 440, 16, 152, 56, 'S3', None, 'bucket', t='store', k='큰 창고')
    D.node('efs', 440, 116, 152, 56, 'EFS', None, 'folder', t='store', k='공용 서류실')
    D.node('auth', 210, 180, 166, 56, '사용자 인증', 'AD · LDAP · Cognito', 'idcard', lay='side', k='손님 확인', ksub='회원 명단')
    D.edge('p', 'tf', 'SFTP', k='옛 택배', t='acc')
    D.edge('tf', 's3', t='acc')
    D.edge('tf', 'efs', t='acc')
    D.edge('tf', 'auth', dash=True)
    return D


@reg('c16-datasync')
def _():
    D = Diagram('c16-datasync', w=600, at='스토리지 한눈에 비교',
                cap='전산실의 DataSync 에이전트가 NFS·SMB 서버를 읽어 DataSync로 보내고, DataSync가 예약한 시간마다 S3, EFS, FSx로 동기화합니다. AWS 서비스끼리는 에이전트 없이 옮깁니다.',
                kcap='사무실의 이사 담당 직원이 서류를 챙기면, 이사 서비스가 정한 시간마다 창고와 서류실로 옮겨요. 도시 안에서는 담당 직원이 필요 없어요.')
    D.group(8, 8, 200, 180, '온프레미스', k='사무실', solid=True)
    D.node('nfs', 20, 40, 176, 52, 'NFS·SMB 서버', None, 'server', k='사무실 서류장')
    D.node('agent', 20, 112, 176, 60, 'DataSync\n에이전트', '최대 10Gbps', 'gear', lay='side', k='이사 담당 직원', ksub='빠르게 날라요')
    D.node('ds', 260, 70, 140, 80, 'DataSync', '매일·매주 예약', 'sync', t='hl', k='정기 이사 서비스', ksub='정한 시간마다')
    D.node('s3', 450, 8, 142, 50, 'S3', None, 'bucket', t='store', k='큰 창고')
    D.node('efs', 450, 70, 142, 50, 'EFS', None, 'folder', t='store', k='공용 서류실')
    D.node('fsx', 450, 132, 142, 50, 'FSx', None, 'folder', t='store', k='전문 서류실')
    D.edge('nfs', 'agent', t='acc')
    D.edge('agent', 'ds', 'TLS', k='안전하게', t='acc')
    D.edge('ds', 's3', t='acc', sa=('r', 0.2), sb='l')
    D.edge('ds', 'efs', t='acc')
    D.edge('ds', 'fsx', t='acc')
    D.node('s3b', 220, 220, 140, 52, 'S3 버킷', None, 'bucket', t='store', k='큰 창고')
    D.node('efs2', 450, 220, 142, 52, 'EFS', None, 'folder', t='store', k='공용 서류실')
    D.edge('s3b', 'efs2', '에이전트 없이', k='직원 없이', t='acc')
    D.text(8, 300, '권한·타임스탬프 보존 · 연속 복제가 아닌 예약 동기화', k='"누가 볼 수 있음" 딱지까지 그대로, 정한 시간마다')
    return D
