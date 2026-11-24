const LISTING_URL = "https://vpm.k-neco.com/index.json";
const BOOTH_ITEM_URL = "https://the-cattail.booth.pm/items/8783972";
const GITHUB_PACKAGE_URL = "https://github.com/rinchan-hoshino/afk-motion-patcher";
const LANG_STORAGE_KEY = "k-neco-vpm-lang";

const I18N = {
  ja: {
    pageTitle: "THE_cattail VPM — VRChat パッケージリポジトリ",
    heroBadge: "VRChat Creator Companion · 公式 VPM リポジトリ",
    heroTitle: "THE_cattail VPM",
    heroSubtitle: "VRChat向け汎用エディターツールを配信する公式VPMリポジトリです。",
    addToVcc: "VCC に追加",
    copyUrl: "URLをコピー",
    copied: "コピーしました",
    repoHint: "VRChat Creator Companion (VCC) および ALCOM に対応しています。",
    packagesHeading: "収録パッケージ",
    loadingPackages: "パッケージ一覧を読み込み中...",
    loadError: "index.json の読み込みに失敗しました。再読み込みをお試しください。",
    emptyPackages: "公開中のパッケージはありません。",
    guideHeading: "導入手順",
    step1Title: "リポジトリを追加",
    step1Desc: "「VCC に追加」をクリックするか、URLをコピーして VCC / ALCOM に登録します。",
    step2Title: "追加を承認",
    step2Desc: "VCCの確認画面でリポジトリ情報を確認し、「I Understand」をクリックします。",
    step3Title: "プロジェクトへ導入",
    step3Desc: "対象プロジェクトの「Manage Project」から必要なツールを追加して完了です。",
    btnGithub: "GitHub ソース",
    btnBooth: "BOOTH ページ",
    btnDownload: ".zip をダウンロード",
    pkgDescOverride: {
      "com.the-cattail.afk-motion-patcher":
        "GoGoLoco や既存ダンスを壊さず、別アバターの AFK モーション（導入・待機・復帰）を非破壊で移植・微調整できる NDMF エディター拡張です。",
    },
  },
  en: {
    pageTitle: "THE_cattail VPM — VRChat Package Repository",
    heroBadge: "VRChat Creator Companion · Official VPM Repository",
    heroTitle: "THE_cattail VPM",
    heroSubtitle: "Official VPM repository for general-purpose VRChat editor tools by THE_cattail.",
    addToVcc: "Add to VCC",
    copyUrl: "Copy URL",
    copied: "Copied!",
    repoHint: "Compatible with VRChat Creator Companion (VCC) and ALCOM.",
    packagesHeading: "Packages",
    loadingPackages: "Loading packages...",
    loadError: "Failed to load index.json. Please refresh the page.",
    emptyPackages: "No packages published yet.",
    guideHeading: "Quick Setup",
    step1Title: "Add Repository",
    step1Desc: "Click \"Add to VCC\" or copy the repository URL into VCC / ALCOM.",
    step2Title: "Confirm Source",
    step2Desc: "Review the repository details in VCC and click \"I Understand\".",
    step3Title: "Install to Project",
    step3Desc: "Open \"Manage Project\" in VCC / ALCOM and add the package.",
    btnGithub: "GitHub Source",
    btnBooth: "BOOTH Page",
    btnDownload: "Download .zip",
    pkgDescOverride: {
      "com.the-cattail.afk-motion-patcher":
        "Port another VRChat avatar's AFK pose (Intro / Loop / Outro) onto your avatar non-destructively via NDMF without breaking GoGoLoco or existing Action layers.",
    },
  },
  zh: {
    pageTitle: "THE_cattail VPM — VRChat 官方软件源",
    heroBadge: "VRChat Creator Companion · 官方 VPM 软件源",
    heroTitle: "THE_cattail VPM",
    heroSubtitle: "THE_cattail 官方 VPM 软件源，提供通用 VRChat 编辑器工具包。",
    addToVcc: "添加到 VCC",
    copyUrl: "复制源地址",
    copied: "已复制",
    repoHint: "兼容 VRChat Creator Companion (VCC) 与 ALCOM。",
    packagesHeading: "收录工具包",
    loadingPackages: "正在加载工具包列表...",
    loadError: "无法读取 index.json，请刷新重试。",
    emptyPackages: "暂无已发布的工具包。",
    guideHeading: "安装步骤",
    step1Title: "添加软件源",
    step1Desc: "点击「添加到 VCC」，或复制源地址手动添加至 VCC / ALCOM。",
    step2Title: "确认授权",
    step2Desc: "在弹出的仓库信息确认窗口中点击「I Understand」。",
    step3Title: "安装到工程",
    step3Desc: "打开目标工程的「Manage Project」，选择所需工具包安装即可。",
    btnGithub: "GitHub 源码",
    btnBooth: "BOOTH 页面",
    btnDownload: "下载 .zip",
    pkgDescOverride: {
      "com.the-cattail.afk-motion-patcher":
        "在不破坏原有 GoGoLoco 与自定义动作的前提下，将其他 VRChat 模型的整套 AFK 待机动作非破坏移植到当前模型，并提供耳尾、宽袖防穿模与实时对比预览调校。",
    },
  },
};

