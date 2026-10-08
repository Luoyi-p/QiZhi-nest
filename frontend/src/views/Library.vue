<script setup lang="ts">
import { computed, ref } from "vue";
import { BookOpen, LayoutGrid, Plus, Search, Star } from "lucide-vue-next";
import EntryCard from "../components/EntryCard.vue";
import { entries, tracks } from "../store";
import { openEntry, page, query, trackFilter } from "../ui";
import type { Kind } from "../types";
const status = ref("all");
const onlyStarred = ref(false);
const kind = computed<Kind>(() =>
  page.value === "notes"
    ? "note"
    : page.value === "projects"
      ? "project"
      : "resource",
);
const copy = computed(
  () =>
    ({
      resource: {
        title: "资料库",
        eyebrow: "RESOURCES",
        description: "收藏的链接、教程和工具，可按标签搜索或按路线筛选。",
        action: "收藏资料",
      },
      note: {
        title: "我的笔记",
        eyebrow: "NOTES",
        description: "记录学习笔记、遇到的问题和解决方法。",
        action: "写一篇笔记",
      },
      project: {
        title: "实践项目",
        eyebrow: "PROJECTS",
        description: "整理练习项目，记录进展和相关链接。",
        action: "新建项目",
      },
    })[kind.value],
);
const matching = computed(() =>
  entries.value
    .filter(
      (e) =>
        e.kind === kind.value &&
        (!onlyStarred.value || e.starred) &&
        (status.value === "all" || e.status === status.value) &&
        (!trackFilter.value || e.track_id === trackFilter.value) &&
        `${e.title} ${e.content} ${e.tags.join(" ")}`
          .toLowerCase()
          .includes(query.value.toLowerCase()),
    )
    .sort(
      (a, b) =>
        Number(b.starred) - Number(a.starred) ||
        Date.parse(b.updated_at) - Date.parse(a.updated_at),
    ),
);
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">{{ copy.eyebrow }}</div>
      <h1>
        {{ copy.title }}
        <span class="heading-count">{{
          entries.filter((e) => e.kind === kind).length
        }}</span>
      </h1>
      <p>{{ copy.description }}</p>
    </div>
    <button class="button primary" @click="openEntry(kind)">
      <Plus :size="17" />{{ copy.action }}
    </button>
  </section>
  <div class="library-toolbar">
    <div class="filter-tabs" aria-label="按状态筛选">
      <button
        v-for="item in [
          { value: 'all', label: '全部' },
          { value: 'inbox', label: '待探索' },
          { value: 'active', label: '进行中' },
          { value: 'done', label: '已完成' },
        ]"
        :key="item.value"
        :class="{ active: status === item.value }"
        :aria-pressed="status === item.value"
        @click="status = item.value"
      >
        {{ item.label }}
      </button>
    </div>
    <div class="filter-actions">
      <button
        :class="['chip', { selected: onlyStarred }]"
        :aria-pressed="onlyStarred"
        @click="onlyStarred = !onlyStarred"
      >
        <Star :size="15" />置顶</button
      ><select v-model="trackFilter" aria-label="筛选学习路线">
        <option value="">所有路线</option>
        <option v-for="track in tracks" :key="track.id" :value="track.id">
          {{ track.title }}
        </option>
      </select>
    </div>
  </div>
  <div class="result-line">
    <span
      ><LayoutGrid :size="15" />{{ matching.length }} 份{{
        kind === "resource" ? "资料" : kind === "note" ? "笔记" : "项目"
      }}</span
    ><span>置顶优先 · 最近更新</span>
  </div>
  <div v-if="matching.length" class="entry-grid library-grid">
    <EntryCard v-for="entry in matching" :key="entry.id" :entry="entry" />
  </div>
  <div v-else class="empty-state">
    <Search
      v-if="query || status !== 'all' || onlyStarred || trackFilter"
      :size="36"
    /><BookOpen v-else :size="36" />
    <h2>
      {{
        query || status !== "all" || onlyStarred || trackFilter
          ? "暂时没有匹配的内容"
          : "还没有内容"
      }}
    </h2>
    <p>可以换个筛选条件，或把刚刚想到的内容记下来。</p>
    <button class="button primary" @click="openEntry(kind)">
      <Plus :size="16" />{{ copy.action }}
    </button>
  </div>
</template>
