---
layout: default
title: 세상에서 가장 친절한 컴퓨터 기초 학교
---

<style>
  .school-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #1d4ed8 100%);
    border-radius: 26px;
    padding: 48px 44px;
    color: #ffffff;
    margin-bottom: 36px;
    box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.25);
    position: relative;
    overflow: hidden;
  }
  .hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(56, 189, 248, 0.2);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #7dd3fc;
    font-size: 0.84rem;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 30px;
    margin-bottom: 18px;
  }
  .school-hero h1 {
    font-size: 2.55rem;
    font-weight: 900;
    margin: 0 0 14px 0;
    line-height: 1.3;
    letter-spacing: -0.02em;
    color: #ffffff !important;
  }
  .school-hero p {
    font-size: 1.12rem;
    color: #e2e8f0;
    max-width: 780px;
    margin: 0 0 28px 0;
    line-height: 1.75;
  }
  .schedule-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .sched-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    padding: 18px 20px;
  }
  .sched-time {
    font-size: 0.82rem;
    font-weight: 800;
    color: #38bdf8;
    margin-bottom: 4px;
  }
  .sched-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
  }
  .sched-desc {
    font-size: 0.86rem;
    color: #cbd5e1;
    line-height: 1.5;
  }

  /* Curriculum Roadmap */
  .roadmap-section {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 22px;
    padding: 28px 32px;
    margin-bottom: 36px;
    box-shadow: var(--shadow-sm);
  }
  .roadmap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
  }
  .roadmap-header h2 {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 900;
  }
  .stage-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
  }
  .stage-box {
    background: var(--bg-subtle);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
  }
  .stage-num {
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--primary);
    margin-bottom: 4px;
  }
  .stage-name {
    font-size: 0.98rem;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 6px;
  }
  .stage-sub {
    font-size: 0.83rem;
    color: var(--text-secondary);
    line-height: 1.45;
  }

  /* Filter & Search Bar */
  .controls-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
  }
  .filter-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .filter-btn {
    cursor: pointer;
    border: 1px solid var(--border-color);
    background: var(--bg-surface);
    color: var(--text-secondary);
    padding: 9px 16px;
    border-radius: 30px;
    font-size: 0.88rem;
    font-weight: 800;
    transition: all 0.2s;
  }
  .filter-btn.active, .filter-btn:hover {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }
  .search-input-wrap {
    position: relative;
    min-width: 260px;
    flex: 1;
    max-width: 360px;
  }
  .search-input {
    width: 100%;
    padding: 10px 16px 10px 38px;
    border-radius: 30px;
    border: 1px solid var(--border-color);
    background: var(--bg-surface);
    color: var(--text-main);
    font-size: 0.92rem;
    outline: none;
  }
  .search-input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  }
  .search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.9rem;
  }

  /* Post Cards Grid */
  .post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 24px;
  }
  .post-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
    transition: all 0.28s ease;
  }
  .post-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary);
  }
  .card-thumb {
    width: 100%;
    height: 195px;
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
  }
  .card-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.35s ease;
  }
  .post-card:hover .card-thumb img {
    transform: scale(1.04);
  }
  .thumb-overlay-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(6px);
    color: #38bdf8;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 800;
  }
  .card-body {
    padding: 22px 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .card-meta-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 700;
  }
  .slot-indicator {
    padding: 3px 9px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 800;
  }
  .slot-indicator.morning { background: #fef3c7; color: #b45309; }
  .slot-indicator.afternoon { background: #dcfce7; color: #15803d; }
  .slot-indicator.manual { background: #f3e8ff; color: #6d28d9; }

  .card-title {
    margin: 0 0 10px 0;
    font-size: 1.2rem;
    font-weight: 800;
    line-height: 1.45;
  }
  .card-title a {
    color: var(--text-main);
  }
  .post-card:hover .card-title a {
    color: var(--primary);
  }
  .card-excerpt {
    font-size: 0.92rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 18px;
    flex: 1;
  }
  .card-footer {
    padding-top: 14px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag-chip {
    background: var(--primary-soft);
    color: var(--primary);
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 700;
  }
  .read-btn {
    font-size: 0.86rem;
    font-weight: 800;
    color: var(--primary);
    white-space: nowrap;
  }
</style>

<section class="school-hero">
  <div class="hero-kicker">🏫 누구나 이해하는 친절한 기초 컴퓨터 교실 &amp; 가상 OS 실습실</div>
  <h1>"자, 이게 클릭(Click)이야!"<br>처음부터 배우는 컴퓨터 &amp; 노트북의 모든 것</h1>
  <p>
    교실만 하던 최초의 컴퓨터 역사부터 내 무릎 위 노트북의 원리, 마우스 클릭과 창 닫기까지.<br>
    <strong>가상화 OS 환경에서 AI가 직접 마우스를 움직이고 미니게임을 플레이하며 찍은 스크린샷</strong>으로 아무것도 모르는 분도 단번에 이해할 수 있게 설명해 드립니다.
  </p>

  <div class="schedule-grid">
    <div class="sched-card">
      <div class="sched-time">☀️ 매일 오전 09:00 (자동 연산 1회차)</div>
      <div class="sched-title">1~3교시 · 역사와 근원적 기초 원리</div>
      <div class="sched-desc">컴퓨터·노트북의 역사, 0과 1의 비밀, 마우스 클릭과 운영체제 개념을 학교 수업처럼 친절하게 배워요.</div>
    </div>
    <div class="sched-card">
      <div class="sched-time">🎮 매일 오후 15:00 (자동 연산 2회차)</div>
      <div class="sched-title">4교시 · AI 가상 OS 조작 &amp; 게임 실습</div>
      <div class="sched-desc">가상 OS에서 AI가 직접 지뢰찾기·타자게임·파일 탐색기를 실행하고 단계별 스크린샷을 찍어 올려요.</div>
    </div>
    <div class="sched-card">
      <div class="sched-time">🌙 매일 저녁 시간 (인간 수동 발행)</div>
      <div class="sched-title">방과후 노트 · 사람이 직접 쓰는 이야기</div>
      <div class="sched-desc">저녁에는 자동 연산 대신 사람이 직접 경험담, 질의응답, 심화 팁을 다정하게 정리해 올립니다.</div>
    </div>
  </div>
</section>

<section class="roadmap-section" id="curriculum-roadmap">
  <div class="roadmap-header">
    <h2>🗺️ 학교처럼 차근차근 배우는 5단계 기초 커리큘럼</h2>
    <span style="font-size:0.86rem; color:var(--text-muted); font-weight:700;">총 {{ site.posts.size }}개의 수업 노트가 준비되어 있어요</span>
  </div>
  <div class="stage-steps">
    <div class="stage-box">
      <div class="stage-num">STEP 01 · 역사와 근원</div>
      <div class="stage-name">컴퓨터·노트북의 탄생</div>
      <div class="stage-sub">진공관 에니악(ENIAC)부터 노트북까지, 전등 스위치(0과 1)로 생각하는 기계의 원리</div>
    </div>
    <div class="stage-box">
      <div class="stage-num">STEP 02 · 손끝 조작 기초</div>
      <div class="stage-name">"자, 이게 클릭이야!"</div>
      <div class="stage-sub">마우스 커서 이동, 좌클릭·우클릭·더블클릭, 키보드 자판과 필수 단축키</div>
    </div>
    <div class="stage-box">
      <div class="stage-num">STEP 03 · 운영체제 탐험</div>
      <div class="stage-name">바탕화면과 창(Window)</div>
      <div class="stage-sub">컴퓨터 속 집사 OS의 역할, 창 열고 닫기, 서류봉투(폴더)에 파일 정리하기</div>
    </div>
    <div class="stage-box">
      <div class="stage-num">STEP 04 · 가상 OS &amp; 게임</div>
      <div class="stage-name">AI와 함께 게임으로 실습</div>
      <div class="stage-sub">지뢰찾기·타자연습·메모장을 가상 OS에서 AI가 직접 플레이하고 캡처한 실전 수업</div>
    </div>
    <div class="stage-box">
      <div class="stage-num">STEP 05 · 컴퓨터 속 도시</div>
      <div class="stage-name">CPU · RAM · SSD 주방 비유</div>
      <div class="stage-sub">요리사(CPU), 조리대(RAM), 냉장고(SSD) 비유로 내 노트북 사양 완벽 이해하기</div>
    </div>
  </div>
</section>

<div class="controls-bar">
  <div class="filter-tabs">
    <button class="filter-btn active" onclick="filterPosts('all', this)">전체 수업 ({{ site.posts.size }})</button>
    <button class="filter-btn" onclick="filterPosts('morning_auto', this)">☀️ 오전 9시 기초·원리</button>
    <button class="filter-btn" onclick="filterPosts('afternoon_auto', this)">🎮 오후 3시 가상 OS·게임</button>
    <button class="filter-btn" onclick="filterPosts('evening_manual', this)">🌙 저녁 수동 노트</button>
  </div>
  <div class="search-input-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="postSearchInput" class="search-input" placeholder="궁금한 기초 단어 검색 (예: 클릭, 지뢰찾기, 노트북)..." oninput="searchPosts()">
  </div>
</div>

<div class="post-grid" id="postGridContainer">
  {% for post in site.posts %}
    {% assign slot_type = post.slot_id | default: "morning_auto" %}
    <article class="post-card" data-slot="{{ slot_type }}" data-search="{{ post.title | downcase }} {{ post.subtitle | downcase }} {{ post.tags | join: ' ' | downcase }}">
      <a href="{{ site.baseurl }}{{ post.url }}" class="card-thumb">
        {% if post.thumbnail and post.thumbnail != "" %}
          <img src="{{ post.thumbnail }}" alt="{{ post.title }}" loading="lazy">
        {% else %}
          <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#38bdf8; font-size:3rem;">🖥️</div>
        {% endif %}
        <span class="thumb-overlay-badge">{{ post.stage | default: "기초 컴퓨터 교실" }}</span>
      </a>

      <div class="card-body">
        <div class="card-meta-top">
          <span>📅 {{ post.date | date: "%Y-%m-%d" }}</span>
          {% if slot_type == "evening_manual" %}
            <span class="slot-indicator manual">🌙 저녁 수동 노트</span>
          {% elsif slot_type == "afternoon_auto" %}
            <span class="slot-indicator afternoon">🎮 오후 3시 OS·게임 실습</span>
          {% else %}
            <span class="slot-indicator morning">☀️ 오전 9시 기초 수업</span>
          {% endif %}
        </div>

        <h2 class="card-title">
          <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
        </h2>

        <p class="card-excerpt">
          {{ post.subtitle | default: post.excerpt | strip_html | truncate: 110 }}
        </p>

        <div class="card-footer">
          <div class="card-tags">
            {% for tag in post.tags limit:3 %}
              <span class="tag-chip">#{{ tag }}</span>
            {% endfor %}
          </div>
          <a href="{{ site.baseurl }}{{ post.url }}" class="read-btn">수업 듣기 &rarr;</a>
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

  function searchPosts() {
    applyPostFilters();
  }

  function applyPostFilters() {
    const q = (document.getElementById('postSearchInput').value || '').toLowerCase().trim();
    const cards = document.querySelectorAll('#postGridContainer .post-card');
    cards.forEach(card => {
      const cardSlot = card.getAttribute('data-slot') || 'morning_auto';
      const searchBlob = card.getAttribute('data-search') || '';
      const slotMatch = (currentSlotFilter === 'all') || (cardSlot === currentSlotFilter);
      const textMatch = !q || searchBlob.includes(q);
      card.style.display = (slotMatch && textMatch) ? 'flex' : 'none';
    });
  }
</script>
