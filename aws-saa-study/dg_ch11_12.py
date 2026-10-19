from dg import Diagram, reg


@reg('c11-stateless')
def _():
    D = Diagram('c11-stateless', w=600, at='이 사례에서 배운 것',
                cap='완성된 구조입니다. 사용자는 Route 53 Alias로 ELB에 오고, ELB는 상태 확인을 통과한 EC2에만 보냅니다. ASG가 두 AZ에 걸쳐 대수를 조절하고, 늘 필요한 최소 용량은 예약 인스턴스로 삽니다.',
                kcap='손님은 주소 안내소를 거쳐 안내 데스크로 와요. 매니저가 두 동네의 작업실 수를 맞추고, 늘 쓰는 작업실은 1년 약속으로 싸게 빌려요.')
    D.node('user', 16, 10, 150, 52, '사용자', None, 'users', k='손님')
    D.node('r53', 16, 110, 140, 64, 'Route 53', 'Alias → ELB', 'globe', t='hl', lay='side', k='주소 안내소', ksub='데스크 연결')
    D.node('elb', 210, 110, 140, 64, 'ELB', '상태 확인', 'lb', t='hl', lay='side', k='안내 데스크', ksub='"괜찮아요?"')
    D.group(372, 8, 220, 276, 'ASG · 다중 AZ', k='매니저가 조절', solid=True)
    D.group(380, 36, 204, 112, 'AZ a', k='동네 가', lpos='bl')
    D.group(380, 160, 204, 112, 'AZ b', k='동네 나', lpos='bl')
    D.node('a0', 390, 50, 84, 56, 'EC2', '예약', k='작업실', ksub='1년 약속')
    D.node('a1', 490, 50, 84, 56, 'EC2', '온디맨드', k='작업실', ksub='그날 빌림')
    D.node('b0', 390, 174, 84, 56, 'EC2', '예약', k='작업실', ksub='1년 약속')
    D.node('b1', 490, 174, 84, 56, 'EC2', '스팟', k='작업실', ksub='남는 방')
    D.edge('user', 'r53', 'DNS 조회', k='주소 묻기')
    D.edge('r53', 'elb', 'Alias', k='가리킴', t='acc')
    D.edge('elb', 'a0', t='acc', sa=('r', 0.3), via=[(361, 129), (361, 78)])
    D.edge('elb', 'b0', t='acc', sa=('r', 0.7), via=[(361, 155), (361, 202)])
    D.edge('a0', 'a1', dash=True)
    D.edge('b0', 'b1', dash=True)
    D.bar(16, 206, 334, 30, '늘 필요한 최소 용량 → 예약', k='늘 쓰는 작업실 → 1년 약속', t='ok')
    D.bar(16, 244, 334, 30, '넘는 부분 → 온디맨드·스팟', k='바쁠 때만 → 그날 빌림', t='soft')
    D.text(16, 306, '보안 그룹 사슬: 인터넷 → ELB(80·443) → EC2(ELB 보안 그룹만 허용)',
           k='문지기 규칙: 바깥 손님 → 데스크 → 작업실(데스크가 보낸 손님만)')
    return D


