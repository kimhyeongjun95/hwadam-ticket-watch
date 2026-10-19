from dg import Diagram, reg


@reg('c19-lambda')
def _():
    D = Diagram('c19-lambda', w=600, at='end:대표 패턴',
                cap='API 호출, S3 업로드, SQS 메시지, 정해진 시각 같은 이벤트가 Lambda 함수를 실행하고, 함수는 결과를 DynamoDB, S3, SNS 등에 씁니다. 실행될 때만 요금을 냅니다.')
    srcs = [('API Gateway', 'api'), ('S3 이벤트', 'bucket'), ('SQS', 'queue'), ('EventBridge 일정', 'clock')]
    for i, (l, ic) in enumerate(srcs):
        D.node(f's{i}', 8, 16 + i * 54, 140, 44, l, None, None)
    D.node('fn', 200, 70, 160, 96, 'Lambda 함수', '최대 15분 · 10GB', 'lambda', t='hl')
    for i, f in enumerate([0.15, 0.4, 0.65, 0.9]):
        y0 = 38 + i * 54
        yt = 70 + 96 * f
        D.edge(f's{i}', 'fn', t='acc', sa='r', sb=('l', f), via=[(174, y0), (174, yt)])
    D.node('ddb', 420, 64, 172, 44, 'DynamoDB', None, 'db', t='store', lay='side')
    D.node('s3o', 420, 118, 172, 44, 'S3', None, 'bucket', t='store', lay='side')
    D.node('sns', 420, 172, 172, 44, 'SNS', None, 'bell', lay='side')
    D.edge('fn', 'ddb', t='acc')
    D.edge('fn', 's3o', t='acc')
    D.edge('fn', 'sns', t='acc', sa=('r', 0.9), sb='l')
    D.text(8, 250, '요금 = 요청 수 + 실행 시간(GB·초) · 매달 100만 요청과 40만 GB·초 무료')
    return D


@reg('c19-concurrency')
def _():
    D = Diagram('c19-concurrency', w=600, at='콜드 스타트와 프로비저닝된 동시성',
                cap='계정 한도 1,000 중 결제 함수에 200을 예약하면, 이미지 함수가 폭주해 나머지 800을 다 써도 결제 함수는 계속 실행됩니다. 아래는 첫 요청이 처리되기까지의 시간을 세 방식으로 비교한 것입니다.')
    D.text(8, 20, '계정 동시성 한도 1,000(리전)', cls='lbl')
    D.bar(8, 30, 117, 34, '결제 200', t='ok')
    D.bar(127, 30, 465, 34, '나머지 함수가 함께 쓰는 800', t='soft')
    D.text(8, 94, '이미지 함수가 몰릴 때', cls='lbl')
    D.bar(8, 104, 117, 34, '몫 보장', t='ok')
    D.bar(127, 104, 465, 34, '이미지 함수 800 → 다른 함수 스로틀링(429)', t='warn')
    rows = [('콜드 스타트', [(150, '환경 준비 · 초기화', 'warn'), (120, '처리', 'ok')]),
            ('프로비저닝된 동시성', [(120, '처리', 'ok')]),
            ('SnapStart', [(60, '복원', 'soft'), (120, '처리', 'ok')])]
    for i, (lab, segs) in enumerate(rows):
        y = 168 + i * 42
        D.text(8, y + 21, lab, cls='lbl')
        x = 190
        for w, s, t in segs:
            D.bar(x, y, w, 30, s, t=t)
            x += w + 2
    D.text(190, 306, '첫 요청이 들어와서 응답할 때까지 →')
    return D


@reg('c19-edge')
def _():
    D = Diagram('c19-edge', w=600, at='두 방식 비교',
                cap='엣지에서 코드를 실행할 수 있는 시점은 네 곳입니다. 사용자 쪽(뷰어 요청·응답)은 CloudFront Functions와 Lambda@Edge 모두, 오리진 쪽(오리진 요청·응답)은 Lambda@Edge만 됩니다.')
    D.node('u', 8, 50, 100, 80, '사용자', None, 'users')
    D.node('cf', 250, 50, 120, 80, 'CloudFront', '엣지', 'cloud', t='hl')
    D.node('o', 492, 50, 100, 80, '오리진', None, 'server')
    D.edge('u', 'cf', '① 뷰어 요청', t='acc', sa=('r', 0.25), sb=('l', 0.25))
    D.edge('cf', 'u', '④ 뷰어 응답', t='ok', sa=('l', 0.75), sb=('r', 0.75))
    D.edge('cf', 'o', '② 오리진 요청', t='acc', sa=('r', 0.25), sb=('l', 0.25))
    D.edge('o', 'cf', '③ 오리진 응답', t='ok', sa=('l', 0.75), sb=('r', 0.75))
    D.bar(8, 160, 288, 30, '뷰어 쪽(①④): 둘 다 가능', t='ok')
    D.bar(300, 160, 292, 30, '오리진 쪽(②③): Lambda@Edge만', t='soft')
    return D


