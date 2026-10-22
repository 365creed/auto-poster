---
layout: default
title: 컴퓨팅 아카이브 & 디지털 리터러시 연구실
---

<style>
  .lab-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 58%, #312e81 100%);
    border-radius: 22px;
    padding: 46px 42px;
    color: #ffffff;
    margin-bottom: 32px;
    box-shadow: var(--card-shadow);
  }
  .lab-kicker {
    display: inline-block;
    background: rgba(56, 189, 248, 0.18);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #7dd3fc;
    font-size: 0.76rem;
    font-weight: 800;
    padding: 5px 13px;
    border-radius: 30px;
    margin-bottom: 16px;
    letter-spacing: 0.04em;
  }
  .lab-hero h1 {
    font-size: 2.3rem;
    font-weight: 900;
    margin: 0 0 12px 0;
    line-height: 1.34;
    color: #ffffff !important;
    letter-spacing: -0.02em;
  }
  .lab-hero p {
    font-size: 1.05rem;
    color: #cbd5e1;
    max-width: 780px;
    margin: 0;
    line-height: 1.75;
  }

  .concept-section {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 28px;
    box-shadow: var(--card-shadow-sm);
  }
  .concept-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-top: 14px;
  }
  .c-card {
    background: var(--bg-subtle);
    border-left: 3px solid var(--primary);
    padding: 12px 14px;
    border-radius: 10px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.55;
  }
  .c-card strong { color: var(--text-main); display: block; margin-bottom: 3px; font-size: 0.9rem; }

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
    padding: 8px 15px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 700;
    transition: all 0.2s;
  }
  .filter-btn.active, .filter-btn:hover {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }
  .search-input-wrap { position: relative; min-width: 260px; flex: 1; max-width: 340px; }
  .search-input {
    width: 100%;
    padding: 9px 16px 9px 36px;
    border-radius: 30px;
    border: 1px solid var(--border-color);
    background: var(--bg-surface);
    color: var(--text-main);
    font-size: 0.88rem;
    outline: none;
  }
  .search-icon { position: absolute; left: 13px; top: 50%; transform: translateY(-50%); font-size: 0.85rem; }

  .quick-chips-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 24px;
    font-size: 0.82rem;
  }
  .q-chip {
    cursor: pointer;
    background: var(--bg-surface);
    color: var(--text-secondary);
    padding: 4px 11px;
    border-radius: 20px;
    font-weight: 700;
    border: 1px solid var(--border-color);
  }
  .q-chip:hover { border-color: var(--primary); color: var(--primary); }

  .post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 24px;
  }
  .post-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--card-shadow-sm);
    transition: all 0.25s ease;
  }
  .post-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--card-shadow);
    border-color: var(--primary);
  }
  .card-thumb {
    width: 100%;
    height: 190px;
    background: #0f172a;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
  }
  .card-thumb img { width: 100%; height: 100%; object-fit: cover; }
  .thumb-cat-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(15, 23, 42, 0.85);
    color: #e2e8f0;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 700;
  }
  .card-body { padding: 22px 24px; flex: 1; display: flex; flex-direction: column; }
  .card-meta-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 600;
  }
  .card-title { margin: 0 0 10px 0; font-size: 1.15rem; font-weight: 800; line-height: 1.45; }
  .card-title a { color: var(--text-main); }
  .post-card:hover .card-title a { color: var(--primary); }
  .card-excerpt { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 18px; flex: 1; }
  .card-footer {
    padding-top: 14px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .tag-chip {
    background: var(--primary-soft);
    color: var(--primary);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.73rem;
    font-weight: 700;
    margin-right: 4px;
  }
</style>

<section class="lab-hero">
  <div class="lab-kicker">COMPUTING ARCHIVE &amp; DIGITAL LITERACY LAB</div>
  <h1>컴퓨터의 근원적 원리부터<br>운영체제 환경 설정까지 기록하는 리서치 랩</h1>
  <p>
    하드웨어의 발전사, 그래픽 인터페이스(GUI)의 입력 메커니즘, 그리고 가상 OS 환경에서 단계별로 테스트한 시스템 설정 가이드를 누구나 이해하기 쉬운 언어로 아카이빙합니다.
  </p>
</section>

<section class="concept-section" id="concept-notes">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <strong style="font-size:0.98rem;">핵심 개념 노트 (Core Concepts)</strong>
    <span style="font-size:0.8rem; color:var(--text-muted);">자주 등장하는 시스템 용어의 기본 정의</span>
  </div>
  <div class="concept-grid">
    <div class="c-card"><strong>호스트네임 (Hostname · 장치 이름)</strong>네트워크 및 블루투스 연결 시 기기를 식별하기 위해 부여되는 시스템 이름입니다.</div>
    <div class="c-card"><strong>마우스 입력 이벤트 (Click &amp; Hover)</strong>단일 선택(좌클릭), 연결 프로그램 실행(더블클릭), 옵션 호출(우클릭)로 구분되는 GUI 제어 신호입니다.</div>
    <div class="c-card"><strong>컨텍스트 메뉴 (Context Menu)</strong>특정 아이콘이나 화면 영역을 우클릭했을 때 그 위치에서 실행 가능한 기능만 모아 보여주는 메뉴입니다.</div>
    <div class="c-card"><strong>운영체제 (Operating System)</strong>CPU·메모리 등 하드웨어 자원을 관리하고 사용자가 그래픽 창(Window)으로 제어할 수 있게 중개하는 시스템입니다.</div>
  </div>
</section>

<div class="controls-bar">
  <div class="filter-tabs">
    <button class="filter-btn active" onclick="filterPosts('all', this)">전체 아카이브 ({{ site.posts.size }})</button>
    <button class="filter-btn" onclick="filterPosts('OS 환경 설정', this)">OS 환경 설정</button>
    <button class="filter-btn" onclick="filterPosts('인터페이스 원리', this)">인터페이스 원리</button>
    <button class="filter-btn" onclick="filterPosts('소프트웨어 아카이브', this)">소프트웨어 아카이브</button>
    <button class="filter-btn" onclick="filterPosts('컴퓨팅 아키텍처', this)">컴퓨팅 아키텍처</button>
  </div>
  <div class="search-input-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="postSearchInput" class="search-input" placeholder="아카이브 키워드 검색..." oninput="searchPosts()">
  </div>
</div>

<div class="quick-chips-row">
  <span style="font-weight:700; color:var(--text-muted);">주요 키워드:</span>
  <span class="q-chip" onclick="quickSearch('이름')">시스템 이름 변경</span>
  <span class="q-chip" onclick="quickSearch('클릭')">마우스 입력 구조</span>
  <span class="q-chip" onclick="quickSearch('지뢰찾기')">지뢰찾기와 GUI 설계</span>
  <span class="q-chip" onclick="quickSearch('바탕화면')">바탕화면 아이콘 배율</span>
  <span class="q-chip" onclick="quickSearch('')">전체 보기</span>
</div>

<div class="post-grid" id="postGridContainer">
  {% for post in site.posts %}
    {% assign cat_name = post.category | default: post.stage | default: "OS 환경 설정" %}
    <article class="post-card" data-cat="{{ cat_name }}" data-search="{{ post.title | downcase }} {{ post.subtitle | downcase }} {{ post.tags | join: ' ' | downcase }}">
      <a href="{{ site.baseurl }}{{ post.url }}" class="card-thumb">
        {% if post.thumbnail and post.thumbnail != "" %}
          <img src="{{ post.thumbnail }}" alt="{{ post.title }}" loading="lazy">
        {% endif %}
        <span class="thumb-cat-badge">{{ cat_name }}</span>
      </a>

      <div class="card-body">
        <div class="card-meta-top">
          <span>{{ post.date | date: "%Y.%m.%d" }}</span>
          <span>{{ post.os_type | default: "OS 환경 테스트" }}</span>
        </div>

        <h2 class="card-title">
          <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
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
          <a href="{{ site.baseurl }}{{ post.url }}" style="font-weight:800; font-size:0.85rem;">자세히 보기 &rarr;</a>
        </div>
      </div>
    </article>
  {% endfor %}
</div>

<script>
  let currentCatFilter = 'all';
  function filterPosts(cat, btnEl) {
    currentCatFilter = cat;
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
      const cardCat = card.getAttribute('data-cat') || '';
      const searchBlob = card.getAttribute('data-search') || '';
      const catMatch = (currentCatFilter === 'all') || cardCat.includes(currentCatFilter);
      const textMatch = !q || searchBlob.includes(q);
      card.style.display = (catMatch && textMatch) ? 'flex' : 'none';
    });
  }
</script>
