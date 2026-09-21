(() => {
  const root = document.getElementById("root");
  if (!root) {
    throw new Error("formula runtime requires the nested scene #root");
  }
  if (!window.katex) {
    throw new Error("formula runtime requires the local KaTeX bundle");
  }

  root.querySelectorAll("[data-tex]").forEach((node) => {
    const tex = node.getAttribute("data-tex");
    if (!tex) return;
    window.katex.render(tex, node, {
      throwOnError: false,
      displayMode: true,
      output: "html",
    });
  });
})();
