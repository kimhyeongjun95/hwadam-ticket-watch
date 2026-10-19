from dg import Diagram, reg


@reg('start-terms')
def _():
    D = Diagram('start-terms', w=600, at='end:한 장으로 보는 용어 지도',
                cap='요청은 Route 53으로 주소를 찾고(①) CloudFront 엣지를 거쳐(②) 리전의 ALB로 들어가(③) 두 AZ의 EC2에 나뉘고(④) RDS 주 DB에 기록됩니다(⑤). 주 DB는 다른 AZ의 대기 DB로 동기 복제됩니다. IAM과 Route 53, CloudFront는 리전 밖의 글로벌 서비스입니다.',
                kcap='손님은 주소 안내소에서 위치를 묻고(①) 동네 편의점에 들렀다가(②) 도시 안 우리 단지의 안내 데스크로 가요(③). 안내 데스크가 두 동네의 작업실로 나눠 보내고(④) 작업실은 기록실에 적어요(⑤).')
    D.node('user', 8, 8, 120, 46, '사용자', '브라우저', 'user', k='손님', ksub='집에서')
    D.node('r53', 158, 8, 132, 46, 'Route 53', 'DNS', 'globe', k='주소 안내소', ksub='위치 알려 줌')
    D.node('cf', 300, 8, 140, 46, 'CloudFront', '엣지 캐시', 'cloud', k='동네 편의점', ksub='인기 물건')
    D.node('iam', 450, 8, 142, 46, 'IAM', '권한 · 글로벌', 'idcard', k='출입증 창구', ksub='도시 전체')
    D.group(8, 92, 584, 312, '리전 (예: 서울)', k='도시 (예: 서울)')
    D.group(20, 120, 420, 276, 'VPC', k='우리 단지')
    D.node('alb', 150, 146, 180, 44, 'ALB', '로드 밸런서', 'lb', k='안내 데스크', ksub='손님 나누기')
    D.group(32, 204, 196, 184, '가용 영역 A', k='동네 A', lpos='bl')
    D.group(240, 204, 196, 184, '가용 영역 B', k='동네 B', lpos='bl')
    D.node('ec2a', 44, 234, 162, 46, 'EC2', '웹 서버', 'server', k='작업실', ksub='손님 맞이')
    D.node('ec2b', 262, 234, 162, 46, 'EC2', '웹 서버', 'server', k='작업실', ksub='손님 맞이')
    D.node('rdsa', 44, 306, 150, 48, 'RDS', '주 DB', 'db', t='store', k='기록실', ksub='진짜 장부')
    D.node('rdsb', 274, 306, 150, 48, 'RDS', '대기 DB', 'db', t='store', k='비상 기록실', ksub='따라 적기')
    D.node('s3', 446, 146, 140, 56, 'S3', '정적 파일', 'bucket', t='store', k='큰 창고', ksub='짐 보관')
    D.node('cw', 446, 222, 140, 56, 'CloudWatch', '지표 · 경보', 'chart', k='관제실', ksub='계기판')
    D.edge('user', 'r53', '①', t='acc')
    D.edge('user', 'cf', '② 요청', k='② 방문', t='acc', sa=('b', 0.5), sb=('b', 0.25), via=[(68, 72), (335, 72)], lp=1)
    D.edge('cf', 'alb', '③ 원본 요청', k='③ 주문 전달', t='acc', sa=('b', 0.75), sb='t', via=[(405, 108), (240, 108)], lp=1)
    D.edge('cf', 's3', None, sa=('b', 0.95), sb='t', via=[(433, 114), (516, 114)])
    D.edge('alb', 'ec2a', '④ 분산', k='④ 나누기', t='acc')
    D.edge('alb', 'ec2b')
    D.edge('ec2a', 'rdsa', '⑤', t='acc')
    D.edge('rdsa', 'rdsb', '동기 복제', k='똑같이 적기')
    return D


