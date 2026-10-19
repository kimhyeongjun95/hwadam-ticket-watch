from dg import Diagram, reg


@reg('c17-sqs')
def _():
    D = Diagram('c17-sqs', w=600, at='가시성 제한 시간(Visibility Timeout)',
                cap='생산자는 메시지를 넣고 바로 다음 일로 갑니다. 소비자 여럿이 대기열에서 메시지를 나눠 가져가 처리하고 지웁니다. 정한 횟수 넘게 실패한 메시지는 DLQ로 옮겨집니다.',
                kcap='홀 직원은 주문서를 꽂고 다음 손님에게 가요. 요리사 여럿이 나눠 빼 가서 요리하고 버려요. 계속 실패하는 주문서는 따로 모아요.')
    D.node('p1', 8, 30, 120, 52, '생산자', '주문 서비스', 'server', k='홀 직원', ksub='주문 받기')
    D.node('p2', 8, 110, 120, 52, '생산자', 'S3·SNS 등', 'bolt', k='다른 가게', ksub='알림 보내기')
    D.node('q', 190, 50, 190, 92, 'SQS 대기열', '최대 14일 보관 · 1MiB', 'queue', t='hl', k='주문서 꽂이', ksub='최대 14일 보관')
    D.node('c1', 450, 8, 142, 52, '소비자', 'EC2', 'server', k='요리사', ksub='주방 1')
    D.node('c2', 450, 70, 142, 52, '소비자', 'Lambda', 'lambda', k='요리사', ksub='주방 2', kicon='user')
    D.node('c3', 450, 132, 142, 52, '소비자', '온프레미스', 'building', k='요리사', ksub='다른 건물')
    D.node('dlq', 190, 196, 190, 52, 'DLQ', '정한 횟수 넘게 실패', t='warn', k='처리 못 한 바구니', ksub='계속 실패한 주문서')
    D.edge('p1', 'q', t='acc', sb=('l', 0.3))
    D.edge('p2', 'q', t='acc', sb=('l', 0.8))
    D.edge('q', 'c1', t='acc', sa=('r', 0.2), sb='l')
    D.edge('q', 'c2', '폴링', k='빼 가기', t='acc')
    D.edge('q', 'c3', t='acc', sa=('r', 0.8), sb='l')
    D.edge('q', 'dlq', '계속 실패', k='계속 실패', t='bad', dash=True)
    D.text(8, 280, 'SendMessage → ReceiveMessage(폴링, 최대 10개) → 처리 → DeleteMessage',
           k='꽂기 → 빼 가기(한 번에 10장까지) → 요리 → 버리기')
    return D


@reg('c17-sqs:vis')
def _():
    D = Diagram('c17-sqs:vis', w=560, at='end:가시성 제한 시간(Visibility Timeout)',
                cap='소비자 A가 받은 메시지는 30초 동안 다른 소비자에게 보이지 않습니다. 30초 안에 지우면 끝이고, 처리가 더 걸리면 메시지가 다시 보여 소비자 B가 또 처리합니다.',
                kcap='요리사가 주문서를 30초 뒤집어 둬요. 그 안에 끝내면 버리고, 더 걸리면 주문서가 다시 보여 다른 요리사가 또 만들어요.')
    D.text(8, 20, '① 30초 안에 처리', k='① 30초 안에 요리 끝', cls='lbl')
    D.text(8, 51, '소비자 A', k='요리사 가')
    D.bar(110, 30, 240, 30, '처리 중 · 남에게 안 보임', k='요리 중 · 뒤집어 둠', t='soft')
    D.bar(352, 30, 100, 30, '지움', k='버리기', t='ok')
    D.text(8, 98, '② 처리가 30초를 넘으면', k='② 30초 넘게 걸리면', cls='lbl')
    D.text(8, 129, '소비자 A', k='요리사 가')
    D.bar(110, 108, 240, 30, '처리 중 · 안 보임', k='요리 중 · 뒤집어 둠', t='soft')
    D.bar(352, 108, 200, 30, '아직 처리 중', k='아직 요리 중', t='warn')
    D.text(8, 165, '소비자 B', k='요리사 나')
    D.bar(352, 144, 200, 30, '다시 보여 또 처리', k='또 만들기 → 두 번', t='warn')
    D.arrow((110, 194), (552, 194))
    D.text(110, 214, '0초', k='0초')
    D.text(350, 214, '30초', k='30초', anchor='middle')
    D.text(8, 244, '해결: 가시성 제한 시간을 처리 시간보다 길게, 또는 ChangeMessageVisibility로 연장',
           k='해결: 뒤집어 두는 시간을 넉넉히, 또는 "시간 더 주세요"')
    return D


