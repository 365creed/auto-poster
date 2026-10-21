---
layout: default
title: ChooSu Note | 실전 IT & 인프라 엔지니어링
---

<head>
  <link rel="manifest" href="{{ site.baseurl }}/manifest.json">
  <meta name="theme-color" content="#0f172a">
</head>

<style>
  header.page-header, .page-header { display: none !important; }
  .main-content { max-width: 1000px !important; padding: 30px 20px !important; }
  body { background-color: #f8fafc !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
</style>

<div class="hero-banner">
  <div class="hero-badge">⚡ INFRASTRUCTURE & PWA TECH LAB</div>
  <h1 class="hero-title">ChooSu Note</h1>
  <p class="hero-desc">
    Synology NAS, Dell · HPE 서버, NT 및 네트워크 인프라까지.<br>
    현장에서 직접 겪고 해결하며 축적하는 <strong>실무 기술 노하우 & 엔지니어링 아카이브</strong>
  </p>
  <div class="legal-notice-badge">
    ⚖️ 본 블로그의 모든 포스팅은 법적 기준에 따라 <b>AI(인공지능) 기술을 활용해 자동 생성 및 검수</b>되어 발행됩니다.
  </div>
  
  <div class="tech-stack-pills" style="margin-top: 16px;">
    <span class="pill">🌐 Network</span>
    <span class="pill">🖥️ Dell & HPE Server</span>
    <span class="pill">💾 Synology NAS</span>
    <span class="pill">⚡ PWA Web App</span>
    <span class="pill">🛠️ IT Infrastructure</span>
  </div>
</div>

<div class="section-header">
  <h2>🔥 Latest Engineering Logs</h2>
  <span class="post-count">Total Archives: {{ site.posts.size }}</span>
</div>

<div class="post-grid">
  {% for post in site.posts %}
    <article class="post-card">
      <div class="card-top">
        <span class="post-date">📅 {{ post.date | date: "%Y-%m-%d" }}</span>
        {% if post.tags.size > 0 %}
          <div class="card-tags">
            {% for tag in post.tags limit:2 %}
              <span class="tag-badge">#{{ tag }}</span>
            {% endfor %}
          </div>
        {% endif %}
      </div>

      <h2 class="post-title">
        <a href="{{ site.baseurl }}{{ post.url }}">
          {{ post.title }}
        </a>
      </h2>

      <div class="card-footer">
        <span class="read-more">Read Guide &rarr;</span>
        <span class="tech-icon-hint">🤖 AI Assisted Tech Log</span>
      </div>
    </article>
  {% endfor %}
</div>

<style>
  .hero-banner { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border-radius: 20px; padding: 48px 36px; color: #ffffff; margin-bottom: 40px; box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.15); }
  .hero-badge { display: inline-block; background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.75rem; font-weight: 700; padding: 6px 12px; border-radius: 30px; margin-bottom: 16px; }
  .legal-notice-badge { background: rgba(255, 255, 255, 0.1); border-left: 3px solid #38bdf8; padding: 8px 12px; border-radius: 4px; font-size: 0.82rem; color: #e2e8f0; margin-top: 12px; }
  .hero-title { margin: 0 0 12px 0; font-size: 2.5rem; font-weight: 900; color: #ffffff !important; }
  .hero-desc { margin: 0 0 16px 0; font-size: 1.05rem; color: #cbd5e1; line-height: 1.6; }
  .hero-desc strong { color: #38bdf8; }
  .tech-stack-pills { display: flex; flex-wrap: wrap; gap: 8px; }
  .pill { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.12); color: #e2e8f0; padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; }
  .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }
  .section-header h2 { margin: 0; font-size: 1.4rem; font-weight: 800; color: #0f172a; }
  .post-count { font-size: 0.85rem; color: #64748b; font-weight: 600; background: #e2e8f0; padding: 4px 10px; border-radius: 20px; }
  .post-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
  .post-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02); transition: all 0.3s ease; }
  .post-card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08); border-color: #3b82f6; }
  .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
  .post-date { font-size: 0.8rem; color: #94a3b8; font-weight: 600; }
  .card-tags { display: flex; gap: 6px; }
  .tag-badge { background: #eff6ff; color: #2563eb; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
  .post-title { margin: 0 0 20px 0; font-size: 1.15rem; font-weight: 700; line-height: 1.5; }
  .post-title a { color: #1e293b; text-decoration: none; }
  .post-card:hover .post-title a { color: #2563eb; }
  .card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px; font-size: 0.85rem; }
  .read-more { color: #2563eb; font-weight: 700; }
  .tech-icon-hint { color: #64748b; font-weight: 600; font-size: 0.75rem; }
</style>