@reg('c19-lambda-vpc')
def _():
    D = Diagram('c19-lambda-vpc', w=600, at='Lambda와 RDS',
                cap='VPC에 연결한 Lambda는 서브넷에 ENI를 두고, RDS Proxy를 거쳐 프라이빗 RDS에 접속합니다. 공인 IP가 없으므로 외부 API는 NAT 게이트웨이로 나가고, S3·DynamoDB는 VPC 엔드포인트로 가면 NAT 요금이 들지 않습니다.')
    D.group(8, 8, 452, 260, 'VPC', solid=True)
    D.group(20, 36, 270, 222, '프라이빗 서브넷', lpos='bl')
    D.group(300, 36, 152, 120, '퍼블릭 서브넷', lpos='bl')
    D.node('lam', 32, 110, 120, 72, 'Lambda', 'ENI · 보안 그룹', 'lambda', t='hl')
    D.node('proxy', 168, 60, 110, 64, 'RDS Proxy', '연결 풀링')
    D.node('rds', 168, 170, 110, 72, 'RDS', '프라이빗', 'db', t='store')
    D.node('nat', 312, 70, 128, 56, 'NAT 게이트웨이')
    D.node('net', 488, 70, 104, 56, '외부 API', None, t='muted')
    D.edge('lam', 'proxy', t='acc', sa=('r', 0.3), sb='l')
    D.edge('proxy', 'rds', '연결 재사용', t='acc')
    D.edge('lam', 'nat', '외부 호출', sa='t', sb='t', via=[(92, 46), (376, 46)])
    D.edge('nat', 'net', t='acc')
    D.text(8, 292, 'S3·DynamoDB는 VPC 엔드포인트로 가면 NAT 요금이 들지 않음')
    return D


@reg('c19-dynamodb')
def _():
    D = Diagram('c19-dynamodb', w=600, at='읽기·쓰기 용량 모드',
                cap='주문 테이블 예시입니다. 파티션 키(user_id)가 같은 항목은 함께 저장되고 정렬 키(order_ts) 순으로 정렬됩니다. 항목마다 속성이 달라도 되고, 항목 하나는 최대 400KB입니다.')
    D.bar(8, 16, 150, 30, 'user_id (파티션 키)', t='acc')
    D.bar(162, 16, 170, 30, 'order_ts (정렬 키)', t='acc')
    D.bar(336, 16, 256, 30, '속성(항목마다 다름)', t='muted')
    rows = [('u1', '2026-10-01', 'total=30000 · status=paid', 'soft'),
            ('u1', '2026-10-05', 'total=12000 · coupon=A1', 'soft'),
            ('u2', '2026-10-03', 'total=8000', 'store')]
    for i, (pk, sk, at, t) in enumerate(rows):
        y = 50 + i * 34
        D.bar(8, y, 150, 30, pk, t=t)
        D.bar(162, y, 170, 30, sk, t=t)
        D.bar(336, y, 256, 30, at, t=t)
    D.node('prov', 8, 170, 284, 64, '프로비저닝 모드', 'RCU·WCU 지정 · 오토 스케일링 · 꾸준한 트래픽')
    D.node('od', 308, 170, 284, 64, '온디맨드 모드', '요청당 과금 · 예측 불가 트래픽', t='hl')
    return D


@reg('c19-dynamodb-adv')
def _():
    D = Diagram('c19-dynamodb-adv', w=600, at='DAX(DynamoDB Accelerator)',
                cap='앱은 DAX를 거쳐 읽어 마이크로초 응답을 받습니다. 테이블의 변경은 스트림으로 흘러 Lambda가 처리하고, 전역 테이블은 다른 리전 복제본과 양방향으로 맞춥니다. PITR을 켜면 운영 부하 없이 S3로 내보낼 수 있습니다.')
    D.node('app', 8, 30, 110, 64, '앱', None, 'browser')
    D.node('dax', 160, 30, 120, 64, 'DAX', '마이크로초 캐시', t='hl')
    D.node('tbl', 320, 20, 130, 84, 'DynamoDB\n테이블', '서울', t='store')
    D.node('glb', 490, 20, 102, 84, '전역 테이블\n복제본', '버지니아', t='store')
    D.node('st', 320, 150, 130, 56, 'Streams', '24시간 보존')
    D.node('lam', 490, 150, 102, 56, 'Lambda')
    D.node('s3', 8, 150, 120, 56, 'S3', '내보내기', 'bucket', lay='side')
    D.edge('app', 'dax', t='acc')
    D.edge('dax', 'tbl', t='acc')
    D.edge('tbl', 'glb', both=True, t='acc')
    D.edge('tbl', 'st', '변경', t='acc')
    D.edge('st', 'lam', t='acc')
    D.edge('tbl', 's3', 'PITR 필요', dash=True, sa=('b', 0.1), sb='t', via=[(333, 124), (68, 124)])
    D.text(8, 240, '+ TTL: 만료 시각이 지난 항목 자동 삭제 · PITR: 최근 1–35일 중 아무 시점으로 새 테이블 복원')
    return D