@reg('start-terms:legend')
def _():
    D = Diagram('start-terms:legend', w=560,
                cap='상자 색은 역할을, 선 색은 흐름의 종류를 뜻합니다. 점선 테두리는 리전, VPC, 서브넷 같은 범위입니다.',
                kcap='상자 색은 하는 일을, 선 색은 무엇이 오가는지를 알려 줘요. 점선 울타리는 도시, 단지 같은 범위예요.')
    rows = [('plain', 'AWS 서비스·자원', '기본 상자', 'server', '도시 시설', '기본 상자'),
            ('hl', '이 그림의 주인공', '먼저 볼 것', 'badge', '주인공', '먼저 볼 것'),
            ('store', '데이터를 담는 곳', 'DB, 버킷', 'db', '보관하는 곳', '장부, 창고'),
            ('ok', '정상·허용·대기', '건강함', 'check', '괜찮은 것', '건강함'),
            ('warn', '장애·거부·위험', '고장 남', 'warn', '문제 생김', '고장 남'),
            ('muted', '바깥 세계·선택', '회사, 인터넷', 'building', '도시 밖', '우리 회사 건물')]
    for i, (t, lbl, sub, icon, k, ksub) in enumerate(rows):
        D.node(f'n{i}', 12, 12 + i * 50, 196, 42, lbl, sub, icon, t=t, k=k, ksub=ksub)
    flows = [('n', False, '요청·데이터 흐름', '물건이 가는 길'), ('acc', False, '순서가 있는 핵심 흐름', '중요한 길'),
             ('ok', False, '허용·성공', '통과'), ('bad', False, '거부·실패', '막힘'), ('n', True, '비동기·나중에·대기', '나중에 가는 길')]
    for i, (t, dash, lbl, k) in enumerate(flows):
        y = 33 + i * 46
        D.arrow((240, y), (318, y), t=t, dash=dash)
        D.text(330, y + 5, lbl, k=k, cls='sub')
    D.group(240, 248, 308, 52, '범위(리전, VPC, 서브넷)', k='범위(도시, 단지, 구역)')
    return D


@reg('start-exam')
def _():
    D = Diagram('start-exam', w=560, at='end:출제 영역과 비중',
                cap='막대 길이는 영역 비중에 비례합니다. 문항 수는 채점되는 50문항을 비중대로 나눈 대략의 값입니다.',
                kcap='막대가 길수록 그 과목 문제가 많아요. 지키기 문제가 가장 많아요.')
    rows = [('1. 보안', '1. 지키기', 30, 15, 'acc'), ('2. 복원력', '2. 버티기', 26, 13, 'soft'),
            ('3. 고성능', '3. 빠르게', 24, 12, 'soft'), ('4. 비용 최적화', '4. 아끼기', 20, 10, 'soft')]
    for i, (lbl, k, pct, n, t) in enumerate(rows):
        y = 14 + i * 46
        D.text(12, y + 22, lbl, k=k, cls='lbl')
        D.bar(140, y, pct * 13.6, 32, f'{pct}% · 약 {n}문항', t=t)
    D.text(140, 206, '채점 50문항 + 비채점 15문항 = 65문항, 130분', k='진짜 문제 50개 + 연습 문제 15개 = 65개, 130분')
    return D


@reg('start-lab')
def _():
    D = Diagram('start-lab', w=560, at='계정을 만들면 바로 할 일',
                cap='실습 계정은 만들자마자 루트 보호(①), 작업용 사용자(②), 예산 알림(③)을 차례로 걸고, 한 리전에서 실습한 뒤(④) 켜 둔 자원을 지웁니다.',
                kcap='가게 카드를 만들면 만능 열쇠를 잠그고(①), 직원 출입증을 만들고(②), 지출 알림을 건 다음(③) 일을 시작해요(④). 끝나면 빌린 것을 돌려줘요.')
    D.node('acct', 8, 8, 160, 52, '계정 만들기', '이메일·카드 등록', 'user', k='가게 등록', ksub='카드 연결')
    D.node('mfa', 200, 8, 160, 52, '① 루트 MFA', '만능 열쇠 보호', 'lock', t='hl', k='① 지문 잠금', ksub='만능 열쇠')
    D.node('iamu', 392, 8, 160, 52, '② IAM 사용자', '일상 작업용', 'idcard', k='② 직원 출입증', ksub='매일 쓰기')
    D.node('bud', 392, 100, 160, 52, '③ 예산 알림', 'AWS Budgets', 'dollar', k='③ 지출 알림', ksub='한도 정하기')
    D.node('lab', 200, 100, 160, 52, '④ 실습', '한 리전에서', 'terminal', k='④ 일하기', ksub='한 도시에서')
    D.node('clean', 8, 100, 160, 52, '정리', '켜 둔 자원 삭제', 'trash', t='warn', k='돌려주기', ksub='빌린 것 반납')
    D.edge('acct', 'mfa', t='acc')
    D.edge('mfa', 'iamu', t='acc')
    D.edge('iamu', 'bud', t='acc')
    D.edge('bud', 'lab', t='acc')
    D.edge('lab', 'clean', t='acc')
    return D
