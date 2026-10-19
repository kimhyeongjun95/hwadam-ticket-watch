from dg import Diagram, reg


@reg('c05-ec2')
def _():
    D = Diagram('c05-ec2', w=560, at='인스턴스를 만들 때 고르는 것',
                cap='인스턴스 하나는 AMI, 인스턴스 유형, 사용자 데이터, 키 페어, EBS, 보안 그룹, IAM 역할, 서브넷을 조합해 만듭니다.',
                kcap='작업실 하나를 빌릴 때 설계도, 방 크기, 첫날 쪽지, 열쇠, 사물함, 경비원, 방문증, 위치를 함께 골라요.')
    D.node('ec2', 210, 50, 140, 240, 'EC2 인스턴스', '실행 중인 서버', 'server', t='hl', k='작업실', ksub='빌린 방')
    left = [('ami', 'AMI', 'OS·소프트웨어 틀', 'layers', '인테리어 설계도', '책상·도구'),
            ('type', '인스턴스 유형', 'CPU·메모리', 'chip', '방 크기', '책상·창고'),
            ('ud', '사용자 데이터', '첫 부팅 스크립트', 'file', '첫날 쪽지', '할 일 목록'),
            ('key', '키 페어', 'SSH 접속', 'key', '열쇠', '문 열기')]
    right = [('ebs', 'EBS', '루트·데이터 디스크', 'disk', '사물함', '물건 보관'),
             ('sg', '보안 그룹', '방화벽', 'shield', '경비원', '문 앞 검사'),
             ('role', 'IAM 역할', '앱 권한', 'badge', '방문증', '로봇 권한'),
             ('sub', '서브넷', 'VPC 안 위치', 'subnet', '단지 구역', '방 위치')]
    for i, (key, l, s, ic, k, ks) in enumerate(left):
        D.node(key, 8, 64 + i * 56, 160, 44, l, s, ic, k=k, ksub=ks)
        D.edge(key, 'ec2')
    for i, (key, l, s, ic, k, ks) in enumerate(right):
        D.node(key, 392, 64 + i * 56, 160, 44, l, s, ic, k=k, ksub=ks)
        D.edge('ec2', key)
    return D


@reg('c05-types')
def _():
    D = Diagram('c05-types', w=560, at='패밀리별 용도',
                cap='m7g.2xlarge는 범용(m), 7세대, Graviton 프로세서(g), 2xlarge 크기(8 vCPU, 32GiB)입니다. 아래는 패밀리 글자와 용도의 짝입니다.',
                kcap='방 이름표는 방 종류, 몇 번째 모델, 기계 종류, 크기 순서로 적혀 있어요. 아래는 방 종류와 쓰임새예요.')
    top = [('a', 'm', '방 종류'), ('b', '7', '몇 번째'), ('c', 'g', '기계'), ('d', '2xlarge', '크기')]
    mid = [('패밀리', '범용', '보통 방', '대부분 여기'), ('세대', '숫자 클수록 최신', '7번째 모델', '클수록 새것'),
           ('속성', 'Graviton(ARM)', '새 기계', '전기 덜 씀'), ('크기', '8 vCPU · 32GiB', '큰 방', '책상 8개')]
    for i, ((key, l, k), (ml, ms, mk, mks)) in enumerate(zip(top, mid)):
        x = 8 + i * 138
        D.node('t' + key, x, 8, 128, 44, l, t='hl', k=k)
        D.node('m' + key, x, 86, 128, 52, ml, ms, k=mk, ksub=mks)
        D.edge('t' + key, 'm' + key)
    D.group(8, 160, 544, 100, '패밀리별 용도', k='방 종류별 쓰임새')
    fams = [('t · m', '범용', '보통 방', '대부분'), ('c', '컴퓨팅', '계산기 방', '계산 많을 때'),
            ('r · x', '메모리', '넓은 책상 방', '큰 지도 펼치기'), ('i · d', '스토리지', '빠른 서랍 방', '서류 많을 때'),
            ('p · g', 'GPU·가속', '그림 기계 방', '그림·인공지능')]
    for i, (l, s, k, ks) in enumerate(fams):
        D.node(f'f{i}', 18 + i * 106, 190, 100, 56, l, s, k=k, ksub=ks)
    return D


