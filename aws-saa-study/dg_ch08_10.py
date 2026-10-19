from dg import Diagram, reg


@reg('c08-ha')
def _():
    D = Diagram('c08-ha', w=600, at='end:확장성과 고가용성',
                cap='수직 확장은 한 대를 키우고, 수평 확장은 대수를 늘립니다. 고가용성은 여러 AZ에 나눠 두어 AZ 하나가 멈춰도 서비스가 이어지게 합니다.',
                kcap='큰 방으로 옮기기, 방 여러 개 빌리기, 두 동네에 나눠 두기예요.')
    D.group(8, 8, 188, 240, '수직 확장', k='더 큰 방으로', solid=True)
    D.node('s', 30, 44, 144, 48, 't3.micro', '2 vCPU · 1GiB', 'server', k='작은 방', ksub='책상 2개')
    D.node('b', 30, 156, 144, 72, 't3.xlarge', '4 vCPU · 16GiB', 'server', t='hl', k='큰 방', ksub='책상 4개, 넓음')
    D.edge('s', 'b', '키우기', k='옮기기')
    D.group(206, 8, 188, 240, '수평 확장', k='방 여러 개', solid=True)
    D.node('one', 228, 44, 144, 48, 'EC2 1대', None, 'server', k='방 하나')
    for i in range(3):
        D.node(f'h{i}', 218 + i * 58, 168, 50, 48, str(i + 1), t='hl')
    D.edge('one', 'h1', '늘리기', k='더 빌리기')
    D.group(404, 8, 188, 240, '고가용성', k='두 동네에 나눠', solid=True)
    for j, (az, kaz) in enumerate([('AZ a', '동네 가'), ('AZ b', '동네 나')]):
        x = 414 + j * 86
        D.group(x, 36, 80, 200, az, k=kaz, lpos='bl')
        D.node(f'a{j}0', x + 10, 64, 60, 44, 'EC2', k='방')
        D.node(f'a{j}1', x + 10, 124, 60, 44, 'EC2', k='방')
    return D


@reg('c08-elb')
def _():
    D = Diagram('c08-elb', w=560, at='상태 확인',
                cap='사용자는 로드 밸런서의 DNS 이름 하나로 들어오고, 로드 밸런서는 상태 확인을 통과한 대상에만 요청을 나눕니다. 실패한 대상은 회복할 때까지 빠집니다.',
                kcap='손님은 대표 번호 하나로 오고, 안내 데스크는 "괜찮아요" 하고 대답한 작업실에만 손님을 보내요.')
    D.node('user', 8, 100, 100, 56, '사용자', None, 'users', k='손님')
    D.node('elb', 150, 100, 140, 56, 'ELB', 'DNS 이름 하나', 'lb', t='hl', k='안내 데스크', ksub='대표 번호 하나')
    D.node('t1', 360, 20, 192, 50, 'EC2 1', 'healthy', 'server', t='ok', k='작업실 1', ksub='괜찮아요')
    D.node('t2', 360, 103, 192, 50, 'EC2 2', 'healthy', 'server', t='ok', k='작업실 2', ksub='괜찮아요')
    D.node('t3', 360, 186, 192, 50, 'EC2 3', 'unhealthy · 제외', 'server', t='warn', k='작업실 3', ksub='대답 없음 · 빼기')
    D.edge('user', 'elb', '요청', k='손님')
    D.edge('elb', 't1', t='acc', sa=('r', 0.3))
    D.edge('elb', 't2', t='acc')
    D.edge('elb', 't3', '보내지 않음', k='안 보냄', t='bad', dash=True, sa=('b', 0.8), sb='l')
    D.text(8, 196, '상태 확인: GET /health', k="'괜찮아요?' 확인")
    return D


@reg('c08-alb')
def _():
    D = Diagram('c08-alb', w=600, at='대상 그룹',
                cap='ALB는 요청의 경로와 호스트 이름을 보고 서로 다른 대상 그룹(EC2, ECS 작업, Lambda)으로 보냅니다. 뒤의 대상은 사용자 IP를 X-Forwarded-For 헤더로 받습니다.',
                kcap='데스크는 주문서를 읽고 빵 작업실, 케이크 작업실, 배달 심부름꾼에게 나눠요. 작업실에는 "원래 손님" 메모가 함께 가요.')
    D.node('user', 8, 110, 100, 56, '사용자', None, 'users', k='손님')
    D.node('alb', 130, 90, 130, 96, 'ALB', 'HTTPS 443', 'lb', t='hl', k='주문서 데스크', ksub='정문')
    D.node('tg1', 330, 16, 262, 56, '대상 그룹: 사용자', 'EC2 인스턴스', 'server', k='빵 작업실들', ksub='빵 주문')
    D.node('tg2', 330, 110, 262, 56, '대상 그룹: 주문', 'ECS 작업 (컨테이너)', 'box', k='케이크 작업실들', ksub='케이크 주문')
    D.node('tg3', 330, 204, 262, 56, '대상 그룹: API', 'Lambda 함수', 'lambda', k='배달 심부름꾼', ksub='옆문 손님', kicon='user')
    D.edge('user', 'alb', t='acc')
    D.edge('alb', 'tg1', '/users*', k='빵', t='acc', sa=('r', 0.2))
    D.edge('alb', 'tg2', '/orders*', k='케이크', t='acc')
    D.edge('alb', 'tg3', 'Host: api', k='옆문', t='acc', sa=('r', 0.8))
    D.text(8, 290, '대상이 보는 출발지 = ALB IP → 사용자 IP는 X-Forwarded-For 헤더로', k='작업실에는 데스크 직원 얼굴만 보여요 → "원래 손님" 메모를 함께 줘요')
    return D