@reg('c17-fifo')
def _():
    D = Diagram('c17-fifo', w=600,
                cap='메시지 그룹마다 들어온 순서대로 나가고, 그룹끼리는 서로 다른 소비자가 병렬로 처리합니다. 5분 안에 같은 중복 제거 ID로 다시 온 메시지는 버려집니다.',
                kcap='김씨 줄, 이씨 줄을 따로 세워 각 줄은 차례대로 나가요. 5분 안에 또 온 같은 주문서는 버려요.')
    D.node('p', 8, 60, 110, 64, '생산자', None, 'server', k='홀 직원')
    D.arrow((118, 92), (158, 92), t='acc')
    D.group(160, 8, 290, 200, 'orders.fifo', k='줄 서기 꽂이', solid=True)
    D.text(176, 46, '그룹 A (고객 A)', k='김씨 줄')
    for j, s in enumerate(['A3', 'A2', 'A1']):
        D.bar(176 + j * 64, 54, 60, 30, s, k=['김3', '김2', '김1'][j], t='soft')
    D.text(176, 112, '그룹 B (고객 B)', k='이씨 줄')
    for j, s in enumerate(['B2', 'B1']):
        D.bar(240 + j * 64, 120, 60, 30, s, k=['이2', '이1'][j], t='soft')
    D.bar(176, 164, 92, 30, 'A2 (다시 옴)', k='김2 (또 옴)', t='warn')
    D.text(276, 184, '5분 안 중복 → 버림', k='5분 안에 또 옴 → 버림')
    D.node('c1', 480, 43, 112, 52, '소비자 1', '그룹 A 차례로', k='요리사 1', ksub='김씨 줄 차례로')
    D.node('c2', 480, 109, 112, 52, '소비자 2', '그룹 B 차례로', k='요리사 2', ksub='이씨 줄 차례로')
    D.arrow((366, 69), (478, 69), t='acc')
    D.arrow((366, 135), (478, 135), t='acc')
    D.text(8, 236, '이름은 .fifo로 끝남 · 초당 300건(일괄 처리 시 3,000건), 고처리량 모드는 더 많이',
           k='보통 꽂이보다 덜 받지만 순서와 한 번만을 지켜요')
    return D


@reg('c17-sqs-asg')
def _():
    D = Diagram('c17-sqs-asg', w=600, at='데이터베이스 쓰기 버퍼',
                cap='웹 앱은 주문을 SQS에 넣고 바로 응답합니다. CloudWatch 경보가 쌓인 메시지 수를 보고 ASG의 소비자를 늘리며, 소비자는 꺼낸 순서대로 DB에 씁니다.',
                kcap='홀 직원은 꽂이에 꽂고 바로 대답해요. 관제실이 쌓인 주문서를 보고 매니저에게 요리사를 늘리라고 해요.')
    D.node('web', 8, 40, 110, 64, '웹 앱', '주문 접수', 'browser', lay='side', k='홀 직원', ksub='주문 받기')
    D.node('q', 160, 40, 130, 64, 'SQS', '쓰기 버퍼', 'queue', t='hl', lay='side', k='주문서 꽂이', ksub='쌓아 두기')
    D.group(330, 8, 262, 136, 'ASG (소비자)', k='요리사들', solid=True)
    D.node('e1', 342, 40, 116, 44, 'EC2', k='요리사')
    D.node('e2', 466, 40, 116, 44, 'EC2', k='요리사')
    D.node('e3', 342, 92, 116, 44, 'EC2 추가', t='muted', k='새 요리사')
    D.node('e4', 466, 92, 116, 44, 'EC2 추가', t='muted', k='새 요리사')
    D.node('cw', 160, 180, 172, 64, 'CloudWatch 경보', '쌓인 메시지 수', 'bell', lay='side', k='관제실 경보', ksub='쌓인 주문서 수')
    D.node('db', 420, 180, 172, 64, 'RDS', '차례로 쓰기', 'db', t='store', lay='side', k='기록실', ksub='차례로 적기')
    D.edge('web', 'q', '주문', k='꽂기', t='acc')
    D.edge('q', 'e1', '폴링', k='빼 가기', t='acc')
    D.edge('q', 'cw', '지표', k='세기', dash=True)
    D.edge('cw', 'e3', '늘리기', k='더 불러', t='ok', sa='r', sb='b', lp=0)
    D.edge('e4', 'db', '쓰기', k='적기', t='acc')
    D.text(8, 280, '대상 추적 지표: 인스턴스당 백로그 = 대기 메시지 수 ÷ 인스턴스 수',
           k='매니저 기준: 요리사 한 명당 쌓인 주문서 수')
    return D