@reg('c05-sg')
def _():
    D = Diagram('c05-sg', w=600, at='end:동작 규칙',
                cap='보안 그룹을 사슬처럼 잇습니다. ALB는 인터넷의 443만, 앱은 ALB 보안 그룹에서 온 80만, DB는 앱 보안 그룹에서 온 3306만 받습니다. 인터넷에서 DB로 바로 가는 연결은 막힙니다.',
                kcap='경비원 셋이 차례로 지켜요. 안내 데스크는 바깥 손님을, 작업실은 데스크가 보낸 손님만, 기록실은 작업실 사람만 들여보내요.')
    D.node('net', 8, 58, 92, 80, '인터넷', '사용자', 'globe', t='muted', k='바깥 손님', ksub='누구나')
    D.group(126, 30, 150, 132, 'sg-alb', k='경비원 1')
    D.group(296, 30, 150, 132, 'sg-app', k='경비원 2')
    D.group(466, 30, 126, 132, 'sg-db', k='경비원 3')
    D.node('alb', 138, 58, 126, 84, 'ALB', '443 ← 인터넷', 'lb', k='안내 데스크', ksub='정문 손님 통과')
    D.node('app', 308, 58, 126, 84, 'EC2 앱', '80 ← sg-alb', 'server', k='작업실', ksub='데스크 손님만')
    D.node('db', 476, 58, 106, 84, 'RDS', '3306 ← sg-app', 'db', t='store', k='기록실', ksub='작업실 사람만')
    D.edge('net', 'alb', '443', k='정문', t='acc')
    D.edge('alb', 'app', '80', k='안내', t='acc')
    D.edge('app', 'db', '3306', k='기록', t='acc')
    D.edge('net', 'db', 'DB 직접 접속은 막힘', k='바로 들어가기는 막혀요', t='bad', dash=True, sa='b', sb='b', via=[(58, 190), (529, 190)], lp=1)
    return D


@reg('c05-connect')
def _():
    D = Diagram('c05-connect', w=560, at='인스턴스 역할',
                cap='SSH와 EC2 Instance Connect는 22번 포트가 열려 있어야 합니다. Session Manager는 인스턴스의 SSM 에이전트가 바깥으로 연결하므로 인바운드 포트를 열지 않습니다.',
                kcap='열쇠와 일회용 열쇠는 22번 문이 열려 있어야 해요. 비밀 통로는 문을 안 열고 관리실과 이어져 있어요.')
    D.node('who', 8, 110, 110, 56, '관리자', None, 'user', k='직원')
    D.node('ssh', 170, 20, 190, 52, 'SSH', '키 파일 · 22번 열기', 'key', k='내 열쇠', ksub='22번 문 열기')
    D.node('eic', 170, 110, 190, 62, 'EC2 Instance\nConnect', None, 'browser', k='일회용 열쇠', ksub='창구에서 받기')
    D.node('sm', 170, 200, 190, 52, 'Session Manager', '포트 안 엶 · 기록', 'terminal', t='ok', k='비밀 통로', ksub='문 안 엶 · 기록')
    D.node('ec2', 420, 90, 132, 100, 'EC2', '리눅스', 'server', t='hl', k='작업실', ksub='일하는 곳')
    for n in ('ssh', 'eic', 'sm'):
        D.edge('who', n)
    D.edge('ssh', 'ec2', '22번', k='22번 문', sb=('l', 0.2))
    D.edge('eic', 'ec2', '22번', k='22번 문')
    D.edge('sm', 'ec2', '에이전트', k='통로', t='ok', sb=('l', 0.85))
    return D


@reg('c05-purchase')
def _():
    D = Diagram('c05-purchase', w=600, at='예약 인스턴스와 Savings Plans',
                cap='막대 길이는 온디맨드 대비 최대 할인율입니다. 할인이 클수록 약정이 단단하거나(유형·리전 고정), 스팟처럼 회수될 위험을 집니다.',
                kcap='막대가 길수록 많이 깎아 줘요. 많이 깎아 줄수록 약속이 단단하거나, 남는 방처럼 비워 줘야 할 위험이 있어요.')
    rows = [('온디맨드', '그날 빌리기', 0, None, None, 'muted'),
            ('전환형 RI', '바꿀 수 있는 약속', 66, '66% · 유형 바꿀 수 있음', '66% · 방 바꿔도 됨', ''),
            ('Compute SP', '금액 약속(넓게)', 66, '66% · Fargate·Lambda까지', '66% · 어떤 방이든', ''),
            ('표준 RI', '방 약속', 72, '72% · 유형·리전 고정', '72% · 이 방만', 'soft'),
            ('EC2 Instance SP', '금액 약속(좁게)', 72, '72% · 패밀리·리전 고정', '72% · 이 종류 방만', 'soft'),
            ('스팟', '남는 방', 90, '90% · 2분 알림 후 회수', '90% · 2분 안에 비우기', 'warn')]
    for i, (l, k, pct, bl, bk, t) in enumerate(rows):
        y = 10 + i * 42
        D.text(12, y + 21, l, k=k, cls='lbl')
        if pct:
            D.bar(150, y, pct * 4.6, 30, bl, k=bk, t=t)
        else:
            D.bar(150, y, 6, 30, '', t=t)
            D.text(166, y + 20, '할인 없음 · 언제든 중지', k='할인 없음 · 언제든 그만')
    D.text(150, 272, '막대 길이 = 온디맨드 대비 최대 할인율(%)', k='막대 길이 = 깎아 주는 만큼')
    return D