@reg('c08-nlb-gwlb')
def _():
    D = Diagram('c08-nlb-gwlb', w=560, at='end:NLB(Network Load Balancer)',
                cap='NLB는 AZ마다 고정 IP(탄력적 IP 가능)를 가져 고객사 방화벽에 등록할 수 있고, 대상으로 EC2뿐 아니라 ALB도 둘 수 있습니다.',
                kcap='번개 안내원은 동네마다 바뀌지 않는 문 번호가 있어요. 그 뒤에 주문서 데스크를 둘 수도 있어요.')
    D.node('cli', 8, 88, 110, 80, '고객사', '방화벽에 IP 등록', 'building', t='muted', k='단골 회사', ksub='번호 적어 둠')
    D.node('e1', 140, 30, 130, 52, 'AZ a 고정 IP', '3.34.10.1', k='가 동네 고정 문', ksub='10번 문')
    D.node('e2', 140, 174, 130, 52, 'AZ b 고정 IP', '3.34.20.1', k='나 동네 고정 문', ksub='20번 문')
    D.node('nlb', 304, 78, 110, 100, 'NLB', '4계층', 'lb', t='hl', k='번개 안내원', ksub='얼굴만 보고')
    D.node('ec2', 440, 30, 112, 52, 'EC2', 'TCP 대상', 'server', k='작업실', ksub='바로 연결')
    D.node('alb', 440, 166, 112, 80, 'ALB', '7계층', 'lb', k='주문서 데스크', ksub='내용 보고')
    D.edge('cli', 'e1')
    D.edge('cli', 'e2')
    D.edge('e1', 'nlb', t='acc')
    D.edge('e2', 'nlb', t='acc')
    D.edge('nlb', 'ec2', t='acc')
    D.edge('nlb', 'alb', t='acc')
    return D


@reg('c08-nlb-gwlb:gwlb')
def _():
    D = Diagram('c08-nlb-gwlb:gwlb', w=600, at='end:GWLB(Gateway Load Balancer)',
                cap='라우팅 테이블이 들어오는 트래픽을 GWLB 엔드포인트로 보내고(①), GWLB가 GENEVE(6081)로 보안 장비 중 하나에 맡깁니다(②). 장비를 통과한 트래픽만 앱으로 갑니다(③).',
                kcap='길 안내판이 모든 짐을 검사실 입구로 보내고(①), 안내원이 검사원에게 나눠 맡겨요(②). 검사를 통과한 짐만 작업실로 가요(③).')
    D.node('net', 8, 20, 110, 52, '인터넷', None, 'globe', t='muted', k='바깥')
    D.node('gwe', 150, 20, 160, 52, 'GWLB 엔드포인트', '라우팅 테이블이 보냄', k='검사실 입구', ksub='길 안내판이 보냄')
    D.node('gwlb', 350, 20, 120, 52, 'GWLB', '3계층', 'lb', t='hl', k='길 안내원', ksub='나눠 맡기기')
    D.group(300, 100, 292, 112, '보안 장비 (EC2)', k='검사원들', lpos='bl')
    D.node('f1', 312, 116, 84, 64, '장비 1', None, 'shield', k='검사원 1')
    D.node('f2', 404, 116, 84, 64, '장비 2', None, 'shield', k='검사원 2')
    D.node('f3', 496, 116, 84, 64, '장비 3', None, 'shield', k='검사원 3')
    D.node('app', 150, 150, 130, 56, '앱 (EC2)', '검사 통과분만', 'server', t='ok', k='작업실', ksub='통과한 짐만')
    D.edge('net', 'gwe', '①', t='acc')
    D.edge('gwe', 'gwlb', '②', t='acc')
    D.edge('gwlb', 'f2', 'GENEVE 6081', k='검사실로', t='acc')
    D.edge('gwlb', 'f1', t='n', dash=True)
    D.edge('gwlb', 'f3', t='n', dash=True, sa='r', sb='t')
    D.edge('f1', 'app', '③', t='ok')
    return D


@reg('c08-elb-features')
def _():
    D = Diagram('c08-elb-features', w=600, at='SSL/TLS 인증서와 SNI',
                cap='AZ A에 대상 2개, AZ B에 8개, 각 LB 노드가 50%씩 받는 경우입니다. 교차 영역을 켜면 모든 대상이 10%씩, 끄면 A의 대상은 25%씩, B의 대상은 6.25%씩 받습니다.',
                kcap='동네를 넘어 나누면 작업실 열 개가 똑같이 받고, 안 넘으면 작업실이 적은 동네가 훨씬 바빠요.')
    for p, (title, ktitle, on) in enumerate([('교차 영역 켜짐 (ALB 기본)', '동네 넘어 나누기', True), ('교차 영역 꺼짐 (NLB 기본)', '자기 동네만', False)]):
        x = 8 + p * 296
        D.group(x, 8, 288, 270, title, k=ktitle, solid=True)
        D.group(x + 10, 36, 128, 204, 'AZ A', k='동네 가', lpos='bl')
        D.group(x + 150, 36, 128, 204, 'AZ B', k='동네 나', lpos='bl')
        D.node(f'la{p}', x + 18, 64, 112, 50, 'LB 노드', '50%', k='데스크', ksub='손님 절반')
        D.node(f'lb{p}', x + 158, 64, 112, 50, 'LB 노드', '50%', k='데스크', ksub='손님 절반')
        D.node(f'ta{p}', x + 18, 160, 112, 56, '대상 2개', '각 10%' if on else '각 25%', t='ok' if on else 'warn', k='작업실 2개', ksub='각 10%' if on else '각 25%')
        D.node(f'tb{p}', x + 158, 160, 112, 56, '대상 8개', '각 10%' if on else '각 6.25%', t='ok', k='작업실 8개', ksub='각 10%' if on else '각 6.25%')
        D.edge(f'la{p}', f'ta{p}', t='acc')
        D.edge(f'lb{p}', f'tb{p}', t='acc')
        if on:
            D.edge(f'la{p}', f'tb{p}', t='acc', sa=('b', 0.8), sb=('t', 0.3), via=[(x + 107.6, 134), (x + 191.6, 134)])
            D.edge(f'lb{p}', f'ta{p}', t='acc', sa=('b', 0.2), sb=('t', 0.7), via=[(x + 180.4, 150), (x + 96.4, 150)])
        D.text(x + 14, 266, '모든 대상이 똑같이' if on else 'AZ마다 대상 수가 다르면 쏠림', k='열 곳이 똑같이' if on else '작업실 적은 동네가 바쁨')
    return D