@reg('c17-sns-fanout')
def _():
    D = Diagram('c17-sns-fanout', w=600, at='SNS FIFO',
                cap='주문 서비스가 SNS 주제에 한 번 발행하면 구독한 SQS 대기열 세 개에 사본이 하나씩 들어가고, 각 서비스가 자기 대기열에서 따로 처리합니다. 이메일 같은 구독자도 함께 받습니다.',
                kcap='방송 한 번에 계산대, 배달, 장부 꽂이에 같은 주문서가 한 장씩 꽂혀요. 사장님 휴대폰에도 문자가 가요.')
    D.node('src', 8, 76, 120, 72, '주문 서비스', '발행 한 번', 'server', k='홀 직원', ksub='방송 한 번')
    D.node('sns', 170, 72, 140, 80, 'SNS 주제', '주문 생성', 'bell', t='hl', k='안내 방송', ksub='주문 채널')
    for i, (s, ks, a, ka) in enumerate([('결제', '계산대', '결제 앱', '계산원'), ('배송', '배달', '배송 앱', '배달원'), ('분석', '장부', '분석 앱', '장부원')]):
        y = 8 + i * 78
        D.node(f'q{i}', 360, y, 120, 52, 'SQS', s, 'queue', k='꽂이', ksub=ks)
        D.node(f's{i}', 512, y, 80, 52, a, k=ka)
        D.edge(f'q{i}', f's{i}', t='acc')
    D.edge('src', 'sns', '발행', k='방송', t='acc')
    D.edge('sns', 'q0', t='acc', sa=('r', 0.2), sb='l')
    D.edge('sns', 'q1', t='acc')
    D.edge('sns', 'q2', t='acc', sa=('r', 0.8), sb='l')
    D.node('mail', 170, 200, 140, 52, '이메일·SMS', '관리자 알림', 'mail', lay='side', k='사장님 휴대폰', ksub='문자 받기')
    D.edge('sns', 'mail', '구독', k='듣기')
    D.text(8, 286, '구독마다 필터 정책 가능 · SQS 액세스 정책에서 SNS의 SendMessage 허용',
           k='각자 듣고 싶은 방송만 고를 수 있어요 · 꽂이는 방송실이 꽂도록 허락해 둬요')
    return D


@reg('c17-kinesis')
def _():
    D = Diagram('c17-kinesis', w=600, at='용량 모드',
                cap='생산자가 보낸 레코드는 파티션 키에 따라 샤드에 들어가고, 같은 키는 같은 샤드로 가서 순서가 지켜집니다. 여러 소비자가 같은 데이터를 각자 읽고, 보존 기간 동안 다시 읽을 수 있습니다.',
                kcap='이름표를 보고 레인을 정해요. 같은 이름표는 같은 레인이라 순서가 지켜지고, 여러 팀이 같은 물건을 각자 봐요.')
    for i, (l, kl, ic) in enumerate([('IoT 장치', '센서', 'chip'), ('앱 로그', '일지', 'log'), ('클릭 기록', '클릭', 'browser')]):
        y = 36 + i * 60
        D.node(f'p{i}', 8, y, 120, 52, l, None, ic, k=kl)
        D.arrow((128, y + 26), (160, y + 26), t='acc')
    D.group(150, 8, 270, 236, 'Kinesis Data Streams', k='컨베이어 벨트', solid=True)
    for i, (s, ks) in enumerate([('샤드 1 · 파티션 키 A, C', '레인 1 · 이름표 가, 다'), ('샤드 2 · 파티션 키 B', '레인 2 · 이름표 나'), ('샤드 3 · 파티션 키 D', '레인 3 · 이름표 라')]):
        D.bar(162, 40 + i * 60, 246, 44, s, k=ks, t='soft')
    D.text(162, 232, '보존 1–365일 · 다시 읽기 가능', k='하루~1년 남아 있어요')
    for i, (l, kl, ic, kic) in enumerate([('Lambda', '심부름꾼', 'lambda', 'user'), ('Data Firehose', '택배 트럭', 'truck', 'truck'), ('분석 앱(KCL)', '분석 팀', 'chart', 'chart')]):
        y = 36 + i * 60
        D.node(f'c{i}', 470, y, 122, 52, l, None, None, k=kl)
        D.arrow((410, y + 26), (468, y + 26), t='acc')
    D.text(8, 272, '샤드 하나: 쓰기 1MB/s(1,000 레코드/s) · 읽기 2MB/s · 같은 파티션 키 = 같은 샤드',
           k='레인 하나가 1초에 싣는 양은 정해져 있어요 · 같은 이름표 = 같은 레인')
    return D


