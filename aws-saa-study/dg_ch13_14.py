from dg import Diagram, reg


@reg('c13-lifecycle')
def _():
    D = Diagram('c13-lifecycle', w=600, at='강의의 두 시나리오',
                cap='현재 버전은 만든 날부터, 이전 버전은 이전 버전이 된 날부터 날짜를 셉니다. 스토리지 클래스 분석이 Standard → Standard-IA 시점을 추천하면 그 날짜로 규칙을 만듭니다.',
                kcap='지금 물건과 옛 물건에 각각 정리 날짜를 정해요. 관찰 보고서가 "이때 옮기면 좋아요" 하고 알려 줘요.')
    xs = {0: 150, 30: 240, 180: 400, 365: 530}
    D.text(8, 51, '현재 버전', k='지금 물건', cls='lbl')
    D.bar(150, 30, 88, 34, 'Standard', k='앞 선반', t='acc')
    D.bar(240, 30, 158, 34, 'Standard-IA', k='안쪽 선반', t='soft')
    D.bar(400, 30, 128, 34, 'Glacier Flexible', k='지하 칸', t='store')
    D.bar(530, 30, 62, 34, '만료', k='버림', t='warn')
    D.text(8, 103, '이전 버전', k='옛 물건', cls='lbl')
    D.bar(150, 82, 88, 34, 'Standard', k='앞 선반', t='acc')
    D.bar(240, 82, 288, 34, 'Glacier Deep Archive', k='가장 깊은 칸', t='store')
    D.bar(530, 82, 62, 34, '만료', k='버림', t='warn')
    for d, x in xs.items():
        D.text(x, 140, f'{d}일', anchor='start' if d == 0 else 'middle')
    D.node('sca', 8, 172, 170, 64, '스토리지 클래스\n분석', 'IA 전환 시점 추천', 'chart', lay='side', k='관찰 보고서', ksub='옮길 때를 알려 줌')
    D.node('rule', 232, 172, 156, 64, '수명 주기 규칙', '전환 + 만료', 'calendar', t='hl', lay='side', k='정리 규칙표', ksub='옮기기 + 버리기')
    D.node('bkt', 444, 172, 148, 64, 'S3 버킷', '접두사·태그 대상', 'bucket', lay='side', k='창고', ksub='칸·꼬리표별')
    D.edge('sca', 'rule', '추천', k='알려 줌')
    D.edge('rule', 'bkt', '적용', k='붙이기', t='acc')
    return D


@reg('c13-events')
def _():
    D = Diagram('c13-events', w=600, at='권한은 대상 쪽 리소스 정책으로',
                cap='이벤트 알림은 SNS, SQS, Lambda 중 하나로 바로 보냅니다(알림 하나에 대상 하나). EventBridge 연동을 켜면 모든 이벤트가 EventBridge로 가고, 규칙으로 걸러 여러 대상(FIFO 포함)에 보냅니다.',
                kcap='알림 벨은 방송, 꽂이, 심부름꾼 중 한 곳에 바로 알려요. 도시 알림 센터와 이으면 모든 소식이 센터로 가고, 센터가 골라서 여러 곳에 전해요.')
    D.node('bkt', 8, 110, 130, 84, 'S3 버킷', 'images/*.jpg', 'bucket', t='hl', k='창고', ksub='사진 칸')
    D.group(184, 8, 212, 212, '이벤트 알림', k='알림 벨', solid=True)
    D.node('sns', 196, 38, 188, 46, 'SNS 표준 주제', None, 'bell', k='안내 방송')
    D.node('sqs', 196, 100, 188, 46, 'SQS 표준 대기열', None, 'queue', k='주문서 꽂이')
    D.node('lam', 196, 162, 188, 46, 'Lambda', None, 'lambda', k='심부름꾼', kicon='user')
    D.edge('bkt', 'sns', t='acc', sa='t', sb='l')
    D.edge('bkt', 'sqs', t='acc')
    D.edge('bkt', 'lam', t='acc')
    D.text(412, 60, '대상마다 리소스 정책으로', k='받는 쪽이 허락해야 해요')
    D.text(412, 78, 'S3의 호출을 허용', k='(리소스 정책)')
    D.text(412, 120, '알림 하나 = 대상 하나', k='벨 하나 = 받는 곳 하나')
    D.text(412, 138, 'FIFO는 직접 못 보냄', k='순서 꽂이는 바로 안 돼요')
    D.node('eb', 196, 256, 188, 68, 'EventBridge', '필터 · 여러 대상 · 재생', 'flow', t='hl', lay='side', k='도시 알림 센터', ksub='골라서 여러 곳에')
    D.node('sf', 440, 222, 152, 40, 'Step Functions', k='작업 순서 관리자')
    D.node('kin', 440, 270, 152, 40, 'Kinesis·Firehose', k='컨베이어 벨트')
    D.node('fifo', 440, 318, 152, 40, 'SQS FIFO', k='순서 지키는 꽂이')
    D.edge('bkt', 'eb', '모든 이벤트', k='모든 소식', t='acc', sa='b', sb='l')
    D.edge('eb', 'sf', t='acc', sa=('r', 0.2), sb='l')
    D.edge('eb', 'kin', t='acc')
    D.edge('eb', 'fifo', t='acc', sa=('r', 0.8), sb='l')
    return D