@reg('c08-asg')
def _():
    D = Diagram('c08-asg', w=600, at='흐름',
                cap='CloudWatch 경보가 울리면(①) 조정 정책이 원하는 용량을 4에서 6으로 올리고(②), ASG가 시작 템플릿으로 두 AZ에 한 대씩 새 인스턴스를 띄워 대상 그룹에 등록합니다.',
                kcap='관제실 경보가 울리면(①) 매니저가 직원을 4명에서 6명으로 늘리고(②), 두 동네에 한 명씩 새 직원이 와요.')
    D.node('alarm', 8, 20, 150, 56, 'CloudWatch 경보', '평균 CPU > 70%', t='warn', k='관제실 경보', ksub='너무 바빠요')
    D.node('pol', 8, 120, 150, 56, '조정 정책', '원하는 4 → 6', 'gear', k='매니저 규칙', ksub='4명 → 6명')
    D.group(190, 8, 402, 250, 'Auto Scaling 그룹 (최소 2 · 원하는 6 · 최대 10)', k='직원 조절 매니저 (적어도 2 · 지금 6 · 많아도 10)')
    for j, (az, kaz) in enumerate([('가용 영역 a', '동네 가'), ('가용 영역 b', '동네 나')]):
        x = 202 + j * 194
        D.group(x, 40, 186, 186, az, k=kaz)
        D.node(f'o{j}0', x + 12, 66, 162, 42, 'EC2', '기존', 'server', k='직원', ksub='일하는 중')
        D.node(f'o{j}1', x + 12, 116, 162, 42, 'EC2', '기존', 'server', k='직원', ksub='일하는 중')
        D.node(f'n{j}', x + 12, 172, 162, 44, '새 EC2', '시작 템플릿', 'server', t='ok', k='새 직원', ksub='안내서대로 준비')
    D.edge('alarm', 'pol', '①', t='acc')
    D.edge('pol', 'n0', '② +2대', k='② +2명', t='acc')
    D.edge('pol', 'n1', t='acc', sa='b', sb='b', via=[(83, 240), (489, 240)])
    D.text(190, 282, '새 인스턴스 → ALB 대상 그룹에 자동 등록 → 상태 확인 통과 후 트래픽', k='새 직원은 안내 데스크 명단에 올라간 뒤 손님을 받아요')
    return D


@reg('c08-scaling')
def _():
    D = Diagram('c08-scaling', w=600, at='자주 쓰는 지표',
                cap='네 가지 조정 정책은 무엇을 보고(지표, 경보, 일정, 과거 패턴) 원하는 용량을 바꾸느냐가 다릅니다. 조정 뒤에는 휴지 기간 동안 다음 조정을 미룹니다.',
                kcap='매니저는 바쁨 정도, 경보, 달력, 지난 기록 중 하나를 보고 직원 수를 정해요.')
    rows = [('CloudWatch 지표', '평균 CPU 63%', '대상 추적', 'CPU 40% 유지', '바쁨 정도', '절반보다 바쁨', '목표 맞추기', '절반만 바쁘게'),
            ('CloudWatch 경보', 'CPU > 70%', '단계 조정', '+2대 / -1대', '경보', '너무 바빠요', '경보 따라 하기', '2명 더, 1명 빼기'),
            ('일정', '금 17:00', '예약 조정', '최소 10대로', '달력', '금요일 저녁', '달력 보고 미리', '10명으로'),
            ('과거 14일 패턴', '머신러닝 예측', '예측 조정', '미리 늘리기', '지난 기록', '매일 아침 9시', '기록 보고 예상', '미리 부르기')]
    for i, (a, asub, b, bsub, ka, kas, kb, kbs) in enumerate(rows):
        y = 12 + i * 72
        D.node(f's{i}', 8, y, 170, 52, a, asub, k=ka, ksub=kas)
        D.node(f'p{i}', 220, y, 170, 52, b, bsub, t='hl' if i == 0 else 'plain', k=kb, ksub=kbs)
        D.edge(f's{i}', f'p{i}')
    D.node('asg', 432, 70, 160, 140, 'ASG', '원하는 용량 변경', 'scale', t='ok', k='매니저', ksub='직원 수 정하기')
    for i in range(4):
        D.edge(f'p{i}', 'asg', t='acc', sb=('l', 0.15 + 0.233 * i))
    D.text(8, 316, '조정 뒤 휴지 기간(기본 300초) 동안 다음 조정 보류', k='새 직원이 익숙해질 때까지 5분 기다려요')
    return D