@reg('c11-stateful')
def _():
    D = Diagram('c11-stateful', w=600, at='end:MyClothes.com',
                cap='쿠키에는 세션 ID만 두고 장바구니는 ElastiCache에 둡니다. 어느 EC2로 가도 같은 세션을 찾으므로 EC2는 무상태가 됩니다. 사용자 정보는 RDS 다중 AZ에 쓰고, 읽기는 읽기 전용 복제본으로 나눕니다.',
                kcap='손님은 번호표만 들고 와요. 어느 작업실에 가도 공용 메모판에서 장바구니를 찾아요. 주소 같은 기록은 기록실에, 보는 일은 열람용 복사본에서 해요.')
    D.node('user', 8, 100, 100, 56, '사용자', None, 'users', k='손님')
    D.node('elb', 124, 96, 130, 64, 'ELB', '다중 AZ', 'lb', t='hl', lay='side', k='안내 데스크', ksub='두 동네')
    D.group(270, 16, 120, 228, 'ASG · 다중 AZ', k='매니저가 조절', solid=True)
    D.node('e1', 282, 48, 96, 52, 'EC2', '무상태', k='작업실', ksub='기억 안 함')
    D.node('e2', 282, 112, 96, 52, 'EC2', '무상태', k='작업실', ksub='기억 안 함')
    D.node('e3', 282, 180, 96, 52, 'EC2', '무상태', k='작업실', ksub='기억 안 함')
    D.node('cache', 440, 30, 152, 64, 'ElastiCache', '세션 데이터', 'bolt', t='hl', lay='side', k='공용 메모판', ksub='장바구니')
    D.node('rds', 440, 128, 152, 64, 'RDS 다중 AZ', '사용자 정보', 'db', t='store', lay='side', k='기록실', ksub='손님 주소')
    D.node('rep', 440, 220, 152, 56, '읽기 전용 복제본', '최대 15개', k='열람용 복사본', ksub='보기만')
    D.edge('user', 'elb', t='acc')
    D.edge('elb', 'e1', t='acc', sa=('r', 0.25))
    D.edge('elb', 'e2', t='acc')
    D.edge('elb', 'e3', t='acc', sa=('r', 0.75))
    D.edge('e1', 'cache', '세션', k='메모', both=True)
    D.edge('e2', 'rds', '쓰기', k='적기')
    D.edge('e3', 'rep', '읽기', k='보기')
    D.edge('rds', 'rep', '복제', k='복사', dash=True)
    D.text(8, 192, '쿠키에는 세션 ID만', k='손님은 번호표만')
    D.text(8, 304, '보안 그룹 사슬: ELB ← 인터넷 · EC2 ← ELB · RDS와 ElastiCache ← EC2',
           k='문지기 규칙: 데스크는 누구나, 작업실은 데스크만, 기록실과 메모판은 작업실만')
    return D


@reg('c11-stateful:wp')
def _():
    D = Diagram('c11-stateful:wp', w=600, at='end:MyWordPress.com',
                cap='EBS는 인스턴스 하나에만 붙으므로, 사진을 올린 서버가 아닌 다른 서버로 요청이 가면 사진이 없습니다. EFS는 여러 AZ의 EC2가 함께 마운트하므로 어느 서버로 가도 같은 사진이 보입니다.',
                kcap='개인 사물함에 넣은 사진은 다른 작업실에서 못 찾아요. 공용 서류실에 넣으면 어느 작업실에서든 찾아요.')
    D.group(8, 8, 288, 214, '사진을 EBS에', k='개인 사물함에', solid=True)
    D.node('a1', 24, 48, 112, 52, 'EC2 1', '사진 올림', k='작업실 1', ksub='사진 받음')
    D.node('a2', 168, 48, 112, 52, 'EC2 2', '사진 요청', k='작업실 2', ksub='사진 찾음')
    D.node('v1', 24, 150, 112, 56, 'EBS 1', 'cat.jpg 있음', t='ok', k='개인 사물함 1', ksub='사진 있음')
    D.node('v2', 168, 150, 112, 56, 'EBS 2', '사진 없음', t='warn', k='개인 사물함 2', ksub='사진 없음')
    D.edge('a1', 'v1', '저장', k='넣기', t='ok')
    D.edge('a2', 'v2', '찾기 실패', k='못 찾음', t='bad', dash=True)
    D.group(304, 8, 288, 214, '사진을 EFS에', k='공용 서류실에', solid=True)
    D.node('c1', 320, 48, 112, 52, 'EC2 1', 'AZ a', k='작업실 1', ksub='가 동네')
    D.node('c2', 464, 48, 112, 52, 'EC2 2', 'AZ b', k='작업실 2', ksub='나 동네')
    D.node('efs', 360, 150, 176, 56, 'EFS', '모두 같은 사진', 'folder', t='ok', k='공용 서류실', ksub='모두 같은 사진')
    D.edge('c1', 'efs', 'NFS 마운트', k='함께 열기', t='acc', both=True)
    D.edge('c2', 'efs', t='acc', both=True)
    return D


