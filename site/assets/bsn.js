/* buildingSMART Norge – felles skript.
   Henter redigerbart innhold (nyheter, domener, arrangementer, medlemmer) fra Wix,
   styrer menyen, språkvalget og YouTube-visning. */
(function () {
  "use strict";
  var KLIENT = "134b964f-80df-49d8-b2ab-149f8d60b76a"; // offentlig Wix-klient-ID (kun lesetilgang for besøkende)
  var API = "https://www.wixapis.com";
  var EN = document.documentElement.lang === "en";
  var T = EN
    ? { mer: "More about the domain", passer: "Suitable for", leder: "Domain leader", ingen: "No upcoming events right now.", ingenNy: "No news yet.", pamelding: "Sign up", feil: "Could not load content. Please try again later.", tilbake: "Back to the overview", lest: "Read more" }
    : { mer: "Mer om domenet", passer: "Passer for", leder: "Domeneleder", ingen: "Ingen kommende arrangementer akkurat nå.", ingenNy: "Ingen nyheter ennå.", pamelding: "Meld deg på", feil: "Klarte ikke å hente innholdet. Prøv igjen senere.", tilbake: "Tilbake til oversikten", lest: "Les mer" };
  var PREFIKS = EN ? "/en" : "";

  // ---------- meny ----------
  var topp = document.querySelector(".topp");
  if (topp) {
    window.addEventListener("scroll", function () { topp.classList.toggle("skygge", window.scrollY > 8); }, { passive: true });
    topp.querySelectorAll(".meny>li>button").forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var li = b.parentElement, var_apen = li.classList.contains("apen");
        topp.querySelectorAll(".meny>li.apen").forEach(function (x) { x.classList.remove("apen"); });
        if (!var_apen) li.classList.add("apen");
        b.setAttribute("aria-expanded", String(!var_apen));
      });
      if (window.matchMedia("(hover:hover) and (min-width:1061px)").matches) {
        var li = b.parentElement, tid;
        li.addEventListener("mouseenter", function () { clearTimeout(tid); topp.querySelectorAll(".meny>li.apen").forEach(function (x) { if (x !== li) x.classList.remove("apen"); }); li.classList.add("apen"); });
        li.addEventListener("mouseleave", function () { tid = setTimeout(function () { li.classList.remove("apen"); }, 180); });
      }
    });
    var burger = topp.querySelector(".burger");
    if (burger) burger.addEventListener("click", function () { topp.classList.toggle("mobil"); });
    var sprak = topp.querySelector(".sprak");
    if (sprak) sprak.querySelector("button").addEventListener("click", function (e) { e.stopPropagation(); sprak.classList.toggle("apen"); });
    document.addEventListener("click", function () {
      topp.querySelectorAll(".apen").forEach(function (x) { x.classList.remove("apen"); });
    });
  }

  // ---------- YouTube (lastes først ved klikk) ----------
  function aktiverYt(rot) {
    (rot || document).querySelectorAll("button.yt").forEach(function (b) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-id");
        b.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="YouTube"></iframe>';
      }, { once: true });
    });
  }
  aktiverYt();

  // ---------- Wix-tilkobling ----------
  var NOKKEL = "bsn-wix-besok";
  var tokenLover = null;
  function token() {
    if (tokenLover) return tokenLover;
    try {
      var t = JSON.parse(localStorage.getItem(NOKKEL) || "null");
      if (t && t.utloper > Date.now() + 60000) return (tokenLover = Promise.resolve(t.access));
    } catch (e) { /* ingen lagring */ }
    tokenLover = fetch(API + "/oauth2/token", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clientId: KLIENT, grantType: "anonymous" }) })
      .then(function (r) { if (!r.ok) throw new Error("token " + r.status); return r.json(); })
      .then(function (j) {
        try { localStorage.setItem(NOKKEL, JSON.stringify({ access: j.access_token, utloper: Date.now() + j.expires_in * 1000 })); } catch (e) { /* ignorer */ }
        return j.access_token;
      });
    return tokenLover;
  }
  function wix(sti, valg) {
    valg = valg || {};
    return token().then(function (tok) {
      return fetch(API + sti, { method: valg.metode || "POST", headers: { "Content-Type": "application/json", Authorization: tok }, body: valg.body ? JSON.stringify(valg.body) : undefined });
    }).then(function (r) {
      if (r.status === 401 || r.status === 403) { try { localStorage.removeItem(NOKKEL); } catch (e) {} }
      if (!r.ok) throw new Error(sti + " " + r.status);
      return r.json();
    });
  }
  function samling(id, sort, filter, grense) {
    var q = { sort: sort || [{ fieldName: "rekkefolge", order: "ASC" }], paging: { limit: grense || 100 } };
    if (filter) q.filter = filter;
    return wix("/wix-data/v2/items/query", { body: { dataCollectionId: id, query: q } }).then(function (j) {
      return (j.dataItems || []).map(function (d) { return d.data || {}; });
    });
  }

  // ---------- hjelpere ----------
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function bilde(v, b, h, modus) {
    if (!v) return "";
    if (typeof v === "object") v = v.url || v.id || "";
    var fil = "";
    if (v.indexOf("wix:image://") === 0) fil = v.slice(15).split("/")[0].split("#")[0];
    else if (/^[\w-]+~mv2\.[a-z0-9]+$/i.test(v)) fil = v;
    else { var m = v.match(/^https:\/\/static\.wixstatic\.com\/media\/([^/?#]+)/); if (m) fil = m[1]; }
    if (!fil) return v;
    return "https://static.wixstatic.com/media/" + fil + "/v1/" + (modus || "fill") + "/w_" + b + ",h_" + h + ",al_c,q_85/" + fil;
  }
  function dato(v) {
    var d = new Date(v && v.$date ? v.$date : v);
    if (isNaN(d)) return "";
    return d.toLocaleDateString(EN ? "en-GB" : "nb-NO", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Oslo" });
  }
  function feil(el, e) { el.innerHTML = '<p class="laster">' + T.feil + "</p>"; if (window.console) console.warn(e); }
  function innleggUrl(slug) { return PREFIKS + "/nyheter/innlegg.html?n=" + encodeURIComponent(slug); }

  // ---------- nyheter ----------
  function nyhetskort(p) {
    var bildeId = p.media && p.media.displayed !== false && p.media.wixMedia && p.media.wixMedia.image ? (p.media.wixMedia.image.id || p.media.wixMedia.image.url) : "";
    return '<a class="kort" href="' + innleggUrl(p.slug) + '">' +
      (bildeId ? '<img loading="lazy" src="' + bilde(bildeId, 800, 450) + '" alt="">' : "") +
      '<div class="tekst"><h3>' + esc(p.title) + '</h3><p class="dato">' + dato(p.firstPublishedDate) + "</p></div></a>";
  }
  document.querySelectorAll("[data-wix=nyheter]").forEach(function (el) {
    var grense = +el.getAttribute("data-antall") || 50;
    var alle = [], markor = null;
    function hent() {
      var body = markor ? { query: { cursorPaging: { limit: grense, cursor: markor } } } : { query: { sort: [{ fieldName: "firstPublishedDate", order: "DESC" }], cursorPaging: { limit: grense } } };
      return wix("/blog/v3/posts/query", { body: body }).then(function (j) {
        alle = alle.concat(j.posts || []);
        var pm = j.pagingMetadata || {};
        markor = pm.hasNext && pm.cursors ? pm.cursors.next : null;
        el.innerHTML = alle.length ? alle.map(nyhetskort).join("") : '<p class="laster">' + T.ingenNy + "</p>";
        var mer = document.querySelector("[data-wix-mer=nyheter]");
        if (mer) { mer.hidden = !markor; }
      });
    }
    var merKnapp = document.querySelector("[data-wix-mer=nyheter]");
    if (merKnapp) merKnapp.addEventListener("click", function () { hent().catch(function (e) { feil(el, e); }); });
    hent().catch(function (e) { feil(el, e); });
  });

  // Rik tekst (Ricos) -> HTML
  function ricosTekst(noder) {
    return (noder || []).map(function (n) {
      if (n.type !== "TEXT") return ricos([n]);
      var t = esc(n.textData.text).replace(/\n/g, "<br>");
      (n.textData.decorations || []).forEach(function (d) {
        if (d.type === "BOLD") t = "<strong>" + t + "</strong>";
        else if (d.type === "ITALIC") t = "<em>" + t + "</em>";
        else if (d.type === "UNDERLINE") t = "<u>" + t + "</u>";
        else if (d.type === "LINK" && d.linkData && d.linkData.link) {
          var l = d.linkData.link, ny = l.target === "BLANK";
          t = '<a href="' + esc(l.url) + '"' + (ny ? ' target="_blank" rel="noopener"' : "") + ">" + t + "</a>";
        }
      });
      return t;
    }).join("");
  }
  function ricos(noder) {
    return (noder || []).map(function (n) {
      switch (n.type) {
        case "PARAGRAPH": var x = ricosTekst(n.nodes); return x ? "<p>" + x + "</p>" : "";
        case "HEADING": var lv = Math.min(Math.max((n.headingData && n.headingData.level) || 2, 2), 4); return "<h" + lv + ">" + ricosTekst(n.nodes) + "</h" + lv + ">";
        case "BULLETED_LIST": return "<ul>" + ricos(n.nodes) + "</ul>";
        case "ORDERED_LIST": return "<ol>" + ricos(n.nodes) + "</ol>";
        case "LIST_ITEM": return "<li>" + ricos(n.nodes) + "</li>";
        case "BLOCKQUOTE": return "<blockquote>" + ricos(n.nodes) + "</blockquote>";
        case "DIVIDER": return "<hr>";
        case "IMAGE":
          var im = n.imageData && n.imageData.image && n.imageData.image.src;
          var src = im ? (im.id || im.url) : "";
          var lenke = n.imageData && n.imageData.link && n.imageData.link.url;
          var img = src ? '<img loading="lazy" src="' + bilde(src, 1600, 1600, "fit") + '" alt="' + esc(n.imageData.altText || "") + '">' : "";
          var cap = n.imageData && n.imageData.caption ? "<figcaption>" + esc(n.imageData.caption) + "</figcaption>" : "";
          return "<figure>" + (lenke ? '<a href="' + esc(lenke) + '">' + img + "</a>" : img) + cap + "</figure>";
        case "VIDEO":
          var v = n.videoData && n.videoData.video && n.videoData.video.src && n.videoData.video.src.url;
          var yt = v && v.match(/(?:youtu\.be\/|v=|embed\/)([\w-]{11})/);
          return yt ? '<button class="yt" data-id="' + yt[1] + '"><img src="https://i.ytimg.com/vi/' + yt[1] + '/hqdefault.jpg" alt=""></button>' : "";
        case "HTML":
          var u = n.htmlData && n.htmlData.url;
          return u ? '<iframe src="' + esc(u) + '" class="middels"></iframe>' : "";
        case "TABLE": return "<table>" + ricos(n.nodes) + "</table>";
        case "TABLE_ROW": return "<tr>" + ricos(n.nodes) + "</tr>";
        case "TABLE_CELL": return "<td>" + ricos(n.nodes) + "</td>";
        default: return n.nodes ? ricos(n.nodes) : "";
      }
    }).join("");
  }
  var innleggEl = document.querySelector("[data-wix=innlegg]");
  if (innleggEl) {
    var slug = new URLSearchParams(location.search).get("n");
    if (!slug) { location.replace(PREFIKS + "/nyheter.html"); }
    else {
      wix("/blog/v3/posts/slugs/" + encodeURIComponent(slug) + "?fieldsets=RICH_CONTENT&fieldsets=SEO", { metode: "GET" }).then(function (j) {
        var p = j.post;
        document.title = p.title + " – buildingSMART Norge";
        var bildeId = p.media && p.media.displayed !== false && p.media.wixMedia && p.media.wixMedia.image ? (p.media.wixMedia.image.id || p.media.wixMedia.image.url) : "";
        innleggEl.innerHTML = "<h1>" + esc(p.title) + '</h1><p class="dato">' + dato(p.firstPublishedDate) + "</p>" +
          (bildeId ? '<img src="' + bilde(bildeId, 1600, 900, "fit") + '" alt="">' : "") + ricos(p.richContent && p.richContent.nodes);
        aktiverYt(innleggEl);
        var meta = document.querySelector('meta[name=description]');
        if (meta && p.excerpt) meta.setAttribute("content", p.excerpt);
      }).catch(function (e) { feil(innleggEl, e); });
    }
  }

  // ---------- medlemslogoer ----------
  document.querySelectorAll("[data-wix=logoer]").forEach(function (el) {
    samling("Medlemslogoer").then(function (rader) {
      var html = rader.filter(function (r) { return r.logo; }).map(function (r) {
        return '<img loading="lazy" src="' + bilde(r.logo, 360, 120, "fit") + '" alt="' + esc(r.navn) + '" title="' + esc(r.navn) + '">';
      }).join("");
      el.innerHTML = html + html.replace(/<img /g, '<img aria-hidden="true" ');
    }).catch(function (e) { feil(el, e); });
  });

  // ---------- medlemsliste ----------
  document.querySelectorAll("[data-wix=medlemmer]").forEach(function (el) {
    samling("Medlemmer", [{ fieldName: "navn", order: "ASC" }], null, 1000).then(function (rader) {
      rader.sort(function (a, b) { return String(a.navn).localeCompare(String(b.navn), "nb"); });
      el.innerHTML = rader.map(function (r) { return "<li>" + esc(r.navn) + "</li>"; }).join("");
    }).catch(function (e) { feil(el, e); });
  });

  // ---------- domener ----------
  function domenekort(d) {
    var navn = EN && d.navnEn ? d.navnEn : d.navn, ingress = EN && d.ingressEn ? d.ingressEn : d.ingress;
    var passer = (EN && d.passerForEn && d.passerForEn.length ? d.passerForEn : d.passerFor) || [];
    return '<article class="domene"><h3>' + esc(navn) + "</h3><p>" + esc(ingress) + '</p>' +
      '<a class="merlenke" href="' + PREFIKS + "/fagnettverk/" + esc(d.slug) + '.html">' + T.mer + " →</a>" +
      (passer.length ? '<div><h4 style="margin:6px 0 8px;font-weight:400">' + T.passer + '</h4><div class="brikker">' + passer.map(function (p) { return "<span>" + esc(p) + "</span>"; }).join("") + "</div></div>" : "") +
      '<div class="leder">' + (d.lederBilde ? '<img loading="lazy" src="' + bilde(d.lederBilde, 160, 160) + '" alt="">' : "") +
      "<div><small>" + T.leder + "</small><b>" + esc(d.leder) + "</b></div></div></article>";
  }
  document.querySelectorAll("[data-wix=domener]").forEach(function (el) {
    samling("Domener").then(function (rader) { el.innerHTML = rader.map(domenekort).join(""); }).catch(function (e) { feil(el, e); });
  });
  document.querySelectorAll("[data-wix=domeneleder]").forEach(function (el) {
    var slug = el.getAttribute("data-domene");
    samling("Domener", null, { slug: { $eq: slug } }, 1).then(function (rader) {
      var d = rader[0]; if (!d) { el.remove(); return; }
      el.innerHTML = (d.lederBilde ? '<img src="' + bilde(d.lederBilde, 200, 200) + '" alt="">' : "") +
        "<div><p style=\"color:var(--gra)\">" + T.leder + "</p><p><b>" + esc(d.leder) + "</b></p>" +
        (d.epost ? '<p><a href="mailto:' + esc(d.epost) + '">' + esc(d.epost) + "</a></p>" : "") +
        (d.lederLinkedin ? '<p><a href="' + esc(d.lederLinkedin) + '" target="_blank" rel="noopener">LinkedIn</a></p>' : "") + "</div>";
    }).catch(function () { el.remove(); });
  });

  // ---------- arrangementer ----------
  function arrkort(a) {
    var tittel = EN && a.tittelEn ? a.tittelEn : a.tittel;
    var href = a.pameldingslenke || PREFIKS + "/arrangementer.html";
    var ekstern = /^https?:/.test(href);
    return '<a class="kort" href="' + esc(href) + '"' + (ekstern ? ' target="_blank" rel="noopener"' : "") + ">" +
      (a.bilde ? '<img loading="lazy" src="' + bilde(a.bilde, 800, 450) + '" alt="">' : "") +
      '<div class="tekst"><h3>' + esc(tittel) + '</h3><p class="dato">' + dato(a.dato) + (a.tid ? " · " + esc(a.tid) : "") + "</p></div></a>";
  }
  document.querySelectorAll("[data-wix=arrangementer]").forEach(function (el) {
    var domene = el.getAttribute("data-domene");
    var idag = new Date(); idag.setHours(0, 0, 0, 0);
    var filter = { dato: { $gte: { $date: idag.toISOString() } } };
    if (domene) filter.domene = { $eq: domene }; else filter.visPaForsiden = { $eq: true };
    samling("Arrangementer", [{ fieldName: "dato", order: "ASC" }], filter, +el.getAttribute("data-antall") || 6).then(function (rader) {
      el.innerHTML = rader.length ? rader.map(arrkort).join("") : '<p class="laster">' + T.ingen + "</p>";
    }).catch(function (e) { feil(el, e); });
  });
})();