@reg('c09-rds')
def _():
    D = Diagram('c09-rds', w=600, at='스토리지 자동 확장',
                cap='RDS는 패치와 백업을 AWS가 맡는 관리형 DB입니다. 저장 공간이 거의 차면(남은 공간 10% 미만이 5분 이상, 마지막 변경 후 6시간 경과) 정한 최대 한도 안에서 자동으로 늘어납니다.',
                kcap='기록실은 관리인이 정리해요. 장부가 거의 차면 관리인이 정한 한도 안에서 페이지를 더 붙여요.')
    D.node('app', 8, 60, 120, 56, '앱 (EC2)', None, 'server', k='작업실')
    D.node('rds', 170, 40, 180, 96, 'RDS 인스턴스', 'AWS가 패치·백업', 'db', t='hl', k='기록실', ksub='관리인이 정리')
    D.edge('app', 'rds', 'SQL', k='기록')
    D.arrow((350, 88), (386, 88), t='n')
    D.text(390, 42, '할당 100 GiB', k='장부 100쪽')
    D.bar(390, 50, 200, 26, '', t='muted')
    D.bar(390, 50, 184, 26, '사용 92 GiB', k='92쪽 씀', t='warn')
    D.arrow((490, 82), (490, 120), t='acc')
    D.bar(390, 126, 200, 26, '110 GiB로 자동 확장', k='110쪽으로 늘어남', t='soft')
    D.text(390, 176, '최대 저장 공간 한도 500 GiB', k='붙일 수 있는 최대 500쪽')
    D.text(170, 210, '조건: 남은 공간 10% 미만이 5분 이상', k='조건: 빈 페이지 10% 미만이 5분 동안')
    D.text(170, 230, '그리고 마지막 변경 후 6시간 지남', k='그리고 마지막으로 붙인 지 6시간 지남')
    return D


@reg('c09-replica')
def _():
    D = Diagram('c09-replica', w=600, at='읽기 전용 복제본',
                cap='왼쪽: 읽기 전용 복제본은 비동기로 따라오며 읽기만 받고, 다른 리전에도 둘 수 있습니다. 오른쪽: 다중 AZ는 다른 AZ의 대기 DB에 동기로 쓰고, 장애 때 같은 DNS 이름이 대기 DB로 넘어갑니다.',
                kcap='왼쪽: 열람용 복사본은 조금 늦게 따라 적고 보기만 받아요. 오른쪽: 비상 기록실은 동시에 적어 두고, 불이 나면 간판이 바뀌어요.')
    D.group(8, 8, 288, 270, '읽기 전용 복제본 (확장)', k='열람용 복사본', solid=True)
    D.node('app1', 20, 36, 264, 44, '앱', '쓰기 → 주 DB, 읽기 → 복제본', 'server', k='손님들', ksub='적기는 원본, 보기는 복사본')
    D.node('p1', 20, 112, 110, 56, '주 DB', '읽기·쓰기', None, t='store', k='원본 장부', ksub='적고 보기')
    D.node('r1', 178, 112, 106, 56, '복제본 1', '같은 리전', None, k='복사본 1', ksub='같은 도시')
    D.node('r2', 178, 200, 106, 56, '복제본 2', '다른 리전', None, k='복사본 2', ksub='다른 도시')
    D.edge('app1', 'p1', '쓰기', k='적기')
    D.edge('app1', 'r1', '읽기', k='보기')
    D.edge('p1', 'r1', '비동기', k='늦게', t='acc')
    D.edge('p1', 'r2', '비동기(리전 간)', k='늦게(다른 도시)', t='acc', sa='b', sb='l')
    D.group(304, 8, 288, 270, '다중 AZ (가용성)', k='비상 기록실', solid=True)
    D.node('app2', 316, 36, 264, 44, '앱', '하나의 DNS 이름', 'server', k='손님들', ksub='간판 하나')
    D.group(316, 96, 128, 170, 'AZ a', k='동네 가', lpos='bl')
    D.group(452, 96, 128, 170, 'AZ b', k='동네 나', lpos='bl')
    D.node('p2', 326, 130, 100, 56, '주 DB', None, None, t='store', k='기록실')
    D.node('s2', 470, 130, 100, 56, '대기 DB', '읽기 불가', None, t='ok', k='비상 기록실', ksub='평소엔 안 봄')
    D.edge('app2', 'p2', '읽기·쓰기', k='적고 보기')
    D.edge('p2', 's2', '동기', k='같이', t='acc')
    D.edge('app2', 's2', '장애 시 자동 전환', k='불나면 간판 바뀜', t='ok', dash=True)
    return D


