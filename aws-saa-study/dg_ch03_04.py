from dg import Diagram, reg


@reg('c03-global')
def _():
    D = Diagram('c03-global', w=600, at='리전',
                cap='리전 안에 가용 영역이 여러 개 있고, AZ 하나는 하나 이상의 데이터 센터입니다. 엣지 로케이션은 리전 밖에서 사용자 가까이 캐시·DNS·가속 입구 역할을 합니다. IAM, Organizations, Route 53, CloudFront는 리전을 고르지 않는 글로벌 서비스입니다.',
                kcap='도시 안에 전기가 따로인 동네가 여러 개 있고, 동네마다 건물이 있어요. 골목 편의점은 손님 가까이 있고, 출입증 창구나 주소 안내소는 모든 도시가 함께 써요.')
    D.group(8, 8, 404, 232, '리전 (서울 ap-northeast-2)', k='도시 (서울)')
    azs = [('a', 20, '가'), ('b', 148, '나'), ('c', 276, '다')]
    for name, x, kn in azs:
        D.group(x, 40, 124, 188, f'AZ 2{name}', k=f'동네 {kn}')
        D.node(f'dc{name}1', x + 9, 66, 106, 64, '데이터 센터', None, 'building', k='건물')
        if name != 'c':
            D.node(f'dc{name}2', x + 9, 148, 106, 64, '데이터 센터', None, 'building', k='건물')
    D.edge('dca1', 'dcb1', both=True)
    D.edge('dcb1', 'dcc1', both=True)
    D.text(20, 258, 'AZ끼리는 고속·저지연 전용망으로 연결, 정전·홍수는 함께 번지지 않음',
           k='동네끼리는 빠른 전용 도로로 이어져 있고, 정전은 옮겨 가지 않아요')
    D.group(424, 8, 168, 232, '엣지 로케이션', k='골목 편의점')
    D.node('e1', 434, 40, 148, 50, '콘텐츠 캐시', 'CloudFront', k='인기 물건 진열', ksub='손님 가까이')
    D.node('e2', 434, 100, 148, 50, 'DNS 응답', 'Route 53', k='주소 알려 주기', ksub='가까운 곳에서')
    D.node('e3', 434, 160, 148, 62, '가속 입구', 'Global Accelerator', k='빠른 입구', ksub='전용 도로로')
    D.group(8, 276, 584, 72, '글로벌 서비스 (콘솔 리전 표시: Global)', k='모든 도시가 함께 쓰는 시설')
    D.node('g1', 20, 302, 110, 36, 'IAM', k='출입증 창구')
    D.node('g2', 140, 302, 150, 36, 'Organizations', k='본사')
    D.node('g3', 300, 302, 130, 36, 'Route 53', k='주소 안내소')
    D.node('g4', 440, 302, 140, 36, 'CloudFront', k='편의점 본부')
    return D


@reg('c04-iam')
def _():
    D = Diagram('c04-iam', w=560, at='사용자와 그룹',
                cap='정책은 그룹에 붙이고 사용자는 그룹에 넣습니다. 지연처럼 두 그룹에 속한 사용자는 두 그룹의 권한을 모두 받습니다. 루트 사용자는 그룹 밖에서 MFA로 따로 보호합니다.',
                kcap='규칙표는 부서에 붙이고 직원은 부서에 넣어요. 지연이는 두 부서에 속해서 두 규칙표를 다 받아요. 사장님 만능 열쇠는 따로 지문으로 잠가요.')
    D.group(8, 8, 544, 320, 'AWS 계정', k='우리 가게')
    D.node('root', 20, 36, 200, 52, '루트 사용자', '모든 권한 · MFA 필수', 'user', t='warn', k='사장님', ksub='만능 열쇠 · 지문 잠금')
    D.node('u1', 20, 110, 130, 44, '민수', 'IAM 사용자', 'user', k='민수', ksub='직원 출입증')
    D.node('u2', 20, 172, 130, 44, '지연', 'IAM 사용자', 'user', k='지연', ksub='직원 출입증')
    D.node('u3', 20, 234, 130, 44, '서준', 'IAM 사용자', 'user', k='서준', ksub='직원 출입증')
    D.node('g1', 226, 110, 136, 56, '개발팀', 'IAM 그룹', 'users', t='hl', k='주방 부서', ksub='부서')
    D.node('g2', 226, 222, 136, 56, '운영팀', 'IAM 그룹', 'users', t='hl', k='청소 부서', ksub='부서')
    D.node('p1', 400, 110, 148, 56, '개발 정책', 'EC2, S3 사용', 'policy', t='store', k='주방 규칙표', ksub='주방, 창고')
    D.node('p2', 400, 222, 148, 56, '운영 정책', 'CloudWatch 보기', 'policy', t='store', k='청소 규칙표', ksub='복도, 화장실')
    D.edge('u1', 'g1', '소속', sa='r', sb=('l', 0.3))
    D.edge('u2', 'g1', sa='r', sb=('l', 0.75))
    D.edge('u2', 'g2', sa='r', sb=('l', 0.25))
    D.edge('u3', 'g2', sa='r', sb=('l', 0.7))
    D.edge('p1', 'g1', '붙임', t='acc')
    D.edge('p2', 'g2', '붙임', t='acc')
    D.text(20, 306, '지연 = 개발 정책 + 운영 정책 (두 그룹의 권한을 합침)', k='지연이 = 주방 규칙 + 청소 규칙 (두 부서 규칙을 합쳐요)')
    return D