@reg('c17-firehose')
def _():
    D = Diagram('c17-firehose', w=600, at='Kinesis Data Streams와 비교',
                cap='여러 원천의 데이터를 Firehose가 버퍼에 모아 Lambda로 변환하고 Parquet·ORC로 바꾸거나 압축해 대상에 배달합니다. 배달에 실패한 데이터는 백업 S3에 남깁니다.',
                kcap='트럭이 여러 곳의 물건을 모아 손질하고 포장을 바꿔 창고마다 배달해요. 못 보낸 물건은 예비 창고에 둬요.')
    for i, (l, kl) in enumerate([('Data Streams', '컨베이어 벨트'), ('SDK·에이전트', '직접 보내기'), ('CloudWatch Logs', '관제실 기록')]):
        D.node(f's{i}', 8, 16 + i * 64, 140, 48, l, k=kl)
    D.node('fh', 196, 40, 170, 136, 'Data Firehose', '버퍼 · 변환 · 압축', 'truck', t='hl', k='택배 묶음 트럭', ksub='모아서 · 손질 · 압축')
    D.edge('s0', 'fh', t='acc')
    D.edge('s1', 'fh', t='acc')
    D.edge('s2', 'fh', t='acc')
    D.node('lam', 196, 210, 130, 48, 'Lambda 변환', k='손질 심부름꾼')
    D.edge('fh', 'lam', '변환', k='손질', both=True, dash=True, sa=('b', 0.38), sb='t')
    for i, (l, kl) in enumerate([('S3', '큰 창고'), ('Redshift (S3 경유)', '데이터 창고'), ('OpenSearch', '검색 창고'), ('HTTP·서드파티', '다른 회사 창구')]):
        D.node(f'd{i}', 420, 16 + i * 54, 172, 44, l, t='store', k=kl)
    D.edge('fh', 'd0', t='acc', sa=('r', 0.1), sb='l')
    D.edge('fh', 'd1', t='acc')
    D.edge('fh', 'd2', t='acc')
    D.edge('fh', 'd3', t='acc', sa=('r', 0.95), sb='l')
    D.node('bk', 420, 236, 172, 44, '백업 S3', '실패분·원본', t='warn', k='예비 창고', ksub='못 보낸 것 보관')
    D.edge('fh', 'bk', dash=True, t='bad', sa=('b', 0.9), sb='l')
    D.text(8, 310, '거의 실시간(버퍼) · 저장·재처리 없음 · Parquet·ORC 변환',
           k='어느 정도 모이면 출발 · 보관은 안 해요 · 포장 바꾸기')
    return D


