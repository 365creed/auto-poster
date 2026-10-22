---
layout: default
title: 세상에서 가장 친절한 컴퓨터 기초 학교 (Argon Edition)
---

<style>
  .argon-hero {
    background: linear-gradient(87deg, #5e72e4 0, #825ee4 100%);
    border-radius: 24px;
    padding: 48px 44px;
    color: #ffffff;
    margin-bottom: 34px;
    box-shadow: var(--argon-shadow);
    position: relative;
    overflow: hidden;
  }
  .argon-kicker-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
  }
  .argon-kicker {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.18);
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 30px;
  }
  .argon-kicker.mint { background: #2dce89; color: #fff; }
  .argon-hero h1 {
    font-size: 2.45rem;
    font-weight: 900;
    margin: 0 0 14px 0;
    line-height: 1.32;
    color: #ffffff !important;
  }
  .argon-hero p {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.92);
    max-width: 820px;
    margin: 0 0 26px 0;
    line-height: 1.75;
  }
  .ops-pipeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
  }
  .ops-card {
    background: rgba(23, 43, 77, 0.35);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 16px;
    padding: 16px 18px;
  }
  .ops-tag { font-size: 0.76rem; font-weight: 800; color: #11cdef; margin-bottom: 4px; }
  .ops-title { font-size: 1rem; font-weight: 800; color: #ffffff; margin-bottom: 6px; }
  .ops-desc { font-size: 0.83rem; color: rgba(255, 255, 255, 0.85); line-height: 1.5; }

  /* Quick Glossary & Search Section */
  .glossary-bar {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 20px 24px;
    margin-bottom: 28px;
    box-shadow: var(--argon-shadow-sm);
  }
  .glossary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 12px;
    margin-top: 12px;
  }
  .g-item {
    background: var(--bg-subtle);
    border-left: 4px solid var(--argon-primary);
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.85rem;
  }
  .g-item strong { color: var(--argon-primary); display: block; margin-bottom: 2px; }

  .controls-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
  }
  .filter-tabs { display: flex; flex-wrap: wrap; gap: 8px; }
  .filter-btn {
    cursor: pointer;
    border: 1px solid var(--border-color);
    background: var(--bg-surface);
    color: var(--text-secondary);
    padding: 9px 16px;
    border-radius: 30px;
    font-size: 0.86rem;
    font-weight: 800;
    transition: all 0.2s;
  }
  .filter-btn.active, .filter-btn:hover {
    background: var(--argon-primary);
    color: #ffffff;
    border-color: var(--argon-primary);
    box-shadow: var(--argon-shadow-sm);
  }
  .search-input-wrap { position: relative; min-width: 260px; flex: 1; max-width: 360px; }
  .search-input {
    width: 100%;
    padding: 10px 16px 10px 38px;
    border-radius: 30px;
    border: 1px solid var(--border-color);
    background: var(--bg-surface);
    color: var(--text-main);
    font-size: 0.9rem;
    outline: none;
  }
  .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); }

  .quick-chips-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 26px;
    font-size: 0.83rem;
  }
  .q-chip {
    cursor: pointer;
    background: var(--argon-primary-soft);
    color: var(--argon-primary);
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 800;
    border: 1px solid rgba(94, 114, 228, 0.25);
  }
  .q-chip:hover { background: var(--argon-primary); color: #fff; }

  .post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 24px;
  }
  .post-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--argon-shadow-sm);
    transition: all 0.25s ease;
  }
  .post-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--argon-shadow);
    border-color: var(--argon-primary);
  }
  .card-thumb {
    width: 100%;
    height: 195px;
    background: #172b4d;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
  }
  .card-thumb img { width: 100%; height: 100%; object-fit: cover; }
  .thumb-overlay-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(23, 43, 77, 0.88);
    color: #11cdef;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 800;
  }
  .thumb-verify-badge {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: #2dce89;
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 900;
  }
  .card-body { padding: 22px 24px; flex: 1; display: flex; flex-direction: column; }
  .card-meta-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 700;
  }
  .card-title { margin: 0 0 10px 0; font-size: 1.18rem; font-weight: 800; line-height: 1.45; }
  .card-title a { color: var(--text-main); }
  .post-card:hover .card-title a { color: var(--argon-primary); }
  .card-excerpt { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 18px; flex: 1; }
  .card-footer {
    padding-top: 14px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .tag-chip {
    background: var(--argon-primary-soft);
    color: var(--argon-primary);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.73rem;
    font-weight: 700;
    margin-right: 4px;
  }
</style>

<section class="argon-hero">
  <div class="argon-kicker-row">
    <span class="argon-kicker">🎨 Argon Design System ({{ site.data.argon_state.current_version | default: "Argon v2.1" }})</span>
    <span class="argon-kicker">🤖 생산: Gemini 가상 OS 테스트</span>
    <span class="argon-kicker mint">🛡️ 검증: GPT Think 추론 승인</span>
  </div>
  <h1>PC 이름 바꾸기부터 클릭·게임까지,<br>가상 OS에서 직접 테스트하고 알려주는 왕초보 컴퓨터 학교</h1>
  <p>
    아무것도 모르는 컴맹이 가장 먼저 막히는 <strong>"내 컴퓨터 이름 바꾸는 법", "마우스 클릭·우클릭", "아이콘 크기 키우기"</strong>까지.<br>
    제미나이(Gemini)가 가상 환경에서 직접 버튼을 눌러 캡처하고, <strong>GPT Think가 정확성을 검증한 뒤 Git으로 자동 배포</strong>합니다.
  </p>

  <div class="ops-pipeline-grid">
    <div class="ops-card">
      <div class="ops-tag">🎨 하루 1회 자동 진화 (03:00 KST)</div>
      <div class="ops-title">Argon 블로그 외관 업그레이드</div>
      <div class="ops-desc">Argon 테마 규격 안에서 글자 돋보기, 용어 사전, 체크박스 등 초보자 UI를 매일 1회 발전시킵니다.</div>
    </div>
    <div class="ops-card">
      <div class="ops-tag">🖥️ 하루 2회 실습 생산 (09시 · 15시)</div>
      <div class="ops-title">제미나이 가상 OS 테스트 포스팅</div>
      <div class="ops-desc">가상 OS에서 PC 이름 변경·클릭·지뢰찾기를 직접 실행해 3단계 스크린샷과 글을 생산합니다.</div>
    </div>
    <div class="ops-card">
      <div class="ops-tag">🛡️ 전 과정 품질 게이트</div>
      <div class="ops-title">GPT Think 다단계 추론 검증</div>
      <div class="ops-desc">컴맹 눈높이 친절도, 스크린샷-본문 일치성, Argon 레이아웃 무결성을 검증한 뒤 승인합니다.</div>
    </div>
    <div class="ops-card">
      <div class="ops-tag">🌙 저녁 수동 + Git 무중단 운영</div>
      <div class="ops-title">Git 자동 배포 &amp; 관제 센터</div>
      <div class="ops-desc"><a href="{{ '/status.html' | relative_url }}" style="color:#11cdef; text-decoration:underline; font-weight:800;">작동 구조 &amp; 자가 점검 센터</a>에서 언제든 작동 상태를 확인합니다.</div>
    </div>
  </div>
</section>

<section class="glossary-bar">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <strong style="font-size:1rem;">📖 컴맹 탈출 1초 용어 사전 (자주 나오는 단어를 쉽게 풀었어요!)</strong>
    <span style="font-size:0.8rem; color:var(--text-muted);">Argon Daily Evolution 적용 위젯</span>
  </div>
  <div class="glossary-grid">
    <div class="g-item"><strong>PC 이름 (호스트네임)</strong>공장 임시 번호(`DESKTOP-XXX`) 대신 내가 붙이는 컴퓨터 이름표예요.</div>
    <div class="g-item"><strong>클릭 vs 더블클릭</strong>한 번 '딸깍'은 선택하기, 두 번 연속 '따닥!'은 문 열고 실행하기예요.</div>
    <div class="g-item"><strong>우클릭 (오른쪽 버튼)</strong>"여기서 할 수 있는 일 목록(메뉴판) 좀 보여줘!" 하고 부르는 버튼이에요.</div>
    <div class="g-item"><strong>운영체제 (OS · 윈도우)</strong>컴퓨터 부품들과 사람 사이에서 통역을 해주는 친절한 집사 프로그램이에요.</div>
  </div>
</section>

<div class="controls-bar">
  <div class="filter-tabs">
    <button class="filter-btn active" onclick="filterPosts('all', this)">전체 수업 ({{ site.posts.size }})</button>
    <button class="filter-btn" onclick="filterPosts('morning_auto', this)">☀️ 오전 9시 실전 설정·원리</button>
    <button class="filter-btn" onclick="filterPosts('afternoon_auto', this)">🎮 오후 3시 가상 OS·게임</button>
    <button class="filter-btn" onclick="filterPosts('evening_manual', this)">🌙 저녁 수동 노트</button>
  </div>
  <div class="search-input-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="postSearchInput" class="search-input" placeholder="궁금한 설정 검색 (예: PC 이름, 클릭, 지뢰찾기)..." oninput="searchPosts()">
  </div>
</div>

<div class="quick-chips-row">
  <span style="font-weight:800; color:var(--text-muted);">💡 컴맹 인기 검색어 원클릭:</span>
  <span class="q-chip" onclick="quickSearch('이름')">🖥️ PC 이름 바꾸기</span>
  <span class="q-chip" onclick="quickSearch('클릭')">🖱️ 클릭·더블클릭 원리</span>
  <span class="q-chip" onclick="quickSearch('지뢰찾기')">💣 지뢰찾기 우클릭 연습</span>
  <span class="q-chip" onclick="quickSearch('노트북')">💻 처음 산 노트북 정리</span>
  <span class="q-chip" onclick="quickSearch('')">🔄 전체 초기화</span>
</div>

<div class="post-grid" id="postGridContainer">
  {% for post in site.posts %}
    {% assign slot_type = post.slot_id | default: "morning_auto" %}
    <article class="post-card" data-slot="{{ slot_type }}" data-search="{{ post.title | downcase }} {{ post.subtitle | downcase }} {{ post.tags | join: ' ' | downcase }}">
      <a href="{{ post.url | relative_url }}" class="card-thumb">
        {% if post.thumbnail and post.thumbnail != "" %}
          <img src="{{ post.thumbnail }}" alt="{{ post.title }}" loading="lazy">
        {% endif %}
        <span class="thumb-overlay-badge">{{ post.stage | default: "기초 컴퓨터 교실" }}</span>
        <span class="thumb-verify-badge">🛡️ GPT Think Verified</span>
      </a>

      <div class="card-body">
        <div class="card-meta-top">
          <span>📅 {{ post.date | date: "%Y-%m-%d" }}</span>
          <span style="color:var(--argon-primary);">{{ post.os_type | default: "가상 OS 테스트" }}</span>
        </div>

        <h2 class="card-title">
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </h2>

        <p class="card-excerpt">
          {{ post.subtitle | default: post.excerpt | strip_html | truncate: 110 }}
        </p>

        <div class="card-footer">
          <div>
            {% for tag in post.tags limit:3 %}
              <span class="tag-chip">#{{ tag }}</span>
            {% endfor %}
          </div>
          <a href="{{ post.url | relative_url }}" style="font-weight:800; font-size:0.86rem;">따라 하기 &rarr;</a>
        </div>
      </div>
    </article>
  {% endfor %}
</div>

<script>
  let currentSlotFilter = 'all';
  function filterPosts(slot, btnEl) {
    currentSlotFilter = slot;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');
    applyPostFilters();
  }
  function quickSearch(keyword) {
    const inp = document.getElementById('postSearchInput');
    inp.value = keyword;
    applyPostFilters();
  }
  function searchPosts() { applyPostFilters(); }
  function applyPostFilters() {
    const q = (document.getElementById('postSearchInput').value || '').toLowerCase().trim();
    document.querySelectorAll('#postGridContainer .post-card').forEach(card => {
      const cardSlot = card.getAttribute('data-slot') || 'morning_auto';
      const searchBlob = card.getAttribute('data-search') || '';
      const slotMatch = (currentSlotFilter === 'all') || (cardSlot === currentSlotFilter);
      const textMatch = !q || searchBlob.includes(q);
      card.style.display = (slotMatch && textMatch) ? 'flex' : 'none';
    });
  }
</script>