@reg('c13-performance')
def _():
    D = Diagram('c13-performance', w=600, at='다운로드를 빠르게',
                cap='먼 곳의 사용자가 큰 파일을 조각으로 나눠 가까운 엣지 로케이션에 병렬로 올리고, 엣지에서 버킷 리전까지는 AWS 전용망으로 옮깁니다. 멀티파트 업로드와 전송 가속을 함께 쓴 모습입니다.',
                kcap='먼 도시 손님이 큰 짐을 조각내 가까운 편의점에 동시에 맡기면, 편의점이 고속도로로 창고까지 보내요.')
    D.node('user', 8, 96, 104, 80, '사용자', '먼 나라', 'user', k='먼 도시 손님', ksub='큰 짐')
    D.group(140, 40, 120, 192, '멀티파트', k='조각내기', solid=True)
    for i in range(4):
        D.bar(152, 70 + i * 38, 96, 30, f'조각 {i + 1}', t='soft')
        D.arrow((250, 85 + i * 38), (298, 85 + i * 38), t='acc')
    D.arrow((112, 136), (138, 136), t='acc')
    D.node('edge', 300, 60, 120, 152, '엣지 로케이션', '가까운 곳', 'pin', t='hl', k='동네 편의점', ksub='가까운 곳')
    D.node('bkt', 500, 96, 92, 80, 'S3 버킷', '서울 리전', 'bucket', k='창고', ksub='서울')
    D.edge('edge', 'bkt', 'AWS 전용망', k='고속도로', t='acc')
    D.text(8, 256, '5GB 초과는 멀티파트 필수 · 100MB 이상 권장 · 전송 가속은 유료',
           k='아주 큰 짐은 꼭 조각내요 · 고속도로는 돈을 더 내요')
    return D


@reg('c13-performance:prefix')
def _():
    D = Diagram('c13-performance:prefix', w=560, at='업로드를 빠르게',
                cap='처리량 한도는 접두사마다 따로 있습니다. 접두사 네 개에 나누면 GET은 초당 22,000번, PUT은 14,000번까지 받을 수 있습니다.',
                kcap='칸마다 입구가 따로 있어서, 칸을 넷으로 나누면 네 배로 넣고 꺼낼 수 있어요.')
    for i, (p, kp) in enumerate([('a/', 'ㄱ 칸'), ('b/', 'ㄴ 칸'), ('c/', 'ㄷ 칸'), ('d/', 'ㄹ 칸')]):
        y = 16 + i * 38
        D.text(8, y + 20, f'my-bucket/{p}', k=kp, cls='lbl')
        D.bar(150, y, 200, 30, 'GET 5,500/초', k='꺼내기 5,500번/초', t='soft')
        D.bar(354, y, 130, 30, 'PUT 3,500/초', k='넣기 3,500번/초', t='muted')
    D.text(150, 186, '합계: GET 22,000/초 · PUT 14,000/초', k='모두 합치면: 꺼내기 22,000번 · 넣기 14,000번', cls='lbl')
    return D


