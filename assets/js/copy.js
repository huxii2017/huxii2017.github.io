<script type="text/javascript">
// @ts-nocheck

document.addEventListener("DOMContentLoaded", () => {
document.querySelectorAll("div.sourceCode").forEach(block => {
    // Create "Copy" button
    const button = document.createElement("button");
    button.className = "copy-btn";
    button.innerText = "Copy";
    block.prepend(button);

    // Get language name from <pre class="sourceCode bash">...
    const pre = block.querySelector("pre");
    const lang = (pre.className.match(/sourceCode\s+(\w+)/) || [])[1];
    if (lang) block.setAttribute("data-lang", lang);

    // Copy functionality
    button.addEventListener("click", async () => {
        const code = block.querySelector("code").innerText;
        try {
        await navigator.clipboard.writeText(code);
        button.innerText = "Copied!";
        button.style.background = "#d1f7c4";
        setTimeout(() => {
            button.innerText = "Copy";
            button.style.background = "#f6f8fa";
        }, 1800);
        } catch (err) {
        button.innerText = "Error";
        console.error("Copy failed:", err);
        }
    });
    });
});

/* ===== Responsive Image Auto Sizing ===== */
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("img").forEach(img => {
    img.onload = () => {
        const ratio = img.naturalWidth / img.naturalHeight;

        // 标准分类逻辑：竖图小、横图大
        if (ratio < 0.9) {
        img.classList.add("portrait");  // 竖图
        } else if (ratio > 1.5) {
        img.classList.add("landscape"); // 宽图
        } else {
        img.classList.add("square");    // 方图
        }
    };
    });
});

/* ===== TOC style determination ===== */
document.addEventListener("DOMContentLoaded", function() {
    // 找到内容主体
    const content = document.querySelector("main.content");
    if (!content) return;

    // 创建 TOC 容器
    const toc = document.createElement("nav");
    toc.id = "auto-toc";
    toc.innerHTML = "<h3>📑 Contents</h3><ul></ul>";

    // 把 TOC 插到 content 之前
    const container = document.createElement("div");
    container.className = "toc-container";
    content.parentNode.insertBefore(container, content);
    container.appendChild(toc);
    container.appendChild(content);

    // 扫描标题（支持 h1-h3）
    const headers = content.querySelectorAll("h1, h2, h3");
    const list = toc.querySelector("ul");

    headers.forEach(header => {
    const id = header.id || header.textContent.trim().toLowerCase().replace(/[^\w]+/g, "-");
    header.id = id; // 确保有 id

    const li = document.createElement("li");
    li.innerHTML = `<a href="#${id}">${header.textContent}</a>`;
    list.appendChild(li);
    });

    // 平滑滚动
    list.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute("href"));
        if (target) {
        window.scrollTo({ top: target.offsetTop - 20, behavior: "smooth" });
        }
    });
    });

  // 滚动高亮当前章节
    const links = list.querySelectorAll("a");
    const sections = Array.from(links).map(link => document.querySelector(link.getAttribute("href")));

    window.addEventListener("scroll", () => {
    const scrollPos = window.scrollY + 100;
    sections.forEach((sec, i) => {
        if (sec && sec.offsetTop <= scrollPos && sec.offsetTop + sec.offsetHeight > scrollPos) {
        links.forEach(l => l.classList.remove("active"));
        links[i].classList.add("active");
        }
    });
    });
});
</script>