@reg('c09-aurora')
def _():
    D = Diagram('c09-aurora', w=600, at='클러스터와 엔드포인트',
                cap='주 인스턴스와 복제본은 3개 AZ에 걸친 하나의 공유 저장 볼륨(6벌)을 씁니다. 쓰기는 6벌 중 4벌, 읽기는 3벌이면 됩니다. 앱은 쓰기 엔드포인트와 읽기 엔드포인트만 알면 됩니다.',
                kcap='쓰는 사람과 읽는 사람들이 세 동네에 나눠 둔 여섯 권 장부를 함께 봐요. 넷에 적으면 끝, 셋이 맞으면 읽어요.')
    D.node('we', 60, 8, 180, 46, '쓰기 엔드포인트', '항상 주 인스턴스', t='hl', k='쓰기 창구', ksub='쓰는 사람에게')
    D.node('re', 360, 8, 200, 46, '읽기 엔드포인트', '연결 단위 분산', t='hl', k='읽기 창구', ksub='번갈아 연결')
    D.node('w', 60, 90, 180, 52, '주 인스턴스', '쓰기', 'db', k='쓰는 사람', ksub='장부에 적기')
    D.node('r1', 300, 90, 130, 52, '복제본 1', '읽기', 'db', k='읽는 사람 1')
    D.node('r2', 450, 90, 130, 52, '복제본 2', '읽기', 'db', k='읽는 사람 2')
    D.edge('we', 'w')
    D.edge('re', 'r1')
    D.edge('re', 'r2')
    D.group(8, 174, 584, 110, '공유 저장 볼륨 (자동 확장, 최대 128TiB)', k='여섯 권 장부 (저절로 늘어남)', t='store')
    for i, (az, kaz) in enumerate([('AZ a', '동네 가'), ('AZ b', '동네 나'), ('AZ c', '동네 다')]):
        x = 20 + i * 190
        D.group(x, 200, 180, 74, az, k=kaz)
        D.node(f'c{i}0', x + 10, 226, 76, 38, f'사본 {i * 2 + 1}', k=f'{i * 2 + 1}권', t='store')
        D.node(f'c{i}1', x + 94, 226, 76, 38, f'사본 {i * 2 + 2}', k=f'{i * 2 + 2}권', t='store')
    D.arrow((150, 142), (150, 172), t='acc')
    D.arrow((365, 142), (365, 172))
    D.arrow((515, 142), (515, 172))
    D.text(160, 162, '4/6에 쓰면 완료', k='넷에 적으면 끝')
    D.text(375, 162, '3/6이면 읽기', k='셋이면 읽기')
    D.text(8, 304, 'AZ 하나를 잃어도 4벌이 남아 쓰기·읽기 계속', k='한 동네가 정전돼도 네 권이 남아요')
    return D


@reg('c09-aurora-adv')
def _():
    D = Diagram('c09-aurora-adv', w=600, at='Aurora Global Database',
                cap='Global Database는 주 리전의 저장 볼륨을 보조 리전(최대 10개)으로 보통 1초 안에 복제합니다. 보조 리전은 가까운 사용자의 읽기를 받고, 재해 때 1분 안팎에 승격됩니다.',
                kcap='다른 도시 열 곳까지 1초 안에 따라 적는 사본을 둬요. 큰일이 나면 다른 도시 사본이 1분 만에 진짜 기록실이 돼요.')
    D.group(8, 8, 262, 200, '주 리전 (서울)', k='도시 가 (서울)')
    D.group(330, 8, 262, 200, '보조 리전 (도쿄) · 최대 10개', k='도시 나 (도쿄) · 열 곳까지')
    D.node('w', 20, 40, 238, 50, 'Aurora 쓰기 인스턴스', '읽기·쓰기', 'db', t='hl', k='쓰는 사람', ksub='읽고 쓰기')
    D.node('s1', 20, 124, 238, 60, '클러스터 저장 볼륨', '6벌', 'layers', t='store', k='여섯 권 장부', ksub='세 동네에')
    D.node('r', 342, 40, 238, 50, '읽기 전용 클러스터', '가까운 사용자 읽기', 'db', k='읽는 사람들', ksub='그 도시 손님용')
    D.node('s2', 342, 124, 238, 60, '저장 볼륨 사본', '6벌', 'layers', t='store', k='장부 사본', ksub='세 동네에')
    D.edge('w', 's1')
    D.edge('r', 's2')
    D.edge('s1', 's2', '복제 < 1초', k='1초 안에', t='acc')
    D.text(330, 232, '재해 시 보조 리전 승격 (RTO 약 1분)', k='큰일 나면 1분 만에 진짜가 돼요')
    return D


@reg('c09-ops')
def _():
    D = Diagram('c09-ops', w=600, at='백업',
                cap='위: 매일 자동 백업과 5분마다 저장되는 트랜잭션 로그로 보존 기간 안의 아무 시점으로 복원하며, 복원하면 새 DB가 생깁니다. 아래: 암호화되지 않은 DB는 스냅샷 → 암호화 복사 → 복원으로 암호화합니다.',
                kcap='위: 매일 밤 복사본과 5분마다 쪽지로 원하는 시각의 새 기록실을 만들어요. 아래: 자물쇠는 사진 찍고, 자물쇠 달린 사진으로 복사해서, 새 기록실을 지어 달아요.')
    D.group(4, 4, 592, 168, '자동 백업과 특정 시점 복원', k='매일 복사와 시간 되돌리기')
    D.node('snap', 16, 36, 156, 52, '매일 자동 백업', '백업 기간에 전체', 'calendar', k='매일 밤 복사', ksub='통째로')
    D.node('logs', 16, 106, 156, 52, '트랜잭션 로그', '5분마다 저장', 'log', k='5분마다 쪽지', ksub='바뀐 내용')
    D.node('pitr', 214, 66, 160, 64, '특정 시점 복원', '예: 14:32', 'clock', t='hl', k='그 시각으로', ksub='예: 2시 32분')
    D.node('newdb', 420, 66, 164, 64, '새 DB 인스턴스', '원래 DB는 그대로', 'db', t='ok', k='새 기록실', ksub='원래 것은 그대로')
    D.edge('snap', 'pitr')
    D.edge('logs', 'pitr')
    D.edge('pitr', 'newdb', '복원', k='새로', t='acc')
    D.group(4, 182, 592, 90, '암호화되지 않은 DB 암호화하기', k='자물쇠 나중에 달기')
    D.node('un', 16, 212, 124, 48, '암호화 안 된 DB', None, t='warn', k='자물쇠 없음')
    D.node('e1', 168, 212, 100, 48, '스냅샷', None, k='사진')
    D.node('e2', 296, 212, 130, 48, '암호화 복사', 'KMS 키', k='자물쇠 복사', ksub='열쇠 보관소')
    D.node('e3', 454, 212, 130, 48, '복원', '암호화된 새 DB', t='ok', k='새 기록실', ksub='자물쇠 달림')
    D.edge('un', 'e1', '①', t='acc')
    D.edge('e1', 'e2', '②', t='acc')
    D.edge('e2', 'e3', '③', t='acc')
    return D