@reg('c04-policy')
def _():
    D = Diagram('c04-policy', w=560, at='평가 규칙 세 줄',
                cap='요청의 누가·무엇을·어디에·조건이 정책 문장의 대상·Action·Resource·Condition과 모두 맞고, 어디에도 Deny가 없을 때만 허용됩니다.',
                kcap='부탁의 네 칸이 규칙표 한 줄의 네 칸과 모두 맞고, 어디에도 금지 줄이 없을 때만 들어갈 수 있어요.')
    D.group(8, 8, 256, 250, '요청 (API 호출)', k='부탁')
    D.group(296, 8, 256, 250, '정책 문장 (Statement)', k='출입 규칙표 한 줄')
    rows = [('누가', '민수', '붙은 대상', '민수의 정책', '누가', '민수', '누구 규칙표', '민수 출입증'),
            ('무엇을', 's3:GetObject', 'Action', 's3:GetObject', '무엇을', '꺼내기', '할 수 있는 일', '꺼내기'),
            ('어디에', 'company-reports/report.pdf', 'Resource', 'arn:aws:s3:::company-reports/*', '어디서', '보고서 창고의 물건', '장소', '보고서 창고 안 전부'),
            ('조건', '출발지 IP 203.0.113.7', 'Condition', 'aws:SourceIp 203.0.113.0/24', '조건', '회사 안에서', '조건', '회사 주소 범위')]
    for i, (l, s, r, rs, kl, ks, kr, krs) in enumerate(rows):
        y = 40 + i * 54
        D.node(f'l{i}', 20, y, 232, 44, l, s, k=kl, ksub=ks)
        D.node(f'r{i}', 308, y, 232, 44, r, rs, k=kr, ksub=krs)
        D.edge(f'l{i}', f'r{i}', '일치', k='맞음', t='ok')
    D.node('res', 330, 280, 210, 48, '허용 (Allow)', 'Deny 문장이 없을 때', 'check', t='ok', k='들어가도 돼', ksub='금지 줄이 없으면')
    D.edge('r3', 'res', t='ok')
    return D


@reg('c04-cli')
def _():
    D = Diagram('c04-cli', w=560, at='무엇으로 로그인하나',
                cap='콘솔, CLI, SDK, CloudShell은 모두 같은 AWS API를 부릅니다. 차이는 누구인지 증명하는 방법입니다.',
                kcap='안내 창구, 무전기, 로봇 직원 모두 같은 관리실에 부탁해요. 누구인지 증명하는 방법만 달라요.')
    D.node('who', 8, 92, 130, 80, '사람·프로그램', None, 'users', k='가게 사람들')
    D.node('con', 176, 20, 180, 52, '관리 콘솔', '비밀번호 + MFA', 'browser', k='안내 창구', ksub='출입증 + 휴대폰')
    D.node('cli', 176, 106, 180, 52, 'AWS CLI', '액세스 키', 'terminal', k='무전기', ksub='비밀 번호표')
    D.node('sdk', 176, 192, 180, 52, 'SDK (코드)', '액세스 키 또는 역할', 'file', k='로봇 직원', ksub='번호표나 방문증')
    D.node('cs', 176, 278, 180, 52, 'CloudShell', '로그인 권한 그대로', 'terminal', t='muted', k='창구 옆 무전기', ksub='출입증 그대로')
    D.node('api', 400, 106, 152, 52, 'AWS API', '서비스 엔드포인트', 'api', t='hl', k='관리실', ksub='모든 부탁이 모임')
    for n in ('con', 'cli', 'sdk', 'cs'):
        D.edge('who', n)
        D.edge(n, 'api', t='acc')
    return D


@reg('c04-role')
def _():
    D = Diagram('c04-role', w=600, at='요청 하나의 흐름',
                cap='EC2에 역할을 붙이면 앱은 STS에서 몇 시간짜리 임시 자격 증명을 받아(①②) S3를 읽습니다(③). 장기 액세스 키를 코드에 넣는 방식은 키가 새면 계속 악용되므로 쓰지 않습니다.',
                kcap='작업실에 방문증을 걸어 두면 로봇은 창구에서 몇 시간짜리 방문증을 받아(①②) 창고에서 물건을 꺼내요(③). 번호표를 몸에 붙여 두면 누가 떼어 가도 계속 쓸 수 있어요.')
    D.node('role', 8, 8, 170, 52, 'IAM 역할', 'S3 읽기만 허용', 'badge', k='방문증', ksub='창고 꺼내기만')
    D.node('sts', 230, 8, 160, 52, 'STS', '임시 자격 증명 발급', 'key', k='방문증 창구', ksub='몇 시간짜리 발급')
    D.node('ec2', 8, 110, 170, 60, 'EC2 + 앱', '인스턴스 프로파일', 'server', t='hl', k='작업실 로봇', ksub='방문증 걸어 둠')
    D.node('s3', 430, 110, 160, 60, 'S3 버킷', '보고서', 'bucket', t='store', k='창고', ksub='보고서')
    D.node('bad', 8, 222, 220, 52, '액세스 키를 코드에 저장', '새어 나가면 계속 쓰임', 'key', t='warn', k='번호표를 몸에 붙이기', ksub='떼어 가면 끝')
    D.edge('role', 'ec2', '붙이기', k='걸어 두기')
    D.edge('ec2', 'sts', '①② 임시 키 받기', k='①② 방문증 받기', t='acc', both=True, sa=('r', 0.25))
    D.edge('ec2', 's3', '③ 임시 키로 읽기', k='③ 방문증으로 꺼내기', t='acc')
    D.edge('bad', 's3', '쓰지 말 것', k='이러면 안 돼요', t='bad', dash=True, sa='r', sb='b')
    return D