@reg('c11-beanstalk')
def _():
    D = Diagram('c11-beanstalk', w=600, at='end:Elastic Beanstalk',
                cap='개발자는 코드만 올리고, Beanstalk이 웹 서버 환경(ELB + ASG)과 작업자 환경(SQS + ASG)을 만듭니다. 웹 서버는 오래 걸리는 작업을 SQS에 넣고, 작업자가 꺼내 처리합니다.',
                kcap='사장님은 레시피만 건네요. 업체가 손님 받는 가게와 뒷방 작업장을 꾸미고, 가게는 오래 걸리는 일을 주문서 꽂이에 꽂아 뒷방에 넘겨요.')
    D.node('dev', 8, 8, 130, 56, '개발자', '코드만 올림', 'user', lay='side', k='사장님', ksub='레시피만 건넴')
    D.node('eb', 8, 120, 130, 100, 'Elastic\nBeanstalk', '앱·버전·환경', 'rocket', t='hl', k='인테리어\n업체 패키지', ksub='알아서 꾸밈')
    D.group(300, 8, 292, 106, '웹 서버 환경', k='손님 받는 가게', solid=True)
    D.node('elb', 312, 40, 96, 56, 'ELB', '요청 받기', k='안내 데스크', ksub='손님 받기')
    D.node('web', 420, 40, 160, 56, 'ASG + EC2', '자동 확장', k='매니저 + 작업실', ksub='알아서 늘림')
    D.group(300, 140, 292, 112, '작업자 환경', k='뒷방 작업장', solid=True, lpos='bl')
    D.node('sqs', 312, 156, 96, 56, 'SQS 대기열', '작업 쌓임', k='주문서 꽂이', ksub='일 쌓임')
    D.node('wrk', 420, 156, 160, 56, 'ASG + EC2', '대기열 길이로 확장', k='매니저 + 작업자', ksub='꽂이가 차면 늘림')
    D.edge('dev', 'eb', '코드 업로드', k='레시피')
    D.edge('eb', 'elb', '만들기', k='꾸미기', sa=('r', 0.2), sb='l')
    D.edge('eb', 'sqs', '만들기', k='꾸미기')
    D.edge('elb', 'web', t='acc')
    D.edge('web', 'sqs', '작업 넣기', k='주문서 꽂기', t='acc', sa=('b', 0.25), sb='t')
    D.edge('sqs', 'wrk', t='acc')
    return D


@reg('c11-beanstalk:fast')
def _():
    D = Diagram('c11-beanstalk:fast', w=560, at='end:애플리케이션을 빨리 띄우는 방법',
                cap='부팅한 뒤 무엇을 하느냐에 따라 서비스 시작이 달라집니다. 골든 AMI는 설치가 끝난 상태로 부팅하고, 사용자 데이터는 바뀌는 설정만 적용합니다. DB와 디스크는 스냅샷에서 복원하면 데이터가 이미 들어 있습니다.',
                kcap='책상이 다 놓인 설계도로 열면 바로 손님을 받아요. 오늘의 메뉴 쪽지만 붙이면 돼요.')
    rows = [
        ('처음부터 설치', '처음부터 조립', [(60, '부팅', '문 열기', 'muted'), (190, '패키지·앱 설치 (수 분)', '책상 조립 (오래)', 'warn'), (76, '설정', '메뉴 쪽지', 'soft')], 'ok'),
        ('골든 AMI', '다 놓인 설계도', [(60, '부팅', '문 열기', 'muted')], 'ok'),
        ('골든 AMI + 사용자 데이터', '설계도 + 쪽지', [(60, '부팅', '문 열기', 'muted'), (76, '설정', '메뉴 쪽지', 'soft')], 'ok'),
        ('RDS·EBS 스냅샷 복원', '기록 사진으로 채우기', [(76, '복원', '채우기', 'muted')], 'ok'),
    ]
    for i, (lab, klab, segs, _) in enumerate(rows):
        y = 16 + i * 52
        D.text(8, y + 20, lab, k=klab, cls='lbl')
        x = 196
        for w, s, ks, t in segs:
            D.bar(x, y, w, 30, s, k=ks, t=t)
            x += w + 2
        if 552 - x >= 70:
            D.bar(x, y, 552 - x, 30, '서비스', k='손님 받기', t='ok')
    D.text(196, 228, '왼쪽에서 오른쪽으로 시간이 흐릅니다', k='왼쪽에서 오른쪽으로 시간이 흘러요')
    return D


