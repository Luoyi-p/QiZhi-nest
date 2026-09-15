<script setup lang="ts">
import { computed } from "vue";
import { BookOpen, Clock3, Code2, FileText, Plus } from "lucide-vue-next";
import ActivityGrid from "../components/ActivityGrid.vue";
import { dayKey, entries, sessions, shortDate, trackName } from "../store";
import { openEntry, openSession, query } from "../ui";
import type { Entry } from "../types";
interface Event {
  id: string;
  title: string;
  date: string;
  kind: string;
  detail: string;
  demo: boolean;
  entry?: Entry;
}
const events = computed(() => {
  const items: Event[] = [
    ...sessions.value.map((s) => ({
      id: s.id,
      title: s.title,
      date: s.created_at,
      kind: "session",
      detail: `${s.minutes} 分钟 · ${trackName(s.track_id)}`,
      demo: s.demo,
    })),
    ...entries.value.map((e) => ({
      id: e.id,
      title: e.title,
      date: e.created_at,
      kind: e.kind,
      detail: `${{ note: "写下笔记", resource: "收藏资料", project: "开启实践" }[e.kind]} · ${trackName(e.track_id)}`,
      demo: e.demo,
      entry: e,
    })),
  ];
  return items
    .filter((e) =>
      `${e.title} ${e.detail}`
        .toLowerCase()
        .includes(query.value.toLowerCase()),
    )
    .sort((a, b) => Date.parse(b.date) - Date.parse(a.date));
});
const groups = computed(() => {
  const result: { day: string; label: string; events: Event[] }[] = [];
  for (const event of events.value) {
    const day = dayKey(event.date);
    let group = result.find((g) => g.day === day);
    if (!group) {
      group = {
        day,
        label: day === dayKey(new Date()) ? "今天" : shortDate(event.date),
        events: [],
      };
      result.push(group);
    }
    group.events.push(event);
  }
  return result;
});
function eventIcon(kind: string) {
  return kind === "session"
    ? Clock3
    : kind === "note"
      ? FileText
      : kind === "project"
        ? Code2
        : BookOpen;
}
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">YOUR DAYS, CONNECTED</div>
      <h1>成长时间线</h1>
      <p>收藏是起点，理解是过程，实践让每一天有迹可循。</p>
    </div>
    <button class="button primary" @click="openSession()">
      <Plus :size="17" />记录学习
    </button>
  </section>
  <section class="panel timeline-activity">
    <div class="section-heading">
      <h2>回头看，已经走了这么远</h2>
      <span class="muted">{{ sessions.length }} 次学习记录</span>
    </div>
    <ActivityGrid />
  </section>
  <div class="timeline">
    <section v-for="group in groups" :key="group.day" class="timeline-group">
      <div class="timeline-date">
        <strong>{{ group.label }}</strong
        ><span>{{ group.day }}</span>
      </div>
      <div class="timeline-events">
        <article
          v-for="event in group.events"
          :key="`${event.kind}-${event.id}`"
          class="timeline-event"
        >
          <div :class="['event-icon', event.kind]">
            <component :is="eventIcon(event.kind)" :size="18" />
          </div>
          <div>
            <button
              v-if="event.entry"
              class="timeline-title"
              @click="openEntry(event.entry.kind, event.entry)"
            >
              {{ event.title }}
            </button>
            <h3 v-else>{{ event.title }}</h3>
            <p>{{ event.detail }}</p>
          </div>
          <span v-if="event.demo" class="demo-tag">示例</span
          ><time>{{
            new Date(event.date).toLocaleTimeString("zh-CN", {
              hour: "2-digit",
              minute: "2-digit",
            })
          }}</time>
        </article>
      </div>
    </section>
  </div>
  <div v-if="!groups.length" class="empty-state">
    <Clock3 :size="36" />
    <h2>{{ query ? "没有匹配的记录" : "时间线等你落下第一笔" }}</h2>
    <p>收藏资料、创建笔记，或记录一次学习，都会出现在这里。</p>
  </div>
</template>
