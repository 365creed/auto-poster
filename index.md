---
layout: default
title: ChooSu Note | 실전 IT & 홈랩 가이드
---

<div style="padding: 20px 0 30px 0; border-bottom: 1px solid #eaecef; margin-bottom: 30px;">
  <h1 style="margin: 0 0 10px 0; font-size: 2.2rem; font-weight: 800; color: #1e293b;">📚 ChooSu Note</h1>
  <p style="margin: 0; font-size: 1.1rem; color: #64748b; line-height: 1.5;">
    격으면서 이리저리 정리하는 <br><strong>Synology NAS, Dell, HPE, PC, NT, Network 등.. 인프라, IT 실무 기술 노트</strong>입니다.
  </p>
</div>

<h3 style="margin-bottom: 20px; font-size: 1.3rem; font-weight: 700; color: #334155;">🔥 최신 기술 가이드</h3>

<div class="post-list" style="display: flex; flex-direction: column; gap: 16px;">
  {% for post in site.posts %}
    <div class="post-card" style="padding: 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); transition: transform 0.2s, box-shadow 0.2s;">
      
      <!-- 날짜 및 태그 -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 500;">📅 {{ post.date | date: "%Y-%m-%d" }}</span>
        {% if post.tags.size > 0 %}
          <div style="display: flex; gap: 6px;">
            {% for tag in post.tags limit:3 %}
              <span style="background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">#{{ tag }}</span>
            {% endfor %}
          </div>
        {% endif %}
      </div>

      <!-- 포스트 제목 -->
      <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">
        <a href="{{ site.baseurl }}{{ post.url }}" style="color: #0f172a; text-decoration: none; transition: color 0.2s;">
          {{ post.title }}
        </a>
      </h2>
      
    </div>
  {% endfor %}
</div>

<style>
  .post-card:hover {
    transform: translateY(-2px;);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    border-color: #cbd5e1;
  }
  .post-card a:hover {
    color: #0284c7 !important;
  }
</style>
