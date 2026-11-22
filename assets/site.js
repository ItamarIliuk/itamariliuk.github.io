// Idioma (PT/EN, lembrado entre as páginas) e botões de copiar comandos.
(function () {
  var html = document.documentElement;
  var ouvintes = [];
  window.onLang = function (fn) { ouvintes.push(fn); };
  window.L = function (pt, en) { return html.lang === "en" ? en : pt; };
  function setLang(l) {
    html.lang = l;
    document.querySelectorAll("[data-set-lang]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.setLang === l)); });
    try { localStorage.setItem("lang", l); } catch (e) {}
    ouvintes.forEach(function (fn) { try { fn(l); } catch (e) {} });
  }
  window.setLang = setLang;
  var salvo = null;
  try { salvo = localStorage.getItem("lang"); } catch (e) {}
  if (!salvo) salvo = (navigator.language || "").toLowerCase().indexOf("pt") === 0 ? "pt" : "en";
  html.lang = salvo;
  document.addEventListener("DOMContentLoaded", function () {
    setLang(salvo);
    document.querySelectorAll("[data-set-lang]").forEach(function (b) { b.addEventListener("click", function () { setLang(b.dataset.setLang); }); });
    document.querySelectorAll(".cmd").forEach(function (el) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "copiar";
      var rot = function () { b.textContent = L("Copiar", "Copy"); };
      rot(); onLang(rot);
      b.addEventListener("click", function () {
        var texto = Array.prototype.filter.call(el.childNodes, function (n) { return n.nodeType === 3; }).map(function (n) { return n.textContent; }).join("").trim();
        var ok = function () { b.textContent = L("Copiado", "Copied"); setTimeout(rot, 1500); };
        var seleciona = function () { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(ok, seleciona); else seleciona();
      });
      el.appendChild(b);
    });
  });
})();