@reg('c09-proxy')
def _():
    D = Diagram('c09-proxy', w=600, at='특징',
                cap='수백 개의 Lambda 연결을 RDS Proxy가 받아 적은 수의 DB 연결로 재사용합니다. 장애 조치 때 프록시가 새 주 DB로 연결을 옮기고, DB 자격 증명은 Secrets Manager에서 가져옵니다.',
                kcap='손님 수백 명의 전화를 교환원이 받아 전화선 몇 개로 기록실에 이어 줘요. 기록실이 바뀌어도 통화는 이어져요.')
    D.group(8, 8, 170, 236, 'Lambda 수백 개', k='손님 수백 명')
    for i in range(4):
        D.node(f'l{i}', 20, 40 + i * 48, 146, 40, 'Lambda', None, 'lambda', k='손님', kicon='user')
    D.node('proxy', 230, 80, 150, 90, 'RDS Proxy', '연결 풀 · IAM 인증', 'plug', t='hl', k='전화 교환원', ksub='전화선 나눠 쓰기')
    D.node('sec', 230, 200, 150, 52, 'Secrets Manager', 'DB 자격 증명', k='금고', ksub='기록실 비밀번호')
    D.node('db', 460, 40, 132, 56, 'RDS 주 DB', None, 'db', t='store', k='기록실')
    D.node('sb', 460, 150, 132, 56, '대기 DB', '장애 시 승격', 'db', t='ok', k='비상 기록실', ksub='불나면 바뀜')
    D.edge('l0', 'proxy', sb=('l', 0.15))
    D.edge('l1', 'proxy')
    D.edge('l2', 'proxy')
    D.edge('l3', 'proxy', sb=('l', 0.9))
    D.edge('proxy', 'db', '적은 연결', k='선 몇 개', t='acc', sa=('r', 0.3), lp=1)
    D.edge('proxy', 'sb', '전환', k='바꿔 연결', t='ok', dash=True, sa=('r', 0.7), lp=1)
    D.edge('sec', 'proxy', '자격 증명', k='비밀번호')
    return D


@reg('c09-elasticache')
def _():
    D = Diagram('c09-elasticache', w=600, at='캐시 전략',
                cap='지연 로딩: 앱은 먼저 캐시를 보고(①) 없으면(②) DB에서 읽은 뒤(③) 캐시에 넣습니다(④). 다음 요청부터는 캐시에서 바로 답합니다. 라이트 스루는 DB에 쓸 때 캐시에도 함께 씁니다.',
                kcap='먼저 메모판을 보고(①) 없으면(②) 기록실에서 찾아(③) 메모판에 붙여요(④). 다음 손님부터는 메모판에서 바로 알려 줘요.')
    D.node('app', 8, 90, 140, 84, '앱 (EC2)', None, 'server', k='작업실')
    D.node('cache', 300, 8, 180, 60, 'ElastiCache', '메모리 · 1ms 안팎', 'bolt', t='hl', k='책상 위 메모판', ksub='바로 읽기')
    D.node('db', 300, 196, 180, 60, 'RDS', '디스크 · 더 느림', 'db', t='store', k='기록실', ksub='멀어서 느림')
    D.edge('app', 'cache', '① 조회', k='① 메모판', t='acc', sa=('r', 0.2), sb=('l', 0.3))
    D.edge('cache', 'app', '② 없음', k='② 없음', t='bad', sa=('l', 0.75), sb=('r', 0.45), via=[(260, 53), (260, 127.8)])
    D.edge('app', 'db', '③ DB 읽기', k='③ 기록실', t='acc', sa=('r', 0.8), sb=('l', 0.5))
    D.edge('app', 'cache', '④ 캐시에 저장', k='④ 메모판에 붙이기', t='ok', sa=('t', 0.5), sb=('l', 0.5), via=[(78, 38)], lo=0.3)
    D.text(8, 292, '라이트 스루: DB에 쓸 때 캐시에도 함께 씀 · TTL로 오래된 항목 정리', k='적을 때 같이 적기: 기록실과 메모판에 함께 · 메모에 유효 기간')
    return D


