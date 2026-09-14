<script setup lang="ts">
import { ArrowUpRight, BookOpen, Code2, FileText, Star } from "lucide-vue-next";
import type { Entry } from "../types";
import { shortDate, toggleStar, trackName } from "../store";
import { openEntry } from "../ui";
defineProps<{ entry: Entry }>();
const labels = { resource: "资料", note: "笔记", project: "项目" };
const statuses = { inbox: "待探索", active: "进行中", done: "已完成" };
const icons = { resource: BookOpen, note: FileText, project: Code2 };
</script>

<template>
  <article class="entry-card">
    <div class="entry-top">
      <div :class="['entry-icon', entry.kind]">
        <component :is="icons[entry.kind]" :size="20" />
      </div>
      <span class="entry-type">{{ labels[entry.kind] }}</span
      ><span v-if="entry.demo" class="demo-tag">示例</span
      ><button
        :class="['icon-button', 'star-button', { starred: entry.starred }]"
        :aria-label="
          entry.starred ? `取消置顶 ${entry.title}` : `置顶 ${entry.title}`
        "
        :aria-pressed="entry.starred"
        @click="toggleStar(entry)"
      >
        <Star :size="17" :fill="entry.starred ? 'currentColor' : 'none'" />
      </button>
    </div>
    <button class="entry-title" @click="openEntry(entry.kind, entry)">
      {{ entry.title }}
    </button>
    <p class="entry-summary">
      {{ entry.content || "留一段自己的理解，下次回来就能接着开始。" }}
    </p>
    <div class="tags">
      <span v-for="tag in entry.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
    </div>
    <div class="entry-bottom">
      <span :title="trackName(entry.track_id)">{{
        entry.track_id ? trackName(entry.track_id) : shortDate(entry.updated_at)
      }}</span
      ><a
        v-if="entry.url"
        :href="entry.url"
        target="_blank"
        rel="noopener noreferrer"
        class="text-button"
        :aria-label="`访问 ${entry.title}`"
        >访问 <ArrowUpRight :size="14" /></a
      ><span v-else :class="['status-tag', entry.status]">{{
        statuses[entry.status]
      }}</span>
    </div>
  </article>
</template>
