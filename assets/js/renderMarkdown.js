// renderMarkdown.js
function renderMarkdown(mdPath, targetId = "viewer") {
    fetch(mdPath)
      .then(res => {
        if (!res.ok) throw new Error("Markdown not found: " + mdPath);
        return res.text();
      })
      .then(text => {
        const baseDir = mdPath.substring(0, mdPath.lastIndexOf("/") + 1);
        const fixedText = text.replace(/!\[(.*?)\]\((?!http)(.*?)\)/g, (match, alt, path) => {
          return `![${alt}](${baseDir}${path})`;
        });
  
        // ✅ 设置 marked 支持代码高亮
        marked.setOptions({
          highlight: function(code, lang) {
            if (hljs.getLanguage(lang)) {
              return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
          },
          langPrefix: 'hljs language-', // highlight.js 的 class 格式
        });
  
        const html = marked.parse(fixedText);
        const viewer = document.getElementById(targetId);
        viewer.innerHTML = html;
        viewer.classList.add("markdown-viewer");
  
        // 处理代码块高亮
        document.querySelectorAll('pre code').forEach(block => {
          hljs.highlightElement(block);
        });
      })
      .catch(err => {
        document.getElementById(targetId).innerHTML =
          `<p style="color:#ffb3b3;">⚠️ Failed to load markdown:</p><pre>${err}</pre>`;
      });
  }