@reg('c19-apigw')
def _():
    D = Diagram('c19-apigw', w=600, at='엔드포인트 유형',
                cap='클라이언트 요청은 API Gateway에서 인증(Cognito 토큰 등), 요청 제한, 캐시를 거친 뒤 Lambda, HTTP 백엔드, SQS 같은 AWS 서비스로 전달됩니다.')
    D.node('cl', 8, 90, 110, 72, '클라이언트', '앱 · 파트너', 'users')
    D.node('gw', 170, 70, 170, 112, 'API Gateway', '인증 · 요청 제한 · 캐시', 'api', t='hl')
    D.node('lam', 400, 16, 192, 52, 'Lambda', '서버리스 API', 'lambda', lay='side')
    D.node('http', 400, 100, 192, 52, 'HTTP 백엔드', 'ALB · 온프레미스', 'server', lay='side')
    D.node('sqs', 400, 184, 192, 52, 'SQS', 'AWS 서비스 통합', 'queue', lay='side')
    D.node('cog', 170, 220, 170, 56, 'Cognito 사용자 풀', 'JWT 발급')
    D.edge('cl', 'gw', t='acc')
    D.edge('gw', 'lam', t='acc', sa=('r', 0.15), sb='l')
    D.edge('gw', 'http', t='acc')
    D.edge('gw', 'sqs', t='acc', sa=('r', 0.85), sb='l')
    D.edge('gw', 'cog', '토큰 확인', dash=True)
    D.text(8, 306, '엔드포인트: 엣지 최적화 · 리전 · 프라이빗 | 통합 제한 시간 기본 29초 · 페이로드 10MB')
    return D


@reg('c19-stepfunctions')
def _():
    D = Diagram('c19-stepfunctions', w=600,
                cap='주문 처리 상태 머신의 예입니다. 결제가 실패하면 실패 처리로 끝나고, 성공하면 재고 확보, 사람 승인, 배송 요청을 차례로 실행합니다. 각 단계에 재시도와 오류 처리를 붙입니다.')
    D.node('st', 8, 20, 90, 44, '시작', t='muted')
    D.node('pay', 130, 20, 150, 44, '결제 승인', 'Lambda')
    D.node('ch', 320, 20, 110, 44, '결제 성공?', t='warn')
    D.node('fail', 478, 20, 114, 44, '실패 처리', 'SNS 알림', t='warn')
    D.node('stock', 320, 110, 120, 52, '재고 확보', 'DynamoDB')
    D.node('appr', 160, 110, 130, 52, '사람 승인', '승인 올 때까지 대기', t='hl')
    D.node('ship', 8, 110, 120, 52, '배송 요청', 'ECS 작업')
    D.node('done', 8, 200, 120, 40, '완료', t='ok')
    D.edge('st', 'pay', t='acc')
    D.edge('pay', 'ch', t='acc')
    D.edge('ch', 'fail', '아니오', t='bad')
    D.edge('ch', 'stock', '예', t='ok', sa=('b', 0.5), sb=('t', 0.46))
    D.edge('stock', 'appr', t='acc')
    D.edge('appr', 'ship', t='acc')
    D.edge('ship', 'done', t='ok')
    D.text(160, 226, 'Standard: 최대 1년, 정확히 한 번 · Express: 최대 5분, 대량 이벤트')
    return D


@reg('c19-cognito')
def _():
    D = Diagram('c19-cognito', w=600, at='end:자격 증명 풀(Identity Pools): AWS 자원 직접 접근',
                cap='① 앱 사용자가 사용자 풀에 로그인하면 ② JWT 토큰으로 API Gateway나 ALB를 부릅니다. AWS 자원에 직접 접근하려면 ③ 토큰을 자격 증명 풀에서 임시 AWS 자격 증명으로 바꾸고 ④ 조건이 걸린 범위 안에서 S3·DynamoDB를 부릅니다.')
    D.node('app', 8, 100, 110, 72, '모바일·웹 앱', None, 'phone')
    D.node('up', 170, 16, 170, 64, '사용자 풀', '가입 · 로그인 · MFA', 'users', t='hl', lay='side')
    D.node('gw', 410, 16, 182, 64, 'API Gateway · ALB', 'JWT 검증')
    D.node('ip', 170, 190, 170, 64, '자격 증명 풀', '임시 AWS 자격 증명', 'key', t='hl', lay='side')
    D.node('res', 410, 190, 182, 64, 'S3 · DynamoDB', '자기 데이터만(조건)', t='store')
    D.edge('app', 'up', '① 로그인', t='acc', sa='t', sb='l', lp=0)
    D.edge('up', 'gw', '② 토큰', t='acc')
    D.edge('app', 'ip', '③ 토큰 교환', t='acc', sa='b', sb='l', lp=0)
    D.edge('ip', 'res', '④ 접근', t='acc')
    D.text(8, 290, '직원의 AWS 콘솔 로그인은 Cognito가 아니라 IAM Identity Center')
    return D