@reg('c13-performance:range')
def _():
    D = Diagram('c13-performance:range', w=560, at='end:다운로드를 빠르게',
                cap='Range 헤더로 구간을 나눠 GET 요청 네 개를 동시에 보내고 받은 뒤 합칩니다. 실패한 구간만 다시 받고, 파일 앞부분만 필요하면 그 구간만 받습니다.',
                kcap='두꺼운 책을 네 사람이 쪽을 나눠 동시에 복사해 와요. 표지만 필요하면 표지만 복사해요.')
    D.bar(8, 16, 544, 32, 'video.mp4 · 2GB', k='두꺼운 책', t='store')
    for i, (s, ks) in enumerate([('0–499MB', '1–100쪽'), ('500–999MB', '101–200쪽'), ('1000–1499MB', '201–300쪽'), ('1500–1999MB', '301–400쪽')]):
        x = 8 + i * 136
        D.arrow((x + 67, 50), (x + 67, 82), t='acc')
        D.bar(x, 84, 134, 30, s, k=ks, t='soft')
    D.text(8, 140, 'GET 요청 4개를 동시에 → 합쳐서 빠르게, 실패한 구간만 다시', k='네 사람이 동시에 → 합치면 빨라요, 잘못된 쪽만 다시')
    D.bar(8, 156, 70, 30, '헤더', k='표지', t='ok')
    D.text(88, 176, 'Range: bytes=0-1023 → 앞 1KB만 읽어 파일 정보 확인', k='표지 한 장만 복사해서 무슨 책인지 확인')
    return D


@reg('c13-ops')
def _():
    D = Diagram('c13-ops', w=600, at='S3 Storage Lens',
                cap='S3 Inventory로 객체 목록을 만들고 Athena로 대상을 거른 뒤, 배치 작업이 객체마다 작업(예: 암호화 복사)이나 Lambda를 실행합니다. 끝나면 완료 보고서를 남깁니다.',
                kcap='재고표에서 목록을 뽑고, 자물쇠 없는 물건만 골라, 대량 작업반이 한꺼번에 일해요. 끝나면 결과표를 남겨요.')
    D.node('inv', 8, 40, 124, 80, 'S3 Inventory', '객체 목록', 'list', k='창고 재고표', ksub='물건 목록')
    D.node('ath', 158, 40, 124, 80, 'Athena', '암호화 안 된 것만', 'search', k='골라내기', ksub='자물쇠 없는 것')
    D.node('job', 308, 40, 124, 80, '배치 작업', '목록 + 할 일', 'gear', t='hl', k='대량 작업반', ksub='목록 + 할 일')
    D.node('obj', 458, 8, 134, 72, 'S3 객체', '수백만 개 처리', 'bucket', t='store', k='창고 물건', ksub='수백만 개')
    D.node('lam', 458, 104, 134, 72, 'Lambda', '사용자 지정 작업', 'lambda', k='심부름꾼', ksub='특별한 일', kicon='user')
    D.node('rep', 308, 172, 124, 56, '완료 보고서', '성공·실패 목록', k='결과표', ksub='한 일 목록')
    D.edge('inv', 'ath', t='acc')
    D.edge('ath', 'job', t='acc')
    D.edge('job', 'obj', t='acc')
    D.edge('job', 'lam', t='acc')
    D.edge('job', 'rep', '끝나면', k='끝나면')
    return D


@reg('c13-ops:pays')
def _():
    D = Diagram('c13-ops:pays', w=600, at='end:요청자 지불(Requester Pays)',
                cap='요청자 지불 버킷에서 저장료는 주인이, 요청과 내려받는 전송 비용은 인증된 요청자 계정이 냅니다. 익명 요청은 거부됩니다.',
                kcap='자리값은 주인이, 택배비는 가져가는 가입 손님이 내요. 이름을 밝히지 않은 손님은 못 가져가요.')
    D.node('own', 8, 30, 150, 64, '버킷 주인', '저장료만', 'user', lay='side', k='창고 주인', ksub='자리값만')
    D.node('bkt', 220, 30, 150, 64, 'S3 버킷', '요청자 지불 켬', 'bucket', t='hl', lay='side', k='창고', ksub='택배비는 손님이')
    D.node('req', 432, 30, 160, 64, '다른 AWS 계정', '요청·전송 비용', 'building', t='ok', lay='side', k='가입한 손님', ksub='택배비 냄')
    D.node('anon', 432, 130, 160, 52, '익명 사용자', '거부', 'globe', t='warn', lay='side', k='모르는 사람', ksub='못 가져감')
    D.edge('own', 'bkt', '저장', k='보관')
    D.edge('bkt', 'req', '다운로드', k='가져감', t='acc')
    D.edge('bkt', 'anon', '403', k='거절', t='bad', dash=True, sa='b', sb='l')
    return D