@reg('c12-s3')
def _():
    D = Diagram('c12-s3', w=600, at='end:객체와 키',
                cap='s3://my-bucket/photos/2026/cat.jpg에서 버킷은 my-bucket, 키는 photos/2026/cat.jpg입니다. 키의 앞부분이 접두사이고, 콘솔은 접두사의 /를 폴더처럼 보여 줍니다. 버킷은 리전 하나에 있습니다.',
                kcap='창고 동 이름 뒤에 긴 번호표가 붙어요. 번호표의 "/"를 칸처럼 보여 줄 뿐 진짜 칸막이는 없어요.')
    D.bar(8, 20, 150, 34, 's3://my-bucket', k='가나다창고', t='acc')
    D.bar(160, 20, 140, 34, 'photos/2026/', k='사진/2026/', t='soft')
    D.bar(302, 20, 110, 34, 'cat.jpg', k='고양이 사진', t='store')
    D.bar(8, 58, 150, 26, '버킷', k='창고 동')
    D.bar(160, 58, 252, 26, '키 = 접두사 + 객체 이름', k='번호표 = 앞부분 + 물건 이름')
    D.group(8, 104, 428, 144, '리전: 서울(ap-northeast-2)', k='도시: 서울', solid=True)
    D.group(20, 132, 404, 104, 'my-bucket', k='가나다창고 동', lpos='tl')
    D.node('o1', 32, 160, 124, 60, 'cat.jpg', 'photos/2026/', t='store', k='고양이 사진', ksub='사진/2026/')
    D.node('o2', 164, 160, 124, 60, 'app.log', 'logs/', t='store', k='일지', ksub='기록/')
    D.node('o3', 296, 160, 116, 60, 'index.html', '접두사 없음', t='store', k='첫 안내문', ksub='앞부분 없음')
    D.node('app', 460, 160, 132, 60, '앱·사용자', 'PUT · GET', 'browser', lay='side', k='손님', ksub='넣기 · 꺼내기')
    D.edge('app', 'o3', t='acc', both=True)
    D.text(8, 272, '객체 하나 최대 50TB · PUT 한 번에 5GB까지 · 넘으면 멀티파트 업로드',
           k='물건 하나는 아주 커도 돼요 · 큰 물건은 조각내서 넣어요')
    return D


@reg('c12-policy')
def _():
    D = Diagram('c12-policy', w=600, at='누가 무엇으로 들어오나',
                cap='같은 계정은 IAM 정책이나 버킷 정책 중 하나만 허용해도 되고, 다른 계정은 양쪽 모두 허용해야 합니다. 인터넷 공개는 퍼블릭 액세스 차단을 끄고 버킷 정책으로 공개 읽기를 줘야 합니다. 어디에든 명시적 Deny가 있으면 거부됩니다.',
                kcap='우리 직원은 한쪽만 허락하면 되고, 옆 가게 직원은 양쪽 다 허락해야 해요. 지나가는 사람은 잠금장치를 풀고 "누구나 구경" 안내문을 붙여야 들어와요.')
    rows = [
        ('u1', '같은 계정', '사용자·역할', 'user', '우리 직원', '같은 가게',
         'c1', '둘 중 하나만 허용', 'IAM 정책 또는 버킷 정책', '한쪽만 허락', '출입증 규칙표 또는 문 안내문', 'ok'),
        ('u2', '다른 계정', '사용자·역할', 'building', '옆 가게 직원', '다른 가게',
         'c2', '양쪽 모두 허용', '그 계정 IAM 정책 + 버킷 정책', '양쪽 다 허락', '그 가게 규칙표 + 우리 문 안내문', 'plain'),
        ('u3', '인터넷 누구나', 'Principal: *', 'globe', '지나가는 사람', '누구나',
         'c3', '퍼블릭 액세스 차단 끔', '+ 버킷 정책 공개 읽기', '잠금장치 풀기', '+ "누구나 구경" 안내문', 'warn'),
    ]
    for i, (uk, ul, us, ui, kul, kus, ck, cl, cs, kcl, kcs, ct) in enumerate(rows):
        y = 16 + i * 84
        D.node(uk, 8, y, 150, 60, ul, us, ui, lay='side', k=kul, ksub=kus)
        D.node(ck, 186, y, 236, 60, cl, cs, t=ct, k=kcl, ksub=kcs)
        D.edge(uk, ck)
    D.node('b', 472, 16, 120, 228, 'S3 버킷', '접근 허용', 'bucket', t='hl', k='창고', ksub='문 열림')
    for ck in ('c1', 'c2', 'c3'):
        D.edge(ck, 'b', '허용', k='들어감', t='acc')
    D.text(8, 276, '어디에든 명시적 Deny가 있으면 거부 · 새 버킷은 ACL이 꺼져 있음',
           k='어디에든 "절대 안 돼"가 있으면 못 들어가요')
    return D