@reg('c17-compare-mq')
def _():
    D = Diagram('c17-compare-mq', w=600, at='Amazon MQ',
                cap='SQS는 소비자들이 메시지를 나눠 가져가고 처리하면 지웁니다. SNS는 모든 구독자에게 같은 메시지를 밀어 주고 남기지 않습니다. Kinesis는 데이터를 보존 기간 동안 남겨 두고 여러 소비자가 각자 읽습니다.',
                kcap='꽂이는 나눠 빼 가고, 방송은 모두에게 똑같이 알리고, 벨트는 남겨 두고 각자 봐요.')
    cols = [('SQS: 나눠 가져감', '꽂이: 나눠 빼 감', '대기열', '주문서 꽂이', '소비자', '요리사', '처리하면 지움', '요리하면 버려요', 'queue'),
            ('SNS: 모두에게 밀어 줌', '방송: 모두에게', '주제', '안내 방송', '구독자', '듣는 곳', '저장 안 함', '방송은 남지 않아요', 'bell'),
            ('Kinesis: 남겨 두고 읽음', '벨트: 남겨 두고 봄', '스트림', '컨베이어 벨트', '소비자', '팀', '보존 기간 동안 재처리', '한동안 다시 볼 수 있어요', 'stream')]
    for c, (gl, kgl, top, ktop, sub, ksub, foot, kfoot, ic) in enumerate(cols):
        x = 8 + c * 198
        D.group(x, 8, 188, 220, gl, k=kgl, solid=True)
        D.node(f't{c}', x + 12, 40, 164, 50, top, None, ic, t='hl', k=ktop)
        D.node(f'a{c}', x + 12, 130, 76, 44, sub, k=ksub + (' 가' if c == 2 else ''))
        D.node(f'b{c}', x + 100, 130, 76, 44, sub, k=ksub + (' 나' if c == 2 else ''))
        D.edge(f't{c}', f'a{c}', t='acc')
        D.edge(f't{c}', f'b{c}', t='acc')
        D.text(x + 12, 206, foot, k=kfoot)
    D.text(8, 252, 'SQS 메시지 1 → 소비자 하나만 · SNS 메시지 1 → 구독자 모두 · Kinesis 레코드 1 → 소비자 모두(여러 번)',
           k='주문서 한 장은 요리사 한 명만 · 방송은 모두 · 벨트 물건은 모든 팀이 여러 번')
    return D


@reg('c17-compare-mq:mq')
def _():
    D = Diagram('c17-compare-mq:mq', w=600, at='end:Amazon MQ',
                cap='온프레미스 앱은 AMQP·MQTT 같은 개방형 프로토콜을 그대로 쓰며 Amazon MQ 브로커에 연결합니다. ActiveMQ는 두 AZ의 활성·대기 브로커가 EFS를 함께 써서 장애 때 대기 브로커가 이어받습니다.',
                kcap='이사 온 식당은 원래 전달 방식 그대로 전달소에 말해요. 두 동네에 전달소를 하나씩 두고 장부를 같이 봐서, 하나가 멈추면 다른 하나가 이어받아요.')
    D.node('app', 8, 70, 150, 64, '온프레미스 앱', 'AMQP · MQTT', 'building', lay='side', k='이사 온 식당', ksub='원래 전달 방식')
    D.group(200, 8, 220, 110, 'AZ a', k='동네 가', solid=True)
    D.node('b1', 214, 40, 192, 56, 'MQ 브로커 (활성)', 'ActiveMQ', t='hl', k='전달소 (일하는 중)', ksub='원래 방식 그대로')
    D.group(200, 130, 220, 110, 'AZ b', k='동네 나', solid=True)
    D.node('b2', 214, 162, 192, 56, 'MQ 브로커 (대기)', 'ActiveMQ', t='muted', k='전달소 (대기)', ksub='멈추면 이어받기')
    D.node('efs', 462, 96, 130, 64, 'EFS', '공유 스토리지', 'folder', t='store', lay='side', k='공용 서류실', ksub='함께 보는 장부')
    D.edge('app', 'b1', 'AMQP', k='원래 방식', t='acc')
    D.edge('app', 'b2', '장애 조치', k='바꿔 넣기', dash=True, sa=('b', 0.5), sb='l')
    D.edge('b1', 'efs', both=True, sa='r', sb=('l', 0.3), via=[(438, 68), (438, 115.2)])
    D.edge('b2', 'efs', both=True, dash=True, sa='r', sb=('l', 0.7), via=[(450, 190), (450, 140.8)])
    return D