@reg('c06-ip')
def _():
    D = Diagram('c06-ip', w=560, at='end:사설 IP, 공인 IP, 탄력적 IP',
                cap='자동 할당 공인 IP는 인스턴스를 중지했다 시작하면 바뀌고 사설 IP는 유지됩니다. 탄력적 IP는 계정이 소유해 고장 난 인스턴스에서 떼어 다른 인스턴스에 붙일 수 있습니다.',
                kcap='바깥 주소는 문을 닫았다 열면 바뀌어요. 내 이름 주소판은 떼어서 다른 작업실에 붙일 수 있어요.')
    D.group(8, 8, 272, 214, '자동 할당 공인 IP', k='바뀌는 바깥 주소')
    D.node('r1', 20, 40, 248, 56, 'EC2 (실행 중)', '공인 3.35.12.10 · 사설 10.0.1.5', 'server', k='작업실 (영업 중)', ksub='바깥 12번지 · 안쪽 201호')
    D.node('r2', 20, 150, 248, 56, 'EC2 (중지 후 시작)', '공인 13.209.5.7 · 사설 10.0.1.5', 'server', t='warn', k='작업실 (다시 열면)', ksub='바깥 57번지 · 안쪽 201호')
    D.edge('r1', 'r2', '중지 → 시작', k='닫았다 열기')
    D.group(296, 8, 256, 214, '탄력적 IP', k='내 이름 주소판')
    D.node('eip', 308, 40, 232, 52, '탄력적 IP 43.200.1.1', '계정 소유 · 고정', 'pin', t='hl', k='주소판 99번지', ksub='내 것 · 안 바뀜')
    D.node('a', 308, 140, 112, 76, 'EC2 A', '고장', 'server', t='warn', k='작업실 가', ksub='고장')
    D.node('b', 428, 140, 112, 76, 'EC2 B', '대기', 'server', t='ok', k='작업실 나', ksub='대기')
    D.edge('eip', 'a', '① 떼기', k='① 떼기', t='bad', dash=True)
    D.edge('eip', 'b', '② 붙이기', k='② 붙이기', t='ok')
    D.text(296, 246, '더 나은 설계: 로드 밸런서나 DNS 이름을 앞에 둠', k='더 좋은 방법: 가게 이름을 알려 주기')
    return D


