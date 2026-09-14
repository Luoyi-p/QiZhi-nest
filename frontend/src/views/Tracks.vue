<script setup lang="ts">
import { computed, ref } from "vue";
import {
  ArrowUpRight,
  BookOpen,
  Check,
  Circle,
  Clock3,
  Plus,
  Route,
} from "lucide-vue-next";
import {
  entries,
  notify,
  progress,
  saveTrack,
  trackInput,
  tracks,
} from "../store";
import { openEntry, openSession, openTrack, query } from "../ui";
import type { Track } from "../types";
const filtered = computed(() =>
  tracks.value.filter((t) =>
    `${t.title} ${t.description}`
      .toLowerCase()
      .includes(query.value.toLowerCase()),
  ),
);
const pending = ref(new Set<string>());
async function toggle(track: Track, index: number) {
  if (pending.value.has(track.id)) return;
  pending.value.add(track.id);
  try {
    await saveTrack(
      {
        ...trackInput(track),
        milestones: track.milestones.map((m, i) => ({
          ...m,
          done: i === index ? !m.done : m.done,
        })),
      },
      track.id,
    );
  } catch (error) {
    notify((error as Error).message);
  } finally {
    pending.value.delete(track.id);
  }
}
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">FOLLOW YOUR CURIOSITY</div>
      <h1>学习路线</h1>
      <p>从一个想弄懂的问题开始，一步一步走到自己的答案。</p>
    </div>
    <button class="button primary" @click="openTrack()">
      <Plus :size="17" />新建路线
    </button>
  </section>
  <div class="route-grid">
    <article
      v-for="track in filtered"
      :key="track.id"
      :class="['route-card', track.color]"
    >
      <div class="route-card-top">
        <span class="route-icon"><Route :size="24" /></span
        ><span v-if="track.demo" class="demo-tag">示例路线</span
        ><button
          class="icon-button"
          :aria-label="`编辑 ${track.title}`"
          @click="openTrack(track)"
        >
          <ArrowUpRight :size="20" />
        </button>
      </div>
      <h2>{{ track.title }}</h2>
      <p class="route-description">
        {{ track.description || "留一点空间，给接下来想探索的事。" }}
      </p>
      <div class="route-progress-label">
        <span
          >{{ track.milestones.filter((m) => m.done).length }} /
          {{ track.milestones.length }} 个里程碑</span
        ><strong>{{ progress(track) }}%</strong>
      </div>
      <div class="progress-track">
        <div :style="{ width: `${progress(track)}%` }" />
      </div>
      <div class="milestone-list">
        <button
          v-for="(milestone, index) in track.milestones"
          :key="index"
          :class="['milestone', { done: milestone.done }]"
          :disabled="pending.has(track.id)"
          :aria-pressed="milestone.done"
          @click="toggle(track, index)"
        >
          <span
            ><Check v-if="milestone.done" :size="13" /><Circle
              v-else
              :size="17" /></span
          >{{ milestone.title }}
        </button>
        <p v-if="!track.milestones.length" class="muted">
          编辑路线，添加你的第一个小目标。
        </p>
      </div>
      <div class="route-related">
        <BookOpen :size="15" /><span
          >关联
          {{ entries.filter((e) => e.track_id === track.id).length }}
          份积累</span
        ><button class="text-button" @click="openEntry('note', null, track.id)">
          写笔记<Plus :size="14" />
        </button>
      </div>
      <details
        v-if="entries.some((e) => e.track_id === track.id)"
        class="related-details"
      >
        <summary>查看这条路线的积累</summary>
        <button
          v-for="entry in entries.filter((e) => e.track_id === track.id)"
          :key="entry.id"
          @click="openEntry(entry.kind, entry)"
        >
          <span>{{
            { resource: "资料", note: "笔记", project: "项目" }[entry.kind]
          }}</span>
          {{ entry.title }}<ArrowUpRight :size="13" />
        </button>
      </details>
      <button
        class="button secondary route-session"
        @click="openSession(track.id)"
      >
        <Clock3 :size="16" />记录这次学习
      </button>
    </article>
    <button v-if="!query" class="new-route" @click="openTrack()">
      <span><Plus :size="28" /></span>
      <h3>下一份好奇心</h3>
      <p>把想学的事，变成一条清晰的路。</p>
    </button>
  </div>
  <div v-if="query && !filtered.length" class="empty-state">
    <Route :size="36" />
    <h2>没有找到相关路线</h2>
    <p>换个关键词试试。</p>
  </div>
</template>
