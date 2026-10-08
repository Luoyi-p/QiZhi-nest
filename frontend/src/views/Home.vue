<script setup lang="ts">
import { computed } from "vue";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  Clock3,
  Code2,
  FileText,
  Flag,
  Plus,
  Sparkles,
} from "lucide-vue-next";
import ActivityGrid from "../components/ActivityGrid.vue";
import EntryCard from "../components/EntryCard.vue";
import {
  dayKey,
  entries,
  progress,
  sessions,
  shortDate,
  tracks,
} from "../store";
import { navigate, openEntry, openSession, openTrack } from "../ui";
const currentTrack = computed(
  () => tracks.value.find((t) => progress(t) < 100) || tracks.value[0],
);
const nextStep = computed(
  () => currentTrack.value?.milestones.find((m) => !m.done)?.title,
);
const pinned = computed(() =>
  entries.value.filter((e) => e.starred).slice(0, 3),
);
const recentNotes = computed(() =>
  entries.value
    .filter((e) => e.kind === "note")
    .sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))
    .slice(0, 3),
);
const weekMinutes = computed(() => {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  start.setDate(start.getDate() - 6);
  return sessions.value
    .filter((s) => new Date(s.created_at) >= start)
    .reduce((sum, s) => sum + s.minutes, 0);
});
const todayMinutes = computed(() =>
  sessions.value
    .filter((s) => dayKey(s.created_at) === dayKey(new Date()))
    .reduce((sum, s) => sum + s.minutes, 0),
);
const stats = computed(() => [
  {
    label: "进行中的路线",
    value: tracks.value.filter((t) => progress(t) < 100).length,
    unit: "条",
    icon: Flag,
    note: "按里程碑跟进进度",
    tone: "green",
  },
  {
    label: "已保存内容",
    value: entries.value.length,
    unit: "份",
    icon: BookOpen,
    note: `${entries.value.filter((e) => e.kind === "resource").length} 份资料 · ${entries.value.filter((e) => e.kind === "note").length} 篇笔记`,
    tone: "blue",
  },
  {
    label: "最近 7 天学习",
    value: +(weekMinutes.value / 60).toFixed(1),
    unit: "小时",
    icon: Clock3,
    note: `今天已记录 ${todayMinutes.value} 分钟`,
    tone: "orange",
  },
  {
    label: "未完成项目",
    value: entries.value.filter(
      (e) => e.kind === "project" && e.status !== "done",
    ).length,
    unit: "个",
    icon: Code2,
    note: "包含待探索和进行中的项目",
    tone: "purple",
  },
]);
</script>

<template>
  <section class="page-heading home-heading">
    <div>
      <div class="eyebrow">WORKSPACE</div>
      <h1>我的学习工作台</h1>
      <p>查看学习进度，接着上次的内容继续。</p>
    </div>
    <button class="button secondary" @click="openSession()">
      <Plus :size="17" />记录学习
    </button>
  </section>
  <div class="dashboard-top">
    <section class="continue-card">
      <div class="continue-content">
        <span class="continue-label"
          ><span class="live-dot" /> 当前路线</span
        >
        <h2>{{ currentTrack?.title || "创建第一条学习路线" }}</h2>
        <p>
          {{
            currentTrack?.description ||
            "选择一个学习主题，添加要完成的步骤。"
          }}
        </p>
        <div v-if="currentTrack" class="next-step">
          <span>下一步</span>{{ nextStep || "查看路线，整理后续计划" }}
        </div>
        <button
          class="button lime"
          @click="currentTrack ? openTrack(currentTrack) : openTrack()"
        >
          {{ currentTrack ? "查看路线" : "创建学习路线"
          }}<ArrowUpRight :size="18" />
        </button>
      </div>
      <div class="progress-orbit">
        <svg viewBox="0 0 160 160" aria-hidden="true">
          <circle cx="80" cy="80" r="65" class="orbit-track" />
          <circle
            cx="80"
            cy="80"
            r="65"
            class="orbit-value"
            :stroke-dasharray="`${(currentTrack ? progress(currentTrack) : 0) * 4.084} 408.4`"
          />
        </svg>
        <div class="orbit-label">
          <strong
            >{{ currentTrack ? progress(currentTrack) : 0
            }}<small>%</small></strong
          ><span>路线进度</span>
        </div>
        <span class="orbit-caption">PROGRESS</span>
      </div>
    </section>
    <section class="quick-capture">
      <div class="section-kicker">
        <Sparkles :size="18" />QUICK CAPTURE / 随手记
      </div>
      <h2>收藏资料，<br />记下想法。</h2>
      <p>保存正在看的链接，<br />或写一篇简短的笔记。</p>
      <div class="capture-actions">
        <button @click="openEntry('resource')">
          <BookOpen :size="17" />收藏资料<Plus :size="15" /></button
        ><button @click="openEntry('note')">
          <FileText :size="17" />新建笔记<Plus :size="15" />
        </button>
      </div>
    </section>
  </div>
  <section class="stats-grid">
    <article v-for="stat in stats" :key="stat.label" class="stat-card">
      <div class="stat-label">
        {{ stat.label
        }}<span :class="['stat-icon', stat.tone]"
          ><component :is="stat.icon" :size="18"
        /></span>
      </div>
      <div class="stat-value">
        {{ stat.value }}<span>{{ stat.unit }}</span>
      </div>
      <p>{{ stat.note }}</p>
    </article>
  </section>
  <div class="section-heading">
    <h2>
      置顶内容
      <span class="count">{{ entries.filter((e) => e.starred).length }}</span>
    </h2>
    <button class="text-button" @click="navigate('library')">
      浏览资料库<ArrowRight :size="16" />
    </button>
  </div>
  <div v-if="pinned.length" class="entry-grid home-entries">
    <EntryCard v-for="entry in pinned" :key="entry.id" :entry="entry" />
  </div>
  <button v-else class="empty-inline" @click="openEntry('resource')">
    <Plus :size="20" />收藏常用资料并置顶，让它们成为你的学习入口。
  </button>
  <div class="dashboard-bottom">
    <section class="panel activity-panel">
      <div class="section-heading">
        <h2>学习足迹</h2>
        <button class="text-button" @click="navigate('timeline')">
          时间线<ArrowUpRight :size="16" />
        </button>
      </div>
      <ActivityGrid />
    </section>
    <section class="panel recent-panel">
      <div class="section-heading">
        <h2>最近笔记</h2>
        <button class="text-button" @click="navigate('notes')">
          <span class="sr-only">查看全部笔记</span><ArrowUpRight :size="18" />
        </button>
      </div>
      <button
        v-for="note in recentNotes"
        :key="note.id"
        class="recent-note"
        @click="openEntry('note', note)"
      >
        <span class="note-bullet"><FileText :size="17" /></span
        ><span
          >{{ note.title
          }}<small
            >{{ shortDate(note.updated_at)
            }}<span v-if="note.demo"> · 示例笔记</span></small
          ></span
        ><ArrowUpRight :size="15" />
      </button>
      <p v-if="!recentNotes.length" class="muted">
        还没有笔记，记下今天弄懂的一件小事吧。
      </p>
    </section>
  </div>
  <footer class="page-footer">
    <span><Check :size="14" />数据保存在本机</span
    ><span>可在「数据与设置」中导出备份。</span
    ><span>NEST / PERSONAL SPACE</span>
  </footer>
</template>
