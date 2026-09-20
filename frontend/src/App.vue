<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import {
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  Code2,
  FileText,
  Home as HomeIcon,
  Leaf,
  Menu,
  Plus,
  Route,
  Search,
  Settings2,
  Sprout,
  X,
  History,
  AlertCircle,
  RefreshCw,
} from "lucide-vue-next";
import Home from "./views/Home.vue";
import Tracks from "./views/Tracks.vue";
import Library from "./views/Library.vue";
import Timeline from "./views/Timeline.vue";
import Settings from "./views/Settings.vue";
import Editors from "./components/Editors.vue";
import {
  entries,
  loadError,
  loading,
  loadWorkspace,
  notice,
  showDemo,
  tracks,
} from "./store";
import { modal, navigate, openEntry, page, query } from "./ui";
import type { Page } from "./types";
const menuOpen = ref(false);
const searchInput = ref<HTMLInputElement>();
const mainContent = ref<HTMLElement>();
const sidebar = ref<HTMLElement>();
const menuButton = ref<HTMLButtonElement>();
const menuCloseButton = ref<HTMLButtonElement>();
const originalOverflow = document.body.style.overflow;
watch(menuOpen, async (open) => {
  document.body.style.overflow = open ? "hidden" : originalOverflow;
  if (open) {
    await nextTick();
    menuCloseButton.value?.focus();
  }
});
async function closeMenu() {
  menuOpen.value = false;
  await nextTick();
  menuButton.value?.focus();
}
function resizeNavigation() {
  if (window.innerWidth >= 1024) menuOpen.value = false;
}
watch(page, async () => {
  menuOpen.value = false;
  await nextTick();
  mainContent.value?.focus({ preventScroll: true });
  window.scrollTo({ top: 0, behavior: "instant" });
});
const navigation = computed(() => [
  { id: "home" as Page, name: "工作台", icon: HomeIcon },
  {
    id: "tracks" as Page,
    name: "学习路线",
    icon: Route,
    count: tracks.value.length,
  },
  {
    id: "library" as Page,
    name: "资料库",
    icon: BookOpen,
    count: entries.value.filter((e) => e.kind === "resource").length,
  },
  {
    id: "notes" as Page,
    name: "我的笔记",
    icon: FileText,
    count: entries.value.filter((e) => e.kind === "note").length,
  },
  {
    id: "projects" as Page,
    name: "实践项目",
    icon: Code2,
    count: entries.value.filter((e) => e.kind === "project").length,
  },
  { id: "timeline" as Page, name: "成长时间线", icon: History },
]);
const currentTitle = computed(
  () => navigation.value.find((n) => n.id === page.value)?.name || "我的数据",
);
const currentView = computed(
  () =>
    ({
      home: Home,
      tracks: Tracks,
      library: Library,
      notes: Library,
      projects: Library,
      timeline: Timeline,
      settings: Settings,
    })[page.value],
);
const date = new Intl.DateTimeFormat("zh-CN", {
  month: "long",
  day: "numeric",
  weekday: "long",
}).format(new Date());
const searchResults = computed(() => {
  if (!query.value.trim() || !["home", "settings"].includes(page.value))
    return [];
  const text = query.value.toLowerCase();
  return entries.value
    .filter((e) =>
      `${e.title} ${e.content} ${e.tags.join(" ")}`
        .toLowerCase()
        .includes(text),
    )
    .slice(0, 8);
});
const globalSearching = computed(
  () => !!query.value.trim() && ["home", "settings"].includes(page.value),
);
async function go(target: Page) {
  navigate(target);
  menuOpen.value = false;
  await nextTick();
  mainContent.value?.focus({ preventScroll: true });
}
function keyboard(event: KeyboardEvent) {
  if (menuOpen.value && event.key === "Tab") {
    const controls = sidebar.value?.querySelectorAll<HTMLElement>(
      "a[href], button:not(:disabled)",
    );
    const first = controls?.[0];
    const last = controls?.[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  }
  if (
    !menuOpen.value &&
    (event.ctrlKey || event.metaKey) &&
    event.key.toLowerCase() === "k"
  ) {
    event.preventDefault();
    searchInput.value?.focus();
  }
  if (event.key === "Escape") {
    query.value = "";
    if (menuOpen.value) closeMenu();
  }
}
onMounted(() => {
  loadWorkspace();
  window.addEventListener("keydown", keyboard);
  window.addEventListener("resize", resizeNavigation);
});
onBeforeUnmount(() => {
  window.removeEventListener("keydown", keyboard);
  window.removeEventListener("resize", resizeNavigation);
  document.body.style.overflow = originalOverflow;
});
</script>

<template>
  <div class="app-shell">
    <a
      class="skip-link"
      :inert="menuOpen"
      href="#main-content"
      @click.prevent="mainContent?.focus()"
      >跳到主要内容</a
    >
    <button
      v-if="menuOpen"
      class="sidebar-backdrop"
      aria-label="关闭导航"
      tabindex="-1"
      @click="closeMenu"
    />
    <aside ref="sidebar" :class="['sidebar', { open: menuOpen }]">
      <button
        ref="menuCloseButton"
        class="icon-button sidebar-close"
        aria-label="收起导航"
        @click="closeMenu"
      >
        <X :size="20" />
      </button>
      <a href="#home" class="brand" @click.prevent="go('home')"
        ><span class="brand-mark"
          ><svg viewBox="0 0 32 32" aria-hidden="true">
            <path d="M8 25V7l16 18V7M8 16h16" /></svg></span
        ><span>栖知 <small>Nest</small></span></a
      >
      <div class="workspace-label">
        <span class="workspace-avatar">我</span>
        <div>我的数字空间<small>PERSONAL WORKSPACE</small></div>
        <Leaf :size="15" />
      </div>
      <div class="nav-caption">WORKSPACE / 我的空间</div>
      <nav aria-label="主导航">
        <a
          v-for="item in navigation"
          :key="item.id"
          :href="`#${item.id}`"
          :class="['nav-link', { active: page === item.id }]"
          :aria-current="page === item.id ? 'page' : undefined"
          @click.prevent="go(item.id)"
          ><component :is="item.icon" :size="19" /><span>{{ item.name }}</span
          ><small v-if="item.count !== undefined">{{ item.count }}</small></a
        >
      </nav>
      <div class="sidebar-grow" />
      <div class="sidebar-note">
        <Sprout :size="24" />
        <p>连接知识，也连接自己。</p>
        <span
          >收藏是开始，理解是过程。<br />把每一次输入，留给未来的自己。</span
        >
        <div class="sidebar-note-line" />
      </div>
      <a
        href="#settings"
        :class="['nav-link', 'settings-link', { active: page === 'settings' }]"
        :aria-current="page === 'settings' ? 'page' : undefined"
        @click.prevent="go('settings')"
        ><Settings2 :size="19" /><span>数据与设置</span></a
      >
      <div class="sidebar-bottom">
        <span class="user-avatar">N</span>
        <div>个人工作台<small>Local-first · v0.1</small></div>
        <span class="local-indicator" title="本地优先应用" />
      </div>
    </aside>
    <div class="main-shell" :inert="menuOpen">
      <header class="topbar">
        <div class="breadcrumb">
          <button
            class="icon-button mobile-menu"
            ref="menuButton"
            aria-label="打开导航"
            :aria-expanded="menuOpen"
            @click="menuOpen = true"
          >
            <Menu :size="22" /></button
          ><span class="breadcrumb-root">我的空间</span
          ><span class="slash">/</span><span>{{ currentTitle }}</span>
        </div>
        <div class="topbar-actions">
          <div class="search-wrap">
            <Search :size="17" /><input
              ref="searchInput"
              v-model="query"
              placeholder="搜索你的积累…"
              aria-label="搜索你的积累"
            /><button
              v-if="query"
              class="icon-button search-clear"
              aria-label="清空搜索"
              @click="query = ''"
            >
              <X :size="14" /></button
            ><kbd v-else>Ctrl K</kbd>
            <div v-if="globalSearching" class="search-results">
              <button
                v-for="entry in searchResults"
                :key="entry.id"
                @click="
                  openEntry(entry.kind, entry);
                  query = '';
                "
              >
                <FileText :size="16" /><span>{{ entry.title }}</span
                ><ArrowUpRight :size="14" />
              </button>
              <p v-if="!searchResults.length">没有找到相关积累</p>
            </div>
          </div>
          <button
            class="button primary top-capture"
            aria-label="快速收集"
            :disabled="loading || !!loadError"
            @click="openEntry('resource')"
          >
            <Plus :size="17" /><span>快速收集</span>
          </button>
        </div>
      </header>
      <main id="main-content" ref="mainContent" tabindex="-1">
        <div class="context-row">
          <span><span class="context-dot" />{{ date }}</span
          ><span v-if="showDemo" class="demo-context"
            >含示例内容<button @click="go('settings')">
              管理<ArrowUpRight :size="12" /></button></span
          ><span v-else class="demo-context">只看我的积累</span>
        </div>
        <section v-if="loading" class="loading-state" aria-live="polite">
          <span class="loader" />
          <h2>正在打开你的空间…</h2>
        </section>
        <section
          v-else-if="loadError"
          class="empty-state error-state"
          role="alert"
        >
          <AlertCircle :size="36" />
          <h2>暂时没有连上数据服务</h2>
          <p>{{ loadError }}</p>
          <button class="button primary" @click="loadWorkspace">
            <RefreshCw :size="16" />重新连接
          </button>
        </section>
        <component :is="currentView" v-else :key="page" />
      </main>
    </div>
    <Editors v-if="modal" :key="modal" />
    <Transition name="toast"
      ><div v-if="notice" class="toast" role="status">
        <CheckCircle2 :size="18" />{{ notice }}
      </div></Transition
    >
  </div>
</template>