const DEP_LABELS = {
  "com.vrchat.avatars": "VRChat Avatars SDK",
  "nadena.dev.ndmf": "NDMF",
};

let currentLang = "ja";
let cachedListing = null;
let copyResetTimer = null;

function detectInitialLang() {
  const paramLang = new URLSearchParams(window.location.search).get("lang");
  if (paramLang && I18N[paramLang]) return paramLang;

  try {
    const saved = localStorage.getItem(LANG_STORAGE_KEY);
    if (saved && I18N[saved]) return saved;
  } catch {
    // Ignore storage errors in restricted contexts.
  }

  const langs = navigator.languages && navigator.languages.length
    ? navigator.languages
    : [navigator.language || "en"];

  for (const raw of langs) {
    const code = String(raw).toLowerCase();
    if (code.startsWith("ja")) return "ja";
    if (code.startsWith("zh")) return "zh";
    if (code.startsWith("en")) return "en";
  }
  return "en";
}

function compareSemverDesc(a, b) {
  const parse = (v) => v.split("-")[0].split(".").map((n) => Number.parseInt(n, 10) || 0);
  const pa = parse(a);
  const pb = parse(b);
  for (let i = 0; i < Math.max(pa.length, pb.length); i += 1) {
    const diff = (pb[i] || 0) - (pa[i] || 0);
    if (diff !== 0) return diff;
  }
  return b.localeCompare(a);
}

function pickLatestVersion(versionsObj) {
  const keys = Object.keys(versionsObj || {});
  if (keys.length === 0) return null;
  keys.sort(compareSemverDesc);
  return versionsObj[keys[0]];
}

function applyTranslations() {
  const t = I18N[currentLang] || I18N.en;
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : currentLang;
  document.title = t.pageTitle;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (key && t[key]) {
      el.textContent = t[key];
    }
  });

  document.querySelectorAll(".lang-btn").forEach((btn) => {
    const active = btn.dataset.lang === currentLang;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", String(active));
  });
}

