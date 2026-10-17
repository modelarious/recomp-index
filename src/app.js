(() => {
  const $ = (id) => document.getElementById(id);
  const els = {
    query: $("query"), clear: $("clearButton"), results: $("results"), resultCount: $("resultCount"),
    refreshStamp: $("refreshStamp"), platform: $("platformFilter"), type: $("typeFilter"),
    status: $("statusFilter"), activity: $("activityFilter"), sort: $("sortFilter"),
    conflict: $("conflictFilter"), loadMore: $("loadMore"), gameCount: $("gameCount"),
    projectCount: $("projectCount"), sourceCount: $("sourceCount"), recentCount: $("recentCount"),
    gameTemplate: $("gameTemplate"), sourcesButton: $("sourcesButton"), sourcesPanel: $("sourcesPanel"),
    closeSources: $("closeSources"), sourceList: $("sourceList")
  };
  const state = { catalog: null, filtered: [], shown: 80 };

  const statusLabel = (value) => ({
    "in-progress": "In progress", "unknown": "Status unknown", "complete": "Complete",
    "released": "Released", "playable": "Playable", "exploring": "Exploring", "paused": "Paused"
  }[value] || value || "Status unknown");

  const typeLabel = (value) => ({
    recomp: "Static recomp", decomp: "Decomp", port: "Source port", other: "Other"
  }[value] || value);

  const fmt = (value) => Number(value || 0).toLocaleString();
  const parseDate = (value) => value ? new Date(value + (value.length === 10 ? "T00:00:00Z" : "")) : null;
  const daysAgo = (value) => {
    const d = parseDate(value); if (!d || Number.isNaN(+d)) return null;
    return Math.floor((Date.now() - d.getTime()) / 86400000);
  };
  const activityText = (value) => {
    const days = daysAgo(value);
    if (days === null) return "No activity date";
    if (days <= 0) return "Active today";
    if (days === 1) return "Active yesterday";
    if (days < 30) return `Active ${days}d ago`;
    if (days < 365) return `Active ${Math.floor(days / 30)}mo ago`;
    return `Active ${Math.floor(days / 365)}y ago`;
  };
  const safe = (value) => value == null ? "" : String(value);

  function fillSelect(select, rows, labeler = (x) => x) {
    const current = select.value;
    for (const [value, count] of rows) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = `${labeler(value)} · ${fmt(count)}`;
      select.append(option);
    }
    select.value = current;
  }

  function projectSearchText(p) {
    return [p.project, p.repo, p.toolchain, p.type, p.status, ...(p.targets || []),
      ...(p.embedded_sources || []), ...((p.evidence || []).map(e => e.source))]
      .filter(Boolean).join(" ").toLowerCase();
  }

  function matchesQuery(game, query) {
    if (!query) return true;
    const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
    const haystack = [game.title, game.platform, ...game.projects.map(projectSearchText)].join(" ").toLowerCase();
    return tokens.every(t => haystack.includes(t));
  }

  function applyFilters() {
    if (!state.catalog) return;
    const q = els.query.value.trim();
    const activityDays = Number(els.activity.value || 0);
    let rows = state.catalog.games.filter(game => {
      if (!matchesQuery(game, q)) return false;
      if (els.platform.value && game.platform !== els.platform.value) return false;
      if (els.type.value && !game.types.includes(els.type.value)) return false;
      if (els.status.value && !game.statuses.includes(els.status.value)) return false;
      if (activityDays) {
        const age = daysAgo(game.last_activity);
        if (age === null || age > activityDays) return false;
      }
      if (els.conflict.checked && !game.has_conflict) return false;
      return true;
    });
    if (els.sort.value === "name") rows.sort((a,b) => a.title.localeCompare(b.title));
    else if (els.sort.value === "projects") rows.sort((a,b) => b.project_count - a.project_count || a.title.localeCompare(b.title));
    else rows.sort((a,b) => safe(b.last_activity).localeCompare(safe(a.last_activity)) || a.title.localeCompare(b.title));
    state.filtered = rows;
    state.shown = 80;
    render();
    syncUrl();
  }

  function makeProjectRow(project) {
    const row = document.createElement("div");
    row.className = "project-row";
    const top = document.createElement("div");
    top.className = "project-top";

    const left = document.createElement("div");
    const link = document.createElement(project.project_url ? "a" : "span");
    link.className = "project-title";
    link.textContent = project.project || project.repo || "Unnamed project";
    if (project.project_url) {
      link.href = project.project_url;
      link.target = "_blank";
      link.rel = "noopener";
    }
    left.append(link);

    const badges = document.createElement("div");
    badges.className = "project-badges";
    const type = document.createElement("span");
    type.className = `mini-badge type-${project.type || "other"}`;
    type.textContent = typeLabel(project.type);
    badges.append(type);
    if (project.status && project.status !== "unknown") {
      const status = document.createElement("span");
      status.className = "mini-badge";
      status.textContent = statusLabel(project.status);
      badges.append(status);
    }
    if (project.toolchain) {
      const tool = document.createElement("span");
      tool.className = "mini-badge";
      tool.textContent = project.toolchain;
      badges.append(tool);
    }
    if (project.progress !== null && project.progress !== undefined) {
      const progress = document.createElement("span");
      progress.className = "mini-badge";
      progress.textContent = `${project.progress}%`;
      badges.append(progress);
    }
    if (project.conflicts && Object.keys(project.conflicts).length) {
      const conflict = document.createElement("span");
      conflict.className = "conflict";
      conflict.textContent = "sources disagree";
      badges.append(conflict);
    }
    left.append(badges);

    const meta = document.createElement("div");
    meta.className = "project-meta";
    const bits = [];
    if (project.last_activity) bits.push(activityText(project.last_activity));
    if (project.stars) bits.push(`★ ${fmt(project.stars)}`);
    if (project.release) bits.push(safe(project.release));
    meta.textContent = bits.join(" · ") || "No activity metadata";

    top.append(left, meta);
    row.append(top);

    const evidence = document.createElement("details");
    evidence.className = "evidence";
    const summary = document.createElement("summary");
    const distinctSources = new Set((project.evidence || []).map(e => e.source)).size;
    summary.textContent = `Evidence from ${distinctSources} source${distinctSources === 1 ? "" : "s"}`;
    const list = document.createElement("div");
    list.className = "evidence-list";
    for (const ev of project.evidence || []) {
      const badge = document.createElement(ev.source_url ? "a" : "span");
      badge.className = "source-badge";
      badge.textContent = ev.claimed ? `${ev.source} · claimed` : ev.source;
      if (ev.source_url) {
        badge.href = ev.source_url;
        badge.target = "_blank";
        badge.rel = "noopener";
      }
      list.append(badge);
    }
    evidence.append(summary, list);
    row.append(evidence);
    return row;
  }

  function render() {
    els.results.textContent = "";
    const total = state.filtered.length;
    els.resultCount.textContent = `${fmt(total)} game${total === 1 ? "" : "s"} match`;
    const fragment = document.createDocumentFragment();
    for (const game of state.filtered.slice(0, state.shown)) {
      const node = els.gameTemplate.content.firstElementChild.cloneNode(true);
      node.querySelector(".game-title").textContent = game.title;
      node.querySelector(".platform-badge").textContent = game.platform;
      node.querySelector(".game-meta").textContent = `${fmt(game.project_count)} project${game.project_count === 1 ? "" : "s"} · ${game.types.map(typeLabel).join(" · ")} · ${game.sources.length} source${game.sources.length === 1 ? "" : "s"}`;
      const badge = node.querySelector(".status-badge");
      badge.dataset.status = game.best_status;
      badge.textContent = statusLabel(game.best_status);
      node.querySelector(".activity").textContent = activityText(game.last_activity);
      const projectList = node.querySelector(".project-list");
      game.projects.forEach(project => projectList.append(makeProjectRow(project)));
      fragment.append(node);
    }
    if (!total) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.innerHTML = "<strong>No matches.</strong><br>Try fewer filters or a broader title.";
      fragment.append(empty);
    }
    els.results.append(fragment);
    els.loadMore.hidden = state.shown >= total;
    if (!els.loadMore.hidden) els.loadMore.textContent = `Show ${fmt(Math.min(80, total - state.shown))} more`;
  }

  function renderSources() {
    els.sourceList.textContent = "";
    for (const source of state.catalog.sources) {
      const item = document.createElement("div");
      item.className = "source-item";
      const link = document.createElement("a");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = source.id;
      const count = document.createElement("span");
      count.textContent = `${fmt(source.records)} records`;
      item.append(link, count);
      els.sourceList.append(item);
    }
  }

  function syncUrl() {
    const p = new URLSearchParams();
    if (els.query.value.trim()) p.set("q", els.query.value.trim());
    if (els.platform.value) p.set("platform", els.platform.value);
    if (els.type.value) p.set("type", els.type.value);
    if (els.status.value) p.set("status", els.status.value);
    if (els.activity.value) p.set("activity", els.activity.value);
    if (els.sort.value !== "recent") p.set("sort", els.sort.value);
    if (els.conflict.checked) p.set("conflicts", "1");
    const next = p.toString() ? `?${p}` : location.pathname;
    history.replaceState(null, "", next);
  }

  function readUrl() {
    const p = new URLSearchParams(location.search);
    els.query.value = p.get("q") || "";
    els.platform.value = p.get("platform") || "";
    els.type.value = p.get("type") || "";
    els.status.value = p.get("status") || "";
    els.activity.value = p.get("activity") || "";
    els.sort.value = p.get("sort") || "recent";
    els.conflict.checked = p.get("conflicts") === "1";
  }

  async function init() {
    try {
      const response = await fetch("data/catalog.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`catalog request failed: ${response.status}`);
      state.catalog = await response.json();
      const { summary, facets } = state.catalog;
      els.gameCount.textContent = fmt(summary.games);
      els.projectCount.textContent = fmt(summary.projects);
      els.sourceCount.textContent = fmt(summary.sources);
      const recent = state.catalog.games.reduce((n,g) => {
        const age = daysAgo(g.last_activity); return n + (age !== null && age <= 30 ? 1 : 0);
      }, 0);
      els.recentCount.textContent = fmt(recent);
      els.refreshStamp.textContent = `Data refreshed ${new Date(state.catalog.generated_at).toLocaleString()}`;
      fillSelect(els.platform, facets.platforms);
      fillSelect(els.type, facets.types, typeLabel);
      fillSelect(els.status, facets.statuses, statusLabel);
      renderSources();
      readUrl();
      applyFilters();
    } catch (error) {
      console.error(error);
      els.resultCount.textContent = "Catalog failed to load";
      els.results.innerHTML = '<div class="empty"><strong>Could not load the catalog.</strong><br>Refresh the page or inspect the deployment status.</div>';
    }
  }

  let timer;
  const schedule = () => { clearTimeout(timer); timer = setTimeout(applyFilters, 70); };
  els.query.addEventListener("input", schedule);
  [els.platform, els.type, els.status, els.activity, els.sort, els.conflict].forEach(el => el.addEventListener("change", applyFilters));
  els.clear.addEventListener("click", () => {
    els.query.value = ""; els.platform.value = ""; els.type.value = ""; els.status.value = "";
    els.activity.value = ""; els.sort.value = "recent"; els.conflict.checked = false; applyFilters(); els.query.focus();
  });
  els.loadMore.addEventListener("click", () => { state.shown += 80; render(); });
  els.sourcesButton.addEventListener("click", () => { els.sourcesPanel.hidden = false; });
  els.closeSources.addEventListener("click", () => { els.sourcesPanel.hidden = true; });
  els.sourcesPanel.addEventListener("click", (e) => { if (e.target === els.sourcesPanel) els.sourcesPanel.hidden = true; });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && !/input|select|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); els.query.focus(); }
    if (e.key === "Escape" && document.activeElement === els.query) { els.query.value = ""; applyFilters(); }
  });
  init();
})();