@reg('c18-docker-ecr')
def _():
    D = Diagram('c18-docker-ecr', w=600, at='Amazon ECR(Elastic Container Registry)',
                cap='Dockerfile로 이미지를 만들어 ECR에 올리면 ECS, EKS, Lambda가 내려받아 실행합니다. 아래는 가상 머신과 컨테이너의 차이로, 컨테이너는 호스트 OS 커널을 함께 써서 가볍습니다.')
    D.node('df', 8, 24, 110, 72, 'Dockerfile', None, 'file')
    D.node('img', 160, 24, 110, 72, '이미지', 'docker build', 'box')
    D.node('ecr', 320, 16, 150, 88, 'Amazon ECR', '비공개 저장소 · 스캔', 'box', t='hl')
    D.node('ecs', 500, 8, 92, 36, 'ECS')
    D.node('eks', 500, 52, 92, 36, 'EKS')
    D.node('lam', 500, 96, 92, 36, 'Lambda')
    D.edge('df', 'img', 'build', t='acc')
    D.edge('img', 'ecr', 'push', t='acc')
    D.edge('ecr', 'ecs', t='acc')
    D.edge('ecr', 'eks', t='acc')
    D.edge('ecr', 'lam', t='acc', sa=('r', 0.85), sb='l')
    D.group(8, 166, 284, 158, '가상 머신: OS를 각자', solid=True)
    D.bar(20, 196, 128, 28, '앱 A', t='soft')
    D.bar(152, 196, 128, 28, '앱 B', t='soft')
    D.bar(20, 226, 128, 28, '게스트 OS', t='muted')
    D.bar(152, 226, 128, 28, '게스트 OS', t='muted')
    D.bar(20, 256, 260, 28, '하이퍼바이저', t='store')
    D.bar(20, 286, 260, 28, '하드웨어', t='muted')
    D.group(300, 166, 292, 158, '컨테이너: OS 커널을 함께', solid=True)
    for j, a in enumerate(['앱 A', '앱 B', '앱 C']):
        D.bar(312 + j * 90, 196, 86, 28, a, t='soft')
    D.bar(312, 226, 266, 28, 'Docker 엔진', t='acc')
    D.bar(312, 256, 266, 28, '호스트 OS', t='muted')
    D.bar(312, 286, 266, 28, '하드웨어', t='muted')
    return D


@reg('c18-ecs')
def _():
    D = Diagram('c18-ecs', w=600, at='데이터 볼륨',
                cap='ALB가 여러 AZ의 작업으로 요청을 나눕니다. 작업 안의 앱은 작업 역할로 DynamoDB 같은 AWS 서비스에 접근하고, 이미지 받기와 로그 전송은 작업 실행 역할이 맡습니다. EFS는 여러 작업이 함께 쓰는 영구 저장소입니다.')
    D.node('alb', 8, 100, 104, 64, 'ALB', '동적 포트', 'lb', t='hl', lay='side')
    D.group(150, 8, 250, 240, 'ECS 서비스 · 원하는 작업 3', solid=True)
    D.node('t1', 162, 40, 226, 52, '작업 1', 'AZ a · Fargate', 'box')
    D.node('t2', 162, 112, 226, 52, '작업 2', 'AZ b · Fargate', 'box')
    D.node('t3', 162, 184, 226, 52, '작업 3', 'AZ c · EC2 시작 유형', 'box')
    D.node('ddb', 440, 8, 152, 56, 'DynamoDB', '작업 역할로 접근', 'db', t='store', lay='side')
    D.node('efs', 440, 100, 152, 64, 'EFS', '작업들이 공유', 'folder', t='store', lay='side')
    D.node('ecr', 440, 196, 152, 56, 'ECR · 로그', '작업 실행 역할', 'box', lay='side')
    D.edge('alb', 't1', t='acc', sa=('r', 0.2), sb='l')
    D.edge('alb', 't2', t='acc')
    D.edge('alb', 't3', t='acc', sa=('r', 0.8), sb='l')
    D.edge('t1', 'ddb', both=True)
    D.edge('t2', 'efs', both=True, dash=True)
    D.edge('t3', 'ecr', both=True, dash=True)
    return D