@reg('c13-ops:lens')
def _():
    D = Diagram('c13-ops:lens', w=600, at='end:S3 Storage Lens',
                cap='Storage Lens는 조직의 모든 계정과 리전, 버킷의 지표를 모아 대시보드로 보여 주고, 매일 S3 버킷으로 내보낼 수 있습니다. 무료 지표는 14일, 고급 지표는 15개월 보관합니다.',
                kcap='본사 상황판은 모든 지점의 창고를 모아 보여 주고, 매일 기록을 보관 창고에 남겨요.')
    D.group(8, 8, 330, 208, 'AWS Organizations', k='본사와 지점들', solid=True)
    D.group(20, 36, 148, 168, '계정 A', k='지점 가', lpos='bl')
    D.group(178, 36, 148, 168, '계정 B', k='지점 나', lpos='bl')
    D.node('a1', 32, 50, 124, 48, '버킷 · 서울', k='창고 · 서울')
    D.node('a2', 32, 110, 124, 48, '버킷 · 도쿄', k='창고 · 도쿄')
    D.node('b1', 190, 50, 124, 48, '버킷 · 서울', k='창고 · 서울')
    D.node('b2', 190, 110, 124, 48, '버킷 · 버지니아', k='창고 · 버지니아')
    D.arrow((340, 90), (378, 90), t='acc')
    D.node('dash', 380, 50, 212, 80, 'Storage Lens 대시보드', '사용량 · 비용 · 데이터 보호', 'chart', t='hl', k='본사 상황판', ksub='크기 · 비용 · 안전')
    D.node('exp', 380, 172, 212, 56, 'S3 버킷', '매일 CSV·Parquet 내보내기', 'bucket', lay='side', k='보관 창고', ksub='매일 상황 기록')
    D.edge('dash', 'exp', '내보내기', k='기록 남김')
    return D


@reg('c14-encryption')
def _():
    D = Diagram('c14-encryption', w=600, at='SSE-KMS와 KMS 요청 한도',
                cap='키를 누가 관리하느냐로 나눕니다. S3가 관리하면 SSE-S3, KMS 키를 쓰면 SSE-KMS와 DSSE-KMS, 고객이 AWS 밖에서 관리하면 SSE-C와 클라이언트 측 암호화입니다.',
                kcap='열쇠를 창고가 갖고 있나, 열쇠 보관소에 있나, 손님이 갖고 있나로 나눠요.')
    D.group(8, 8, 188, 220, 'S3가 키 관리', k='창고가 열쇠 관리', solid=True)
    D.node('s3', 20, 44, 164, 72, 'SSE-S3', '기본값 · AES-256', 'lock', t='ok', lay='side', k='창고 자물쇠', ksub='말 안 해도 채움')
    D.group(206, 8, 188, 220, 'KMS가 키 관리', k='열쇠 보관소', solid=True)
    D.node('kms', 218, 44, 164, 72, 'SSE-KMS', '감사 · 권한 통제', 'key', t='hl', lay='side', k='보관소 열쇠', ksub='빌린 기록 남음')
    D.node('dsse', 218, 132, 164, 72, 'DSSE-KMS', '두 겹 암호화', 'key', lay='side', k='자물쇠 두 개', ksub='규칙 엄한 곳')
    D.group(404, 8, 188, 220, '고객이 키 관리', k='손님이 열쇠 관리', solid=True)
    D.node('ssec', 416, 44, 164, 72, 'SSE-C', 'HTTPS 필수\n새 버킷은 기본 차단', 'key', t='warn', lay='side', k='내 열쇠 가져옴', ksub='잠긴 트럭만\n새 창고는 막아 둠')
    D.node('cse', 416, 132, 164, 72, '클라이언트 측', '올리기 전에 암호화', 'user', lay='side', k='집에서 잠가 옴', ksub='창고는 내용 모름')
    D.text(8, 252, 'SSE-KMS: 업로드마다 GenerateDataKey, 다운로드마다 Decrypt 호출 → KMS 초당 한도에 포함',
           k='보관소 열쇠는 넣고 꺼낼 때마다 창구에 들러요. 창구는 1초에 받는 손님 수가 정해져 있어요')
    return D


