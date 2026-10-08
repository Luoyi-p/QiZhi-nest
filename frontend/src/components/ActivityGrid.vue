<script setup lang="ts">
import { computed } from "vue";
import { dayKey, sessions } from "../store";
const days = computed(() => {
  const totals = new Map<string, number>();
  for (const session of sessions.value) {
    const key = dayKey(session.created_at);
    totals.set(key, (totals.get(key) || 0) + session.minutes);
  }
  const today = new Date();
  today.setHours(12, 0, 0, 0);
  return Array.from({ length: 105 }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - 104 + index);
    const key = dayKey(date);
    const minutes = totals.get(key) || 0;
    return {
      key,
      minutes,
      level:
        minutes === 0
          ? 0
          : minutes < 30
            ? 1
            : minutes < 45
              ? 2
              : minutes < 60
                ? 3
                : 4,
    };
  });
});
const activeDays = computed(
  () => days.value.filter((d) => d.minutes > 0).length,
);
</script>

<template>
  <div class="activity-label">
    <span
      >最近 105 天，<strong>{{ activeDays }}</strong> 天有学习记录</span
    ><span class="muted">按每日学习分钟数统计</span>
  </div>
  <div
    class="heatmap"
    role="img"
    :aria-label="`最近 105 天学习活跃图，${activeDays} 天有学习记录`"
  >
    <div
      v-for="day in days"
      :key="day.key"
      :class="['heat-cell', `heat-${day.level}`]"
      :title="`${day.key} · ${day.minutes} 分钟`"
    />
  </div>
  <div class="heatmap-legend">
    <span>{{ days[0]?.key.slice(5).replace("-", "/") }}</span>
    <div>
      <span>少</span
      ><i
        v-for="level in [0, 1, 2, 3, 4]"
        :key="level"
        :class="['heat-cell', `heat-${level}`]"
      /><span>多</span>
    </div>
    <span>今天</span>
  </div>
</template>