function createEl(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function renderPackages() {
  const container = document.getElementById("packageList");
  const countPill = document.getElementById("packageCount");
  const t = I18N[currentLang] || I18N.en;

  if (!cachedListing) return;

  const entries = Object.entries(cachedListing.packages || {});
  container.innerHTML = "";

  if (entries.length === 0) {
    countPill.hidden = true;
    container.appendChild(createEl("div", "state-card", t.emptyPackages));
    return;
  }

  countPill.hidden = false;
  countPill.textContent = String(entries.length);

  for (const [pkgId, pkgData] of entries) {
    const latest = pickLatestVersion(pkgData.versions);
    if (!latest) continue;

    const card = createEl("article", "package-card");
    card.dataset.packageId = pkgId;

    const head = createEl("div", "package-head");
    const titleWrap = createEl("div");

    const titleRow = createEl("div", "package-title-row");
    titleRow.appendChild(createEl("h3", "package-name", latest.displayName || pkgId));
    titleRow.appendChild(createEl("span", "version-label", `v${latest.version}`));
    if (latest.license) {
      titleRow.appendChild(createEl("span", "license-label", latest.license));
    }
    titleWrap.appendChild(titleRow);
    titleWrap.appendChild(createEl("div", "package-id", pkgId));
    head.appendChild(titleWrap);

    if (Array.isArray(latest.keywords) && latest.keywords.length > 0) {
      const kwRow = createEl("div", "keywords-row");
      for (const kw of latest.keywords) {
        kwRow.appendChild(createEl("span", "keyword-tag", kw));
      }
      head.appendChild(kwRow);
    }

    card.appendChild(head);

    const localizedDesc = (t.pkgDescOverride && t.pkgDescOverride[pkgId]) || latest.description || "";
    card.appendChild(createEl("p", "package-desc", localizedDesc));

    const depsRow = createEl("div", "deps-row");
    if (latest.unity) {
      const unityBadge = createEl("span", "dep-badge");
      unityBadge.appendChild(createEl("span", "dep-key", "Unity"));
      unityBadge.appendChild(createEl("span", "dep-val", latest.unity));
      depsRow.appendChild(unityBadge);
    }

    const vpmDeps = latest.vpmDependencies || {};
    for (const [depId, range] of Object.entries(vpmDeps)) {
      const badge = createEl("span", "dep-badge");
      badge.appendChild(createEl("span", "dep-key", DEP_LABELS[depId] || depId));
      badge.appendChild(createEl("span", "dep-val", range));
      depsRow.appendChild(badge);
    }
    card.appendChild(depsRow);

    const footer = createEl("div", "package-footer");
    const links = createEl("div", "package-links");

    const githubUrl = (latest.author && latest.author.url) || GITHUB_PACKAGE_URL;
    const githubLink = createEl("a", "btn btn-secondary btn-sm", t.btnGithub);
    githubLink.href = githubUrl;
    githubLink.target = "_blank";
    githubLink.rel = "noopener noreferrer";
    links.appendChild(githubLink);

    const boothLink = createEl("a", "btn btn-secondary btn-sm", t.btnBooth);
    boothLink.href = BOOTH_ITEM_URL;
    boothLink.target = "_blank";
    boothLink.rel = "noopener noreferrer";
    links.appendChild(boothLink);

    if (latest.url) {
      const zipLink = createEl("a", "btn btn-secondary btn-sm", t.btnDownload);
      zipLink.href = latest.url;
      zipLink.target = "_blank";
      zipLink.rel = "noopener noreferrer";
      links.appendChild(zipLink);
    }

    footer.appendChild(links);
    card.appendChild(footer);
    container.appendChild(card);
  }
}

function setLanguage(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  try {
    localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    // Ignore storage errors.
  }
  applyTranslations();
  if (cachedListing) {
    renderPackages();
  }
}

async function copyRepoUrl() {
  const urlField = document.getElementById("vccUrlField");
  const copyBtn = document.getElementById("vccUrlFieldCopy");
  const copyLabel = document.getElementById("copyBtnLabel");
  const t = I18N[currentLang] || I18N.en;

  try {
    await navigator.clipboard.writeText(urlField.value);
  } catch {
    urlField.select();
    document.execCommand("copy");
  }

  copyBtn.classList.add("is-copied");
  copyLabel.textContent = t.copied;

  clearTimeout(copyResetTimer);
  copyResetTimer = setTimeout(() => {
    copyBtn.classList.remove("is-copied");
    copyLabel.textContent = (I18N[currentLang] || I18N.en).copyUrl;
  }, 1600);
}

async function loadListing() {
  const container = document.getElementById("packageList");
  const t = I18N[currentLang] || I18N.en;

  try {
    const res = await fetch("./index.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    cachedListing = await res.json();
    renderPackages();
  } catch (err) {
    console.error("Failed to load ./index.json:", err);
    container.innerHTML = "";
    container.appendChild(createEl("div", "state-card", t.loadError));
  }
}

function init() {
  currentLang = detectInitialLang();
  applyTranslations();

  const vccBtn = document.getElementById("vccAddRepoButton");
  vccBtn.href = `vcc://vpm/addRepo?url=${encodeURIComponent(LISTING_URL)}`;

  document.getElementById("vccUrlFieldCopy").addEventListener("click", copyRepoUrl);

  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => setLanguage(btn.dataset.lang));
  });

  loadListing();
}

init();