@reg('c14-encryption:kms')
def _():
    D = Diagram('c14-encryption:kms', w=600, at='end:SSE-KMS와 KMS 요청 한도',
                cap='SSE-KMS 버킷은 업로드 때 GenerateDataKey, 다운로드 때 Decrypt를 KMS에 요청합니다. S3 버킷 키를 켜면 버킷 단위 키를 잠시 받아 쓰므로 KMS 호출이 크게 줄어듭니다.',
                kcap='넣고 꺼낼 때마다 보관소 창구에 가면 줄이 생겨요. 창고용 임시 열쇠를 받아 두면 창구에 덜 가요.')
    D.node('app', 8, 60, 130, 80, '앱', 'PUT / GET', 'browser', k='손님', ksub='넣기 / 꺼내기')
    D.node('s3', 196, 60, 140, 80, 'S3', 'SSE-KMS 버킷', 'bucket', k='창고', ksub='보관소 열쇠 사용')
    D.node('kms', 452, 60, 140, 80, 'KMS', '초당 10,000~100,000', 'key', t='hl', k='열쇠 보관소', ksub='창구 손님 수 제한')
    D.node('bk', 196, 184, 140, 56, 'S3 버킷 키', 'KMS 호출 최대 99% ↓', t='ok', k='창고용 임시 열쇠', ksub='창구에 덜 감')
    D.edge('app', 's3', 'HTTPS', k='잠금', t='acc')
    D.edge('s3', 'kms', 'GenerateDataKey', k='열쇠 빌리기', t='acc', sa=('r', 0.3), sb=('l', 0.3))
    D.edge('kms', 's3', 'Decrypt', k='열쇠로 열기', sa=('l', 0.75), sb=('r', 0.75))
    D.edge('s3', 'bk', '켜면', k='켜면', dash=True)
    D.edge('bk', 'kms', '가끔만 호출', k='가끔만', dash=True, sa='r', sb='b')
    D.text(8, 272, '읽는 사람에게 S3 권한과 함께 그 KMS 키의 kms:Decrypt 권한도 있어야 합니다',
           k='꺼내는 사람은 창고 허락과 보관소 열쇠 허락이 모두 있어야 해요')
    return D


@reg('c14-cors-presigned')
def _():
    D = Diagram('c14-cors-presigned', w=600, at='end:CORS',
                cap='브라우저가 my-html의 페이지를 받은 뒤(①), 다른 출처인 my-assets의 이미지를 부르기 전에 사전 요청을 보냅니다(②). my-assets의 CORS 규칙이 그 출처를 허락하면(③) 실제 요청을 보냅니다(④).',
                kcap='진열장 가게 안내문을 받은 손님 브라우저가, 옆 창고에 "가져가도 돼요?" 하고 먼저 묻고, 허락 안내를 받은 뒤에 사진을 가져와요.')
    D.node('br', 8, 100, 110, 80, '브라우저', '사용자', 'browser', k='손님 브라우저', ksub='손님')
    D.node('html', 330, 8, 262, 72, 'my-html 버킷', '웹사이트 www.example.com', 'bucket', lay='side', k='진열장 가게', ksub='안내문 페이지')
    D.node('as', 330, 172, 262, 92, 'my-assets 버킷', 'CORS: www.example.com 허용', 'bucket', t='hl', lay='side', k='옆 창고', ksub='"이 가게는 가져가도 됨"')
    D.edge('br', 'html', '① 페이지', k='① 가게 안내문', lp=-1)
    D.edge('br', 'as', '② 사전 요청', k='② 먼저 물어보기', dash=True, sa=('r', 0.85), sb=('l', 0.25), via=[(190, 168), (190, 195)], lp=-1)
    D.edge('as', 'br', '③ 허용 헤더', k='③ 허락 안내', t='ok', sa=('l', 0.587), sb=('b', 0.5), via=[(63, 226)], lp=0)
    D.edge('br', 'as', '④ 이미지 GET', k='④ 사진 가져오기', t='acc', sa=('b', 0.8), sb=('l', 0.935), via=[(96, 258)], lp=-1)
    D.text(8, 300, '② OPTIONS 요청에 Origin 헤더 → ③ Access-Control-Allow-Origin으로 허락',
           k='② "이 가게에서 왔어요" → ③ "그 가게는 가져가도 돼요"')
    return D