@reg('c06-placement')
def _():
    D = Diagram('c06-placement', w=600, at='end:배치 그룹: 클러스터, 분산, 파티션',
                cap='클러스터는 한 랙 근처에 모아 지연을 줄이고, 분산은 인스턴스마다 다른 랙에 두며(AZ당 7대), 파티션은 칸마다 다른 랙 묶음을 써서 칸 단위로 고장을 격리합니다.',
                kcap='모여 앉으면 쪽지가 빠르고, 떨어져 앉으면 같이 멈추지 않고, 반을 나누면 한 반이 멈춰도 다른 반은 괜찮아요.')
    panels = [('클러스터', '모여 앉기', '지연 최소 · 함께 고장', '쪽지 빠름 · 함께 멈춤'),
              ('분산', '떨어져 앉기', 'AZ당 7대 · 따로 고장', '동네당 7개 · 따로 멈춤'),
              ('파티션', '반 나누기', '칸마다 다른 랙 · 수백 대', '반마다 다른 층 · 많이')]
    for p, (name, kname, note, knote) in enumerate(panels):
        x0 = 8 + p * 198
        D.group(x0, 8, 188, 262, name, k=kname, solid=True)
        D.group(x0 + 10, 36, 168, 196, '가용 영역', k='동네')
        if p == 0:
            D.group(x0 + 20, 64, 148, 160, '랙', k='층')
            for j in range(4):
                D.node(f'p{p}n{j}', x0 + 30 + (j % 2) * 68, 96 + (j // 2) * 60, 60, 44, str(j + 1))
        else:
            for r in range(3):
                rx = x0 + 18 + r * 52
                D.group(rx, 64, 46, 160, '랙' if p == 1 else f'P{r + 1}', k='층' if p == 1 else f'{r + 1}반')
                if p == 1:
                    D.node(f'p{p}n{r}', rx + 6, 124, 34, 44, str(r + 1))
                else:
                    D.node(f'p{p}n{r}a', rx + 6, 96, 34, 44, str(r * 2 + 1))
                    D.node(f'p{p}n{r}b', rx + 6, 156, 34, 44, str(r * 2 + 2))
        D.text(x0 + 14, 254, note, k=knote)
    return D


@reg('c06-eni-hibernate')
def _():
    D = Diagram('c06-eni-hibernate', w=600, at='최대 절전 모드(Hibernate)',
                cap='왼쪽: 보조 ENI를 고장 난 인스턴스에서 떼어 같은 AZ의 대기 인스턴스에 붙이면 사설 IP와 보안 그룹이 그대로 옮겨 갑니다. 오른쪽: 최대 절전 모드는 메모리를 암호화된 루트 EBS에 저장했다가 그대로 되살립니다.',
                kcap='왼쪽: 전화기를 옆 작업실에 옮겨 꽂으면 같은 번호로 전화가 와요. 오른쪽: 책상 위를 사진 찍어 두고 닫았다가, 다시 열 때 사진대로 펼쳐요.')
    D.group(8, 8, 280, 262, '같은 AZ', k='같은 동네')
    D.node('eni', 20, 40, 256, 56, '보조 ENI', '사설 IP 10.0.0.50 · 보안 그룹', 'plug', t='hl', k='옮겨 꽂는 전화기', ksub='번호 201 · 받는 규칙')
    D.node('a', 20, 160, 116, 56, 'EC2 A', '고장', 'server', t='warn', k='작업실 가', ksub='고장')
    D.node('b', 160, 160, 116, 56, 'EC2 B', '대기', 'server', t='ok', k='작업실 나', ksub='대기')
    D.edge('eni', 'a', '① 떼기', k='① 뽑기', t='bad', dash=True)
    D.edge('eni', 'b', '② 붙이기', k='② 꽂기', t='ok')
    D.group(304, 8, 288, 262, '최대 절전 모드', k='책상 사진 찍고 닫기')
    steps = [('실행 중', '메모리에 앱 상태', '일하는 중', '책상에 책 펼침', 'plain'),
             ('최대 절전', '메모리 → 암호화된 루트 EBS', '사진 찍기', '책상 위를 사물함에', 'hl'),
             ('중지', 'EBS 요금만 · 최대 60일', '닫아 둠', '사물함 값만 · 60일까지', 'plain'),
             ('다시 시작', 'EBS → 메모리, 그대로 이어서', '다시 열기', '사진 보고 그대로 펼침', 'ok')]
    for i, (l, s, k, ks, t) in enumerate(steps):
        D.node(f's{i}', 316, 36 + i * 58, 264, 42, l, s, t=t, k=k, ksub=ks)
        if i:
            D.edge(f's{i - 1}', f's{i}')
    return D


@reg('c07-ebs')
def _():
    D = Diagram('c07-ebs', w=600, at='종료 시 삭제(Delete on Termination)',
                cap='EBS는 AZ에 묶여 있습니다. 다른 AZ에서 쓰려면 스냅샷을 찍고(①) 그 AZ에서 새 볼륨으로 복원해(②) 붙입니다. 루트 볼륨은 기본적으로 인스턴스와 함께 지워지고, 추가 볼륨은 남습니다.',
                kcap='사물함은 동네에만 있어요. 다른 동네에서 쓰려면 사진을 찍고(①) 그 동네에서 새 사물함을 채워요(②).')
    D.group(8, 8, 584, 252, '리전', k='도시')
    D.group(20, 36, 240, 212, '가용 영역 a', k='동네 가')
    D.group(360, 36, 220, 212, '가용 영역 b', k='동네 나')
    D.node('ec2a', 32, 60, 216, 44, 'EC2', '인스턴스 1', 'server', k='작업실', ksub='작업실 1')
    D.node('root', 32, 132, 104, 76, '루트 볼륨', '종료 시 삭제', 'disk', t='store', k='기본 사물함', ksub='돌려줄 때 비움')
    D.node('data', 148, 132, 100, 76, '데이터 볼륨', '종료 후 남음', 'disk', t='store', k='추가 사물함', ksub='돌려줘도 남음')
    D.node('snap', 272, 132, 80, 76, '스냅샷', '리전에 저장', 'copy', t='hl', k='사진', ksub='도시에 보관')
    D.node('ec2b', 376, 60, 192, 44, 'EC2', '인스턴스 2', 'server', k='작업실', ksub='작업실 2')
    D.node('nv', 376, 132, 192, 76, '새 볼륨', '스냅샷에서 복원', 'disk', t='store', k='새 사물함', ksub='사진 보고 채움')
    D.edge('ec2a', 'root')
    D.edge('ec2a', 'data')
    D.edge('data', 'snap', '①', t='acc')
    D.edge('snap', 'nv', '②', t='acc')
    D.edge('nv', 'ec2b', '붙이기', k='연결')
    return D


@reg('c07-snapshot-ami')
def _():
    D = Diagram('c07-snapshot-ami', w=600, at='AMI(Amazon Machine Image)',
                cap='설정한 인스턴스를 멈추고 AMI를 만들면 EBS 스냅샷이 함께 생깁니다. 그 AMI로 설치 없이 새 인스턴스를 띄우고, 다른 리전으로 복사해 재해 복구에도 씁니다.',
                kcap='꾸민 작업실을 정리하고 설계도를 만들면 사물함 사진도 함께 들어가요. 설계도로 새 작업실을 바로 열고, 다른 도시로 복사해 비상용으로도 써요.')
    D.group(8, 8, 380, 232, '리전 A (서울)', k='도시 가 (서울)')
    D.group(404, 8, 188, 232, '리전 B (도쿄)', k='도시 나 (도쿄)')
    D.node('n1', 20, 40, 168, 56, '① 인스턴스 설정', '설치·설정', 'server', k='① 작업실 꾸미기', ksub='책상·도구 놓기')
    D.node('n2', 208, 40, 168, 56, '② 중지', '데이터 무결성', 'power', k='② 문 닫기', ksub='정리된 상태로')
    D.node('n3', 208, 160, 168, 64, '③ AMI 생성', 'EBS 스냅샷 포함', 'layers', t='hl', k='③ 설계도 만들기', ksub='사물함 사진 포함')
    D.node('n4', 20, 160, 168, 64, '④ 새 인스턴스', '설치 없이 바로', 'rocket', t='ok', k='④ 새 작업실', ksub='바로 일하기')
    D.node('b1', 416, 40, 164, 56, 'AMI 사본', '⑤ 리전 간 복사', 'copy', k='설계도 사본', ksub='⑤ 다른 도시로')
    D.node('b2', 416, 160, 164, 64, '인스턴스', '재해 복구용', 'server', t='ok', k='작업실', ksub='비상용')
    D.edge('n1', 'n2', t='acc')
    D.edge('n2', 'n3', t='acc')
    D.edge('n3', 'n4', t='acc')
    D.edge('n3', 'b1', '⑤ 복사', k='⑤ 복사', t='acc')
    D.edge('b1', 'b2', '시작', k='열기')
    return D


@reg('c07-instance-store')
def _():
    D = Diagram('c07-instance-store', w=560, at='end:인스턴스 스토어',
                cap='인스턴스 스토어는 호스트 서버에 직접 붙어 가장 빠르지만 인스턴스를 중지·종료하면 지워집니다. EBS는 네트워크로 붙어 인스턴스와 따로 남습니다.',
                kcap='책상 서랍은 바로 손이 닿지만 문을 닫으면 비워져요. 사물함은 복도 건너에 있어서 조금 느리지만 물건이 그대로 남아요.')
    D.group(8, 8, 300, 210, '호스트 서버 (물리 컴퓨터)', k='작업실 건물')
    D.node('ec2', 20, 40, 276, 52, 'EC2 인스턴스', None, 'server', t='hl', k='작업실')
    D.node('is', 20, 140, 276, 64, '인스턴스 스토어', '직접 연결 · 매우 빠름 · 중지하면 삭제', 'disk', t='warn', k='책상 서랍', ksub='바로 손닿음 · 닫으면 비워짐')
    D.node('ebs', 360, 40, 192, 64, 'EBS 볼륨', '네트워크 연결 · 유지', 'disk', t='store', k='개인 사물함', ksub='복도 건너 · 남음')
    D.edge('ec2', 'is', '직접', k='손')
    D.edge('ec2', 'ebs', '네트워크', k='복도')
    return D


@reg('c07-ebs-types')
def _():
    D = Diagram('c07-ebs-types', w=600, at='고르는 순서',
                cap='큰 순차 데이터이고 부팅 볼륨이 아니면 HDD(자주 읽으면 st1, 거의 안 읽으면 sc1), 아니면 SSD입니다. SSD 중 80,000 IOPS를 넘거나 다중 연결이 필요하면 io2 Block Express, 나머지는 gp3입니다.',
                kcap='긴 기록을 쭉 읽는 일이면 서랍 사물함, 아니면 빠른 사물함이에요. 정말 빨라야 하면 아주 빠른 사물함, 보통은 보통 빠른 사물함이에요.')
    D.node('q1', 180, 8, 240, 56, 'HDD로 충분한가?', '큰 순차 데이터 · 부팅 아님', k='긴 서랍이면 될까?', ksub='쭉 읽기 · 기본 열쇠 아님')
    D.node('q2', 8, 110, 270, 56, 'SSD: 고성능이 꼭 필요한가?', '80,000 IOPS 초과 · 다중 연결', k='아주 빨라야 할까?', ksub='엄청 자주 여닫기')
    D.node('q3', 330, 110, 262, 56, 'HDD: 자주 읽는가?', '로그·빅데이터 순차 읽기', k='자주 꺼내 볼까?', ksub='긴 기록 쭉 읽기')
    D.node('gp3', 8, 222, 126, 56, 'gp3', '대부분', t='ok', k='보통 빠른 사물함', ksub='대부분')
    D.node('io2', 152, 222, 126, 56, 'io2 BE', '최대 256,000 IOPS', t='hl', k='아주 빠른 사물함', ksub='제일 빠름')
    D.node('st1', 330, 222, 126, 56, 'st1', '자주 읽음 · 싸게', t='store', k='긴 서랍 사물함', ksub='자주 읽음')
    D.node('sc1', 466, 222, 126, 56, 'sc1', '거의 안 읽음', t='store', k='창고 구석 사물함', ksub='거의 안 읽음')
    D.edge('q1', 'q2', '아니오', k='아니요')
    D.edge('q1', 'q3', '예', k='네')
    D.edge('q2', 'gp3', '아니오', k='아니요')
    D.edge('q2', 'io2', '예', k='네')
    D.edge('q3', 'st1', '예', k='네')
    D.edge('q3', 'sc1', '아니오', k='아니요')
    return D


@reg('c07-efs')
def _():
    D = Diagram('c07-efs', w=600, at='설정 선택지',
                cap='EFS는 AZ마다 탑재 대상(ENI)을 두고, 여러 AZ의 EC2가 NFS로 같은 파일 시스템을 동시에 씁니다. 데이터는 여러 AZ에 저장되고 용량은 자동으로 늘고 줄어듭니다.',
                kcap='동네마다 서류실 창구가 있어서, 모든 동네의 작업실이 같은 공용 서류실을 함께 써요. 서류가 늘면 방이 저절로 커져요.')
    D.group(8, 8, 584, 262, '리전', k='도시')
    for i, (az, kaz) in enumerate([('a', '가'), ('b', '나'), ('c', '다')]):
        x = 20 + i * 190
        D.group(x, 36, 180, 152, f'가용 영역 {az}', k=f'동네 {kaz}')
        D.node(f'ec2{az}', x + 12, 62, 156, 44, 'EC2', '리눅스', 'server', k='작업실', ksub='함께 씀')
        D.node(f'mt{az}', x + 12, 134, 156, 44, '탑재 대상', 'ENI · 보안 그룹', 'plug', k='서류실 창구', ksub='동네마다 하나')
        D.edge(f'ec2{az}', f'mt{az}', 'NFS' if az == 'a' else None, k='드나들기' if az == 'a' else None)
        D.edge(f'mt{az}', 'efs')
    D.node('efs', 150, 200, 300, 56, 'EFS 파일 시스템', '여러 AZ에 저장 · 자동 확장', 'folder', t='store', k='공용 서류실', ksub='저절로 커짐 · 함께 씀')
    return D