@reg('c10-dns')
def _():
    D = Diagram('c10-dns', w=600, at='이름 하나를 찾는 순서',
                cap='브라우저가 로컬 DNS 서버에 묻고(①), 로컬 DNS 서버가 루트(②), TLD(③), 권한 있는 서버(④) 순서로 물어 최종 IP를 받아 돌려주며(⑤) TTL 동안 캐시합니다.',
                kcap='손님이 동네 안내원에게 묻고(①), 안내원이 중앙 안내소(②), 거리 안내소(③), 주인 주소록(④) 순서로 물어서 알려 줘요(⑤).')
    D.node('root', 8, 8, 170, 50, '루트 DNS', '"." 영역', 'globe', k='도시 중앙 안내소')
    D.node('tld', 215, 8, 170, 50, '.com TLD 서버', None, 'globe', k='빵집 거리 안내소')
    D.node('auth', 422, 8, 170, 56, '권한 있는 서버', 'Route 53 호스팅 영역', 'book', t='hl', k='주인 주소록', ksub='가게 주인이 적음')
    D.node('br', 8, 150, 120, 56, '브라우저', None, 'browser', k='손님')
    D.node('loc', 230, 150, 160, 56, '로컬 DNS 서버', '통신사·회사', 'router', k='동네 안내원', ksub='답을 잠깐 기억')
    D.edge('br', 'loc', '① 질문 · ⑤ 답', k='① 묻기 · ⑤ 답', t='acc', both=True)
    D.edge('loc', 'root', '②', both=True, sa=('t', 0.2), sb=('b', 0.7))
    D.edge('loc', 'tld', '③', both=True)
    D.edge('loc', 'auth', '④', t='acc', both=True)
    return D


@reg('c10-r53')
def _():
    D = Diagram('c10-r53', w=600, at='CNAME과 Alias',
                cap='하위 이름은 CNAME으로 ALB를 가리킬 수 있지만, 루트 도메인에는 CNAME을 만들 수 없습니다. Alias는 루트에도 되고 조회 요금이 없습니다. Alias는 EC2 DNS 이름을 가리키지 못합니다.',
                kcap='주문 창구 이름은 다른 이름을 적어도 되지만, 가게 대표 이름에는 안 돼요. 도시 시설 바로 연결은 대표 이름에도 되고 무료예요.')
    D.group(8, 8, 330, 262, '호스팅 영역 example.com', k='가게 주소록 (가나다빵집)')
    D.node('r1', 20, 40, 306, 56, 'app.example.com', 'CNAME → my-alb-1.elb.amazonaws.com', k='주문 창구 이름', ksub='다른 이름을 적음')
    D.node('r2', 20, 116, 306, 56, 'example.com (루트)', 'Alias A → ALB · 조회 무료', t='ok', k='대표 이름', ksub='도시 시설 바로 연결 · 무료')
    D.node('r3', 20, 196, 306, 56, 'example.com (루트)', 'CNAME → 만들 수 없음', t='warn', k='대표 이름', ksub='다른 이름 적기는 안 돼요')
    D.node('alb', 400, 80, 192, 64, 'ALB', 'IP가 바뀌는 리소스', 'lb', t='hl', k='안내 데스크', ksub='번지가 자주 바뀜')
    D.edge('r1', 'alb', 'CNAME', k='이름 적기')
    D.edge('r2', 'alb', 'Alias', k='바로 연결', t='ok')
    D.edge('r3', 'alb', '불가', k='안 돼요', t='bad', dash=True, sa='r', sb=('b', 0.3))
    D.text(8, 292, 'Alias는 EC2 DNS 이름을 가리킬 수 없음 → EC2는 A 레코드에 IP', k='작업실 이름에는 바로 연결을 못 써요 → 작업실은 번지를 적어요')
    return D


@reg('c10-routing')
def _():
    D = Diagram('c10-routing', w=600, at='가중치(Weighted)',
                cap='가중치 정책은 같은 이름의 레코드에 가중치(70, 20, 10)를 주고 그 비율대로 답을 나눕니다. 새 버전에 10%만 보내는 카나리 배포에 씁니다.',
                kcap='주소 안내소가 열 명 중 일곱은 본점, 둘은 도쿄 지점, 한 명은 새 지점 주소를 알려 줘요.')
    D.node('user', 8, 100, 110, 56, '사용자', 'DNS 질문', 'users', k='손님', ksub='주소 묻기')
    D.node('r53', 150, 90, 140, 76, 'Route 53', '가중치 정책', 'globe', t='hl', k='주소 안내소', ksub='비율대로')
    D.node('e1', 360, 16, 232, 52, '서울 ALB (가중치 70)', '70%', k='본점 (일곱 명)', ksub='열 명 중 7')
    D.node('e2', 360, 100, 232, 52, '도쿄 ALB (가중치 20)', '20%', k='도쿄 지점 (두 명)', ksub='열 명 중 2')
    D.node('e3', 360, 184, 232, 52, '새 버전 (가중치 10)', '10%', t='ok', k='새 지점 (한 명)', ksub='열 명 중 1')
    D.edge('user', 'r53')
    D.edge('r53', 'e1', '70%', k='7명', t='acc', sa=('r', 0.2))
    D.edge('r53', 'e2', '20%', k='2명', t='acc')
    D.edge('r53', 'e3', '10%', k='1명', t='acc', sa=('r', 0.8))
    return D