@reg('c14-cors-presigned:url')
def _():
    D = Diagram('c14-cors-presigned:url', w=600, at='end:미리 서명된 URL(Pre-signed URL)',
                cap='앱 서버가 자기 IAM 권한으로 서명한 URL을 만들어 사용자에게 주면(②), 사용자는 비공개 버킷에서 정해진 시간 동안 직접 내려받습니다(③). 버킷은 공개하지 않습니다.',
                kcap='창고 주인이 시간 제한 쪽지에 서명해 주면, 손님은 쪽지를 보여 주고 닫힌 창고에서 물건을 가져가요.')
    D.node('u', 8, 90, 120, 72, '사용자', '로그인함', 'user', k='손님', ksub='가입함')
    D.node('app', 220, 8, 170, 72, '앱 서버', 'IAM 역할로 서명', 'server', lay='side', k='창고 주인', ksub='쪽지에 서명')
    D.node('b', 440, 90, 152, 72, 'S3 버킷', '비공개', 'bucket', t='hl', lay='side', k='창고', ksub='문은 닫혀 있음')
    D.edge('u', 'app', '① 요청', k='① 부탁', sa=('t', 0.3), sb=('l', 0.3), lp=-1)
    D.edge('app', 'u', '② 서명된 URL', k='② 시간 제한 쪽지', t='acc', sa=('l', 0.75), sb=('t', 0.75), lp=0)
    D.edge('u', 'b', '③ URL로 GET', k='③ 쪽지 보여 주기', t='acc')
    D.text(8, 196, 'URL에는 서명과 만료 시각이 담김 · 콘솔은 12시간, CLI·SDK는 7일까지',
           k='쪽지에는 주인 서명과 끝나는 시각이 적혀 있어요')
    return D


@reg('c14-mfa-logs')
def _():
    D = Diagram('c14-mfa-logs', w=600, at='서버 액세스 로그',
                cap='MFA Delete를 켜면 버전 영구 삭제와 버전 관리 일시 중지에 MFA 코드가 필요합니다. 켜고 끄는 일은 루트 사용자만 CLI·SDK·API로 합니다.',
                kcap='옛 물건까지 완전히 버리거나 쌓아 두기를 멈추려면 휴대폰 인증 번호가 있어야 해요.')
    D.node('root', 8, 30, 150, 64, '루트 사용자', 'MFA 코드 + CLI', 'idcard', t='ok', lay='side', k='창고 사장님', ksub='인증 번호 있음')
    D.node('other', 8, 116, 150, 64, '다른 사용자', 'MFA 코드 없음', 'user', t='warn', lay='side', k='다른 직원', ksub='인증 번호 없음')
    D.group(320, 8, 272, 190, 'S3 버킷 · MFA Delete', k='창고 · 인증 번호 규칙', solid=True)
    D.node('vdel', 334, 40, 244, 56, '버전 영구 삭제', 'MFA 코드 필요', t='hl', k='옛 물건 완전히 버리기', ksub='인증 번호 필요')
    D.node('susp', 334, 120, 244, 56, '버전 관리 일시 중지', 'MFA 코드 필요', t='hl', k='쌓아 두기 멈추기', ksub='인증 번호 필요')
    D.edge('root', 'vdel', '허용', k='됨', t='ok')
    D.edge('other', 'susp', '거부', k='안 됨', t='bad', dash=True)
    D.text(8, 222, 'MFA 없이 되는 일: 버전 관리 켜기, 삭제된 버전 목록 보기', k='인증 번호 없이 되는 일: 쌓아 두기 켜기, 버린 물건 목록 보기')
    D.text(8, 242, '켜고 끄기: 루트 사용자만, 버전 관리가 켜진 버킷에서', k='이 규칙은 사장님만 켜고 꺼요')
    return D


