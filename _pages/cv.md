---
layout: archive
title: "CV (This page is actively being edited)"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

<!-- Education
======
* Ph.D in Version Control Theory, GitHub University, 2018 (expected)
* M.S. in Jekyll, GitHub University, 2014
* B.S. in GitHub, GitHub University, 2012

Work experience
======
* Spring 2024: Academic Pages Collaborator
  * GitHub University
  * Duties includes: Updates and improvements to template
  * Supervisor: The Users

* Fall 2015: Research Assistant
  * GitHub University
  * Duties included: Merging pull requests
  * Supervisor: Professor Hub

* Summer 2015: Research Assistant
  * GitHub University
  * Duties included: Tagging issues
  * Supervisor: Professor Git
  
Skills
======
* Skill 1
* Skill 2
  * Sub-skill 2.1
  * Sub-skill 2.2
  * Sub-skill 2.3
* Skill 3

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Talks
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html  %}
  {% endfor %}</ul>
  
Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Service and leadership
======
* Currently signed in to 43 different slack teams -->



<!-- CV in PDF: always the latest cv.pdf on main of github.com/wei-hsuan-cheng/wei_hsuan_cheng_cv.
     The script asks the GitHub API for the last commit that changed cv.pdf and embeds that exact version from
     jsDelivr, so a new push shows up at once (a commit-pinned URL is never stale). If the API cannot be reached,
     it falls back to @main, which jsDelivr may cache for up to 12 hours. -->
<p>
  <a href="https://github.com/wei-hsuan-cheng/wei_hsuan_cheng_cv/blob/main/cv.pdf" target="_blank" rel="noopener"><i class="fas fa-file-pdf" aria-hidden="true"></i> Open the PDF on GitHub</a>
</p>

<div id="cv-pdf">
  <noscript><embed src="https://cdn.jsdelivr.net/gh/wei-hsuan-cheng/wei_hsuan_cheng_cv@main/cv.pdf" type="application/pdf" width="100%" height="800px" /></noscript>
</div>

<script>
(function () {
  var repo = "wei-hsuan-cheng/wei_hsuan_cheng_cv";
  var shown = false;
  function show(ref) {
    if (shown) return;
    shown = true;
    var pdf = document.createElement("embed");
    pdf.src = "https://cdn.jsdelivr.net/gh/" + repo + "@" + ref + "/cv.pdf";
    pdf.type = "application/pdf";
    pdf.width = "100%";
    pdf.height = "800px";
    document.getElementById("cv-pdf").appendChild(pdf);
  }
  setTimeout(function () { show("main"); }, 4000);
  fetch("https://api.github.com/repos/" + repo + "/commits?path=cv.pdf&sha=main&per_page=1")
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function (commits) { show(commits.length ? commits[0].sha : "main"); })
    .catch(function () { show("main"); });
})();
</script>