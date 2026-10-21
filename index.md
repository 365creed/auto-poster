---
layout: default
title: ChooSu Note | 실전 IT & 홈랩 가이드
---

# 📚 ChooSu Note 최신 기술 가이드

내가 찾는 건 늘 없어서 직접 처음부터 끝까지 통합 정리하는 **시놀로지 NAS, 서버 인프라, IT 실무 노트**입니다.

---

### 📝 전체 포스팅 목록
<ul>
  {% for post in site.posts %}
    <li style="margin-bottom: 12px; font-size: 17px;">
      <span style="color: #64748b; font-size: 14px;">[{{ post.date | date: "%Y-%m-%d" }}]</span>
      <a href="{{ site.baseurl }}{{ post.url }}" style="font-weight: bold; text-decoration: none;">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