@reg('c14-mfa-logs:logs')
def _():
    D = Diagram('c14-mfa-logs:logs', w=600, at='end:서버 액세스 로그',
                cap='감시 버킷의 모든 요청 기록은 같은 리전의 다른 로그 버킷에 쌓이고, Athena로 분석합니다. 로그를 감시 버킷 자신에 쓰면 로그 쓰기가 또 로그를 만들어 끝없이 커집니다.',
                kcap='방문 기록장은 다른 창고에 두고 돋보기로 찾아봐요. 같은 창고에 두면 기록장이 끝없이 두꺼워져요.')
    D.node('src', 8, 30, 150, 72, '감시 버킷', '모든 요청 기록', 'bucket', lay='side', k='창고', ksub='드나든 사람')
    D.node('log', 240, 30, 150, 72, '로그 버킷', '같은 리전', 'bucket', t='hl', lay='side', k='기록장 창고', ksub='같은 도시')
    D.node('ath', 450, 30, 142, 72, 'Athena', 'SQL로 분석', 'search', lay='side', k='돋보기', ksub='찾아보기')
    D.edge('src', 'log', '로그 전달', k='기록', t='acc')
    D.edge('log', 'ath', '조회', k='찾기')
    D.node('bad1', 8, 150, 150, 56, '버킷 A', '로그도 A에 씀', t='warn', k='창고 가', ksub='기록장도 가에')
    D.node('bad2', 240, 150, 150, 56, '로그 쓰기', '또 요청이 됨', t='warn', k='기록 적기', ksub='또 드나듦')
    D.edge('bad1', 'bad2', '로그', k='기록', t='bad')
    D.edge('bad2', 'bad1', '또 기록', k='또 기록', t='bad', sa=('b', 0.5), sb=('b', 0.5), via=[(315, 236), (83, 236)])
    D.text(412, 182, '같은 버킷이면 끝없이 커짐', k='같은 창고면 끝없이 두꺼워져요')
    return D


@reg('c14-lock')
def _():
    D = Diagram('c14-lock', w=600, at='end:S3 객체 잠금(Object Lock)',
                cap='규정 준수 모드는 루트 사용자를 포함해 아무도 지우지 못하고, 거버넌스 모드는 우회 권한이 있는 사용자만 지울 수 있습니다. 법적 보존은 기간 없이 해제할 때까지 막습니다.',
                kcap='엄격한 금고는 사장님도 못 열고, 관리자 열쇠 금고는 특별 열쇠가 있으면 열려요. "재판 중" 딱지는 뗄 때까지 못 버려요.')
    rows = [
        ('루트 사용자 포함', '삭제·덮어쓰기 시도', '사장님도', '버리려 함', 'v1 · 규정 준수', '보존 기간 동안', '엄격한 금고', '정한 날까지', '거부', '기간 단축도 불가', '못 버림', '날짜도 못 당김', False),
        ('관리자', '우회 권한 있음', '관리자', '특별 열쇠 있음', 'v1 · 거버넌스', '보존 기간 동안', '관리자 열쇠 금고', '정한 날까지', '허용', '권한으로 우회', '버릴 수 있음', '특별 열쇠로', True),
        ('일반 사용자', '우회 권한 없음', '보통 직원', '특별 열쇠 없음', 'v1 · 거버넌스', '보존 기간 동안', '관리자 열쇠 금고', '정한 날까지', '거부', '보호됨', '못 버림', '지켜짐', False),
        ('누구나', '삭제 시도', '누구나', '버리려 함', 'v1 · 법적 보존', '기간 없음', '"재판 중" 딱지', '날짜 없음', '거부', '해제 전까지', '못 버림', '딱지 뗄 때까지', False),
    ]
    for i, (w, ws, kw, kws, o, os_, ko, kos, r, rs, kr, krs, ok) in enumerate(rows):
        y = 16 + i * 80
        D.node(f'w{i}', 8, y, 170, 64, w, ws, 'user', lay='side', k=kw, ksub=kws)
        D.node(f'o{i}', 220, y, 180, 64, o, os_, 'lock', t='hl', lay='side', k=ko, ksub=kos)
        D.node(f'r{i}', 442, y, 150, 64, r, rs, 'check' if ok else 'xmark', t='ok' if ok else 'warn', lay='side', k=kr, ksub=krs)
        D.edge(f'w{i}', f'o{i}')
        D.edge(f'o{i}', f'r{i}', t='ok' if ok else 'bad')
    return D