@reg('c12-website')
def _():
    D = Diagram('c12-website', w=600, at='end:켜는 방법',
                cap='웹사이트 엔드포인트로 직접 받으면 HTTP만 되고 버킷을 공개해야 합니다(아니면 403). 운영에서는 CloudFront를 앞에 두어 HTTPS와 도메인, 캐시를 붙이고 버킷은 비공개로 두어 CloudFront만 읽게 합니다(OAC).',
                kcap='진열장에 손님이 바로 오면 보통 길로만 오고 문을 활짝 열어야 해요. 앞에 편의점을 세우면 잠긴 트럭도 받고, 창고 문은 편의점에만 열어 줘요.')
    D.group(8, 8, 584, 110, '직접: S3 웹사이트 엔드포인트', k='진열장으로 바로', solid=True)
    D.node('u1', 20, 46, 118, 56, '브라우저', None, 'browser', k='손님')
    D.node('ep', 200, 46, 182, 56, '웹사이트 엔드포인트', 'HTTP만 · 공개 읽기 필요', k='진열장 입구', ksub='보통 길만 · 문 활짝')
    D.node('b1', 424, 46, 156, 56, 'S3 버킷', 'index.html · error.html', t='store', k='진열장 창고', ksub='첫 안내문 · 길 잃음')
    D.edge('u1', 'ep', 'HTTP', k='보통 길')
    D.edge('ep', 'b1')
    D.group(8, 132, 584, 110, '운영 권장: CloudFront 앞단', k='앞에 편의점 세우기', solid=True)
    D.node('u2', 20, 170, 118, 56, '브라우저', None, 'browser', k='손님')
    D.node('cf', 200, 170, 182, 56, 'CloudFront', 'HTTPS · 도메인 · 캐시', 'cloud', t='hl', k='동네 편의점', ksub='잠긴 트럭 · 가까움')
    D.node('b2', 424, 170, 156, 56, 'S3 버킷', '비공개 · OAC로만', t='ok', k='진열장 창고', ksub='편의점에만 열림')
    D.edge('u2', 'cf', 'HTTPS', k='잠금', t='acc')
    D.edge('cf', 'b2', t='acc')
    return D


@reg('c12-versioning-replication')
def _():
    D = Diagram('c12-versioning-replication', w=600, at='end:버전 관리(Versioning)',
                cap='같은 키에 다시 올리면 새 버전이 위에 쌓입니다. 버전 ID 없이 지우면 삭제 마커가 맨 위에 생겨 GET이 404를 돌려주고, 삭제 마커를 지우면 v3이 다시 보입니다. 버전 ID를 지정해 지우면 그 버전만 영구 삭제됩니다.',
                kcap='새 물건은 앞에, 옛 물건은 뒤에 쌓여요. "버려 주세요" 하면 "버림" 쪽지만 앞에 꽂히고, 쪽지를 빼면 물건이 다시 보여요.')
    cols = [
        ('1. 같은 키에 PUT 세 번', '1. 같은 번호표로 세 번', [('v3 (현재)', '3번째 물건 (앞)', 'acc'), ('v2', '2번째 물건', 'soft'), ('v1', '1번째 물건', 'soft'), ('null (켜기 전)', '켜기 전 물건', 'muted')],
         'GET → v3', '꺼내면 → 3번째 물건'),
        ('2. 버전 ID 없이 DELETE', '2. "버려 주세요"', [('삭제 마커 (현재)', '"버림" 쪽지 (앞)', 'warn'), ('v3', '3번째 물건', 'soft'), ('v2', '2번째 물건', 'soft'), ('v1', '1번째 물건', 'soft'), ('null', '켜기 전 물건', 'muted')],
         'GET → 404 Not Found', '꺼내면 → 없어요'),
        ('3. 삭제 마커를 삭제', '3. 쪽지 빼기', [('v3 (현재)', '3번째 물건 (앞)', 'acc'), ('v2', '2번째 물건', 'soft'), ('v1', '1번째 물건', 'soft'), ('null', '켜기 전 물건', 'muted')],
         'GET → v3 다시 보임', '꺼내면 → 3번째 물건'),
    ]
    for c, (h, kh, bars, foot, kfoot) in enumerate(cols):
        x = 8 + c * 202
        D.text(x, 20, h, k=kh, cls='lbl')
        for i, (s, ks, t) in enumerate(bars):
            D.bar(x, 34 + i * 36, 180, 30, s, k=ks, t=t)
        D.text(x, 236, foot, k=kfoot)
        if c < 2:
            D.arrow((x + 184, 100), (x + 198, 100), t='acc')
    return D


