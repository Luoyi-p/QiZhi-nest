<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import {
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  Code2,
  Command,
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
function go(target: Page) {
  navigate(target);
  menuOpen.value = false;
}
function keyboard(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    searchInput.value?.focus();
  }
  if (event.key === "Escape") {
    query.value = "";
    menuOpen.value = false;
  }
}
onMounted(() => {
  loadWorkspace();
  window.addEventListener("keydown", keyboard);
});
onBeforeUnmount(() => window.removeEventListener("keydown", keyboard));
</script>

<template>
  <div class="app-shell">
    <button
      v-if="menuOpen"
      class="sidebar-backdrop"
      aria-label="关闭导航"
      @click="menuOpen = false"
    />
    <aside :class="['sidebar', { open: menuOpen }]">
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
      <div class="nav-caption">我的空间</div>
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
        <p>知识有自己的生长速度。</p>
        <span>给好奇心一点时间，<br />给积累一个自己的家。</span>
        <div class="sidebar-note-line" />
      </div>
      <a
        href="#settings"
        :class="['nav-link', 'settings-link', { active: page === 'settings' }]"
        @click.prevent="go('settings')"
        ><Settings2 :size="19" /><span>数据与设置</span></a
      >
      <div class="sidebar-bottom">
        <span class="user-avatar">N</span>
        <div>个人工作台<small>Local-first · v0.1</small></div>
        <span class="local-indicator" title="本地优先应用" />
      </div>
    </aside>
    <div class="main-shell">
      <header class="topbar">
        <div class="breadcrumb">
          <button
            class="icon-button mobile-menu"
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
      <main id="main-content">
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