@reg('c14-access-points')
def _():
    D = Diagram('c14-access-points', w=600, at='S3 Object Lambda',
                cap='팀마다 액세스 포인트를 두고 정책을 따로 겁니다. 분석팀 액세스 포인트는 두 접두사를 읽기만 하고, VPC 출처 액세스 포인트는 VPC 안에서만(VPC 엔드포인트 경유) 쓸 수 있습니다.',
                kcap='팀마다 전용 입구를 내고 입구마다 안내를 붙여요. 단지 안에서만 쓰는 입구도 있어요.')
    teams = [('fin', '재무팀', '재무팀', 'ap1', 'finance-ap', '/finance 읽기·쓰기', '재무팀 입구', '재무 칸 넣기·꺼내기'),
             ('sal', '영업팀', '영업팀', 'ap2', 'sales-ap', '/sales 읽기·쓰기', '영업팀 입구', '영업 칸 넣기·꺼내기'),
             ('ana', '분석팀', '분석팀', 'ap3', 'analytics-ap', '두 접두사 읽기만', '분석팀 입구', '두 칸 보기만')]
    for i, (tk, tl, ktl, ak, al, asub, kal, kasub) in enumerate(teams):
        y = 16 + i * 68
        D.node(tk, 8, y, 140, 52, tl, None, 'users', k=ktl)
        D.node(ak, 190, y, 186, 52, al, asub, t='hl', k=kal, ksub=kasub)
        D.edge(tk, ak, t='acc')
    D.group(8, 220, 146, 92, 'VPC', k='우리 단지', lpos='bl')
    D.node('ec2', 16, 232, 130, 44, 'EC2 앱', None, 'server', k='작업실')
    D.node('ap4', 190, 228, 186, 52, 'vpc-ap', 'VPC 출처만', t='hl', k='단지 전용 입구', ksub='단지 안에서만')
    D.edge('ec2', 'ap4', t='acc')
    D.node('b', 420, 16, 172, 264, 'S3 버킷', '/finance · /sales', 'bucket', t='store', k='큰 창고', ksub='재무 칸 · 영업 칸')
    for ak in ('ap1', 'ap2', 'ap3', 'ap4'):
        D.edge(ak, 'b', t='acc')
    D.text(190, 304, 'VPC 출처는 VPC 엔드포인트 필요', k='단지 전용 입구는 단지 통로가 필요해요')
    return D


@reg('c14-access-points:olambda')
def _():
    D = Diagram('c14-access-points:olambda', w=600, at='end:S3 Object Lambda',
                cap='분석 앱은 Object Lambda 액세스 포인트로 요청하고, Lambda가 S3 액세스 포인트로 원본을 가져와 개인정보를 가린 뒤 돌려줍니다. 주문 앱은 S3 액세스 포인트로 원본을 그대로 읽습니다.',
                kcap='분석팀이 손질 입구로 오면 심부름꾼이 원본을 꺼내 전화번호를 가려서 줘요. 주문팀은 보통 입구에서 원본을 받아요.')
    D.node('b', 8, 16, 130, 72, 'S3 버킷', '원본 하나', 'bucket', t='store', lay='side', k='창고', ksub='원본 명단')
    D.node('ap', 176, 16, 150, 72, 'S3 액세스 포인트', '보통 입구', k='창고 입구', ksub='보통 입구')
    D.node('lam', 364, 16, 228, 72, 'Lambda', '개인정보 가리기 · 형식 변환', 'lambda', t='hl', lay='side', k='손질 담당 심부름꾼', ksub='전화번호 가리기', kicon='user')
    D.node('olap', 364, 130, 228, 72, 'Object Lambda 액세스 포인트', '분석 앱용', k='손질 입구', ksub='분석팀용')
    D.node('app', 176, 130, 150, 72, '분석 앱', '가린 데이터', 'chart', lay='side', k='분석팀', ksub='가린 명단')
    D.node('app2', 8, 130, 130, 72, '주문 앱', '원본 데이터', 'browser', lay='side', k='주문팀', ksub='원본 명단')
    D.edge('b', 'ap', t='acc')
    D.edge('ap', 'lam', t='acc')
    D.edge('lam', 'olap', '가린 결과', k='가린 명단', t='acc')
    D.edge('olap', 'app', t='acc')
    D.edge('ap', 'app2', '원본', k='원본', sa='b', sb='t')
    return D