@reg('c12-versioning-replication:repl')
def _():
    D = Diagram('c12-versioning-replication:repl', w=600, at='end:복제(Replication)',
                cap='원본 버킷의 새 객체가 다른 리전(CRR)이나 같은 리전(SRR)의 버킷으로 비동기 복사됩니다. 양쪽 모두 버전 관리가 켜져 있어야 하고, 버킷 2 → 3 규칙이 있어도 1에서 2로 온 객체는 3으로 가지 않습니다.',
                kcap='1번 창고의 새 물건이 다른 도시나 같은 도시 창고로 하나 더 가요. 2번 창고가 3번으로 보내도, 1번에서 온 물건은 3번까지 이어서 가지 않아요.')
    D.group(8, 8, 300, 236, '서울 리전', k='서울 도시', solid=True)
    D.node('src', 24, 44, 130, 72, '버킷 1 (원본)', '버전 관리 켬', 'bucket', t='hl', k='1번 창고', ksub='옛 물건 쌓기 켬')
    D.node('srr', 170, 156, 126, 72, '로그 모음 버킷', 'SRR 대상', 'bucket', k='같은 도시 창고', ksub='모아 두기')
    D.group(330, 8, 262, 236, '도쿄 리전', k='도쿄 도시', solid=True)
    D.node('dst', 346, 44, 130, 72, '버킷 2 (대상)', '버전 관리 켬', 'bucket', t='ok', k='2번 창고', ksub='옛 물건 쌓기 켬')
    D.node('b3', 346, 156, 130, 72, '버킷 3', '1에서 온 것은 안 옴', 'bucket', t='warn', k='3번 창고', ksub='1번 물건은 안 와요')
    D.edge('src', 'dst', 'CRR (비동기)', k='다른 도시로 복사', t='acc')
    D.edge('src', 'srr', 'SRR', k='같은 도시로', t='acc', sa='b', sb='l')
    D.edge('dst', 'b3', '2 → 3 규칙', k='2번 → 3번', dash=True)
    D.text(8, 268, '복제는 켠 뒤의 새 객체만 · 기존 객체는 S3 Batch Replication · S3에 IAM 역할로 권한',
           k='켠 뒤에 들어온 물건만 보내요 · 그 전 물건은 한꺼번에 따로 보내요')
    return D


@reg('c12-classes')
def _():
    D = Diagram('c12-classes', w=600,
                cap='오른쪽 아래로 갈수록 저장료는 싸지고, 꺼내는 시간과 요금, 최소 보관 기간은 늘어납니다. Express One Zone은 Standard보다 빠르고 비쌉니다. Intelligent-Tiering은 접근 패턴에 따라 이 계단을 자동으로 오르내립니다.',
                kcap='오른쪽 아래 선반일수록 자리값은 싸고, 꺼내는 데 시간과 돈이 더 들어요. 로봇 선반은 알아서 안쪽으로 옮겨요.')
    steps = [
        ('Express One Zone', '한 자릿수 ms · 1 AZ', '초고속 선반', '한 동네 · 눈 깜짝', 'warn'),
        ('S3 Standard', '밀리초 · 자주 쓰는 데이터', '앞 선반', '바로 꺼냄 · 자주', 'hl'),
        ('Standard-IA', '밀리초 · 최소 30일', '안쪽 선반', '바로 꺼냄 · 30일 이상', 'plain'),
        ('One Zone-IA', '1 AZ · 최소 30일', '한 동네 안쪽 선반', '한 동네만 · 30일 이상', 'warn'),
        ('Glacier Instant', '밀리초 · 최소 90일', '지하 바로 칸', '바로 꺼냄 · 90일 이상', 'store'),
        ('Glacier Flexible', '분~시간 · 최소 90일', '지하 기다리는 칸', '몇 분~몇 시간', 'store'),
        ('Glacier Deep Archive', '12~48시간 · 최소 180일', '가장 깊은 칸', '하루~이틀 · 180일 이상', 'store'),
    ]
    for i, (l, s, kl, ks, t) in enumerate(steps):
        D.node(f's{i}', 8 + i * 66, 8 + i * 46, 180, 44, l, s, t=t, k=kl, ksub=ks)
    D.node('it', 8, 214, 220, 70, 'Intelligent-Tiering', '접근 패턴 따라 자동 이동\n꺼내는 요금 없음 · 모니터링 요금', t='ok',
           k='로봇이 옮기는 선반', ksub='알아서 안쪽으로 옮김\n꺼낼 때 돈 안 냄 · 로봇 수고비')
    D.text(8, 352, '오른쪽 아래로 갈수록: 저장료 ↓ · 꺼내는 시간·요금 ↑ · 최소 보관 기간 ↑',
           k='오른쪽 아래로 갈수록: 자리값 ↓ · 꺼내는 시간과 돈 ↑')
    return D