@reg('c10-health-failover')
def _():
    D = Diagram('c10-health-failover', w=600, at='장애 조치 라우팅(Failover, 액티브-패시브)',
                cap='상태 확인기가 기본(서울) 엔드포인트의 실패를 감지하면(①) Route 53은 기본 레코드를 답에서 빼고 보조(도쿄)로 답합니다(②). 프라이빗 리소스는 CloudWatch 경보 기반 상태 확인을 씁니다.',
                kcap='전화 확인반이 본점이 전화를 안 받는 걸 알면(①) 안내소는 비상 지점 주소를 알려 줘요(②).')
    D.node('hc', 180, 8, 240, 50, 'Route 53 상태 확인', '30초마다 /health', 'heart', k='전화 확인반', ksub='30초마다 전화')
    D.node('r53', 8, 116, 150, 80, 'Route 53', '장애 조치 정책', 'globe', t='hl', k='주소 안내소', ksub='본점 → 비상 지점')
    D.node('pri', 230, 110, 170, 60, '기본: 서울 ALB', 'unhealthy', 'lb', t='warn', k='본점', ksub='전화 안 받음')
    D.node('sec', 430, 110, 162, 60, '보조: 도쿄 ALB', 'healthy', 'lb', t='ok', k='비상 지점', ksub='괜찮아요')
    D.node('user', 8, 232, 150, 46, '사용자', None, 'users', k='손님')
    D.edge('hc', 'pri', '① 3번 연속 실패', k='① 세 번 안 받음', t='bad')
    D.edge('r53', 'pri', '답에서 뺌', k='주소 빼기', t='bad', dash=True)
    D.edge('r53', 'sec', '② 보조로 답', k='② 비상 지점 알려 줌', t='ok', sa=('b', 0.6), sb='b', via=[(98, 206), (511, 206)])
    D.edge('user', 'r53')
    D.text(180, 300, '프라이빗 리소스: CloudWatch 경보 기반 상태 확인', k='단지 안쪽 가게: 관제실 경보를 보고 판단')
    return D


@reg('c10-geo')
def _():
    D = Diagram('c10-geo', w=600, at='지리적 위치(Geolocation)',
                cap='지리적 위치 정책은 사용자의 국가로 답을 고릅니다. 한국 사용자는 서울, 프랑스 사용자는 파리로 가고, 규칙에 없는 나라의 사용자는 기본 레코드로 갑니다.',
                kcap='손님이 사는 나라를 보고 지점을 알려 줘요. 정해진 나라가 아니면 기본 지점으로 보내요.')
    D.node('kr', 8, 20, 130, 50, '한국 사용자', None, None, k='우리나라 손님')
    D.node('fr', 8, 100, 130, 50, '프랑스 사용자', None, None, k='프랑스 손님')
    D.node('br', 8, 180, 130, 50, '브라질 사용자', '규칙 없음', None, k='브라질 손님', ksub='정해진 게 없음')
    D.node('r53', 200, 86, 140, 80, 'Route 53', '지리적 위치', 'globe', t='hl', k='주소 안내소', ksub='사는 나라 보고')
    D.node('ekr', 400, 20, 192, 50, '서울 리전', '한국어 사이트', 'server', k='서울 지점', ksub='한국어')
    D.node('efr', 400, 100, 192, 50, '파리 리전', '프랑스어 사이트', 'server', k='파리 지점', ksub='프랑스어')
    D.node('edf', 400, 180, 192, 50, '기본 레코드', '영어 사이트', 'server', t='muted', k='기본 지점', ksub='영어')
    D.edge('kr', 'r53', sb=('l', 0.2))
    D.edge('fr', 'r53')
    D.edge('br', 'r53', sb=('l', 0.8))
    D.edge('r53', 'ekr', 'KR', k='우리나라', t='acc', sa=('r', 0.2))
    D.edge('r53', 'efr', 'FR', k='프랑스', t='acc')
    D.edge('r53', 'edf', '기본', k='그 밖', t='acc', sa=('r', 0.8))
    return D


@reg('c10-resolver')
def _():
    D = Diagram('c10-resolver', w=600, at='Route 53 Resolver와 하이브리드 DNS',
                cap='회사 DNS 서버는 인바운드 엔드포인트로 AWS 프라이빗 이름을 묻고(①②), VPC의 EC2가 회사 이름을 물으면(③) Resolver가 전달 규칙에 따라 아웃바운드 엔드포인트로 회사 DNS에 넘깁니다(④⑤).',
                kcap='본사 안내원은 들어오는 창구로 단지 주소를 묻고(①②), 단지 작업실이 본사 주소를 물으면(③) 단지 안내원이 나가는 창구로 본사에 넘겨요(④⑤).')
    D.group(8, 8, 200, 262, '회사 데이터 센터', k='본사 건물')
    D.node('ondns', 20, 40, 176, 56, '회사 DNS 서버', 'corp.company', 'router', k='본사 안내원', ksub='본사 사무실 주소')
    D.node('srv', 20, 170, 176, 56, '사내 서버', 'AWS 이름 질문', 'server', k='본사 직원', ksub='단지 주소 질문')
    D.group(260, 8, 332, 262, 'VPC', k='우리 단지')
    D.node('inb', 272, 40, 156, 56, '인바운드 엔드포인트', None, k='들어오는 창구')
    D.node('outb', 272, 170, 170, 56, '아웃바운드 엔드포인트', None, k='나가는 창구')
    D.node('res', 460, 96, 120, 76, 'Resolver', 'VPC +2 주소', 'router', t='hl', k='단지 안내원', ksub='단지 주소 담당')
    D.node('ec2', 460, 214, 120, 48, 'EC2', '회사 이름 질문', None, k='작업실', ksub='본사 주소 질문')
    D.edge('srv', 'ondns', '질문', k='묻기')
    D.edge('ondns', 'inb', '① 전달', k='① 넘김', t='acc', sa=('r', 0.3), sb=('l', 0.3))
    D.edge('inb', 'res', '②', t='acc')
    D.edge('ec2', 'res', '③', t='ok')
    D.edge('res', 'outb', '④', t='ok', sa=('b', 0.2), sb='r')
    D.edge('outb', 'ondns', '⑤ 전달', k='⑤ 넘김', t='ok', sb=('r', 0.75))
    return D