@reg('c18-ecs-scaling')
def _():
    D = Diagram('c18-ecs-scaling', w=600, at='작업 수와 서버 수는 따로 늘어난다',
                cap='CloudWatch 지표가 목표를 넘으면 Application Auto Scaling이 서비스의 원하는 작업 수를 늘립니다. EC2 시작 유형이면 용량 공급자가 그 작업을 올릴 EC2를 ASG로 함께 늘리고, Fargate는 작업만 늘리면 됩니다.')
    D.node('cw', 8, 30, 150, 64, 'CloudWatch 지표', 'CPU · 요청 수')
    D.node('aas', 220, 30, 160, 64, 'Auto Scaling', '원하는 작업 수 ↑', 'scale', lay='side')
    D.node('svc', 410, 16, 182, 92, 'ECS 서비스', '작업 4 → 8', 'box', t='hl')
    D.node('cp', 410, 150, 182, 64, '용량 공급자', 'ASG 인스턴스 ↑', 'server', lay='side')
    D.node('fg', 220, 150, 160, 64, 'Fargate', '작업만 늘리면 끝', 'cloud', t='ok', lay='side')
    D.edge('cw', 'aas', '목표 초과', t='acc')
    D.edge('aas', 'svc', t='acc')
    D.edge('svc', 'cp', 'EC2라면', t='acc')
    D.edge('svc', 'fg', 'Fargate라면', t='ok', sa=('b', 0.15), sb='t')
    return D


@reg('c18-ecs-scaling:patterns')
def _():
    D = Diagram('c18-ecs-scaling:patterns', w=600, at='end:자주 나오는 아키텍처 네 가지',
                cap='① 파일 업로드 처리, ② 일정 배치, ③ 대기열 소비, ④ 작업 장애 알림. 모두 서버 관리 없이 Fargate 작업으로 만들 수 있습니다.')
    rows = [
        [('① S3 업로드', None), ('EventBridge', '규칙'), ('ECS 작업', 'Fargate'), ('DynamoDB', '결과 저장')],
        [('② EventBridge', '매시간 일정'), ('ECS 작업', 'Fargate'), ('S3', '배치 처리'), None],
        [('③ SQS', '대기열'), ('ECS 서비스', '폴링 · 자동 확장'), None, None],
        [('④ ECS 작업', 'STOPPED 이벤트'), ('EventBridge', '규칙'), ('SNS', '주제'), ('관리자', '이메일')],
    ]
    for i, row in enumerate(rows):
        y = 16 + i * 64
        prev = None
        for j, cell in enumerate(row):
            if not cell:
                continue
            key = f'n{i}{j}'
            D.node(key, 8 + j * 148, y, 128, 48, cell[0], cell[1], t='hl' if 'ECS' in cell[0] else 'plain')
            if prev:
                D.edge(prev, key, t='acc')
            prev = key
    return D


@reg('c18-eks')
def _():
    D = Diagram('c18-eks', w=600, at='데이터 볼륨',
                cap='AWS가 쿠버네티스 컨트롤 플레인을 여러 AZ에서 운영하고, 워커 노드는 관리형 노드 그룹, 자체 관리형 노드, Fargate, EKS Auto Mode 중에서 고릅니다. 저장소는 CSI 드라이버로 EBS, EFS, FSx를 붙입니다.')
    D.node('cli', 8, 8, 150, 44, 'kubectl · Helm')
    D.node('cp', 8, 92, 150, 100, 'EKS 컨트롤 플레인', 'AWS가 운영 · 다중 AZ', t='hl')
    D.edge('cli', 'cp', 'API', t='acc')
    D.arrow((158, 142), (198, 142), t='acc')
    D.group(200, 8, 240, 240, '데이터 플레인 (노드)', solid=True)
    D.node('mng', 212, 40, 216, 44, '관리형 노드 그룹', 'EC2 · 온디맨드·스팟')
    D.node('self', 212, 92, 216, 44, '자체 관리형 노드', '사용자 지정 AMI')
    D.node('fg', 212, 144, 216, 44, 'Fargate', '노드 없이 파드 실행', t='ok')
    D.node('auto', 212, 196, 216, 44, 'EKS Auto Mode', '노드 관리까지 위임', t='ok')
    D.node('ebs', 480, 40, 112, 56, 'EBS', 'CSI 드라이버', t='store')
    D.node('efs', 480, 124, 112, 56, 'EFS', 'Fargate도 가능', t='store')
    D.node('fsx', 480, 200, 112, 48, 'FSx', 'Lustre · ONTAP', t='store')
    D.edge('mng', 'ebs', dash=True)
    D.edge('fg', 'efs', dash=True)
    D.edge('auto', 'fsx', dash=True)
    return D
