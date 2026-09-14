<script setup lang="ts">
import { computed, ref } from "vue";
import {
  ArchiveRestore,
  Check,
  Database,
  Download,
  FolderArchive,
  HardDrive,
  Upload,
} from "lucide-vue-next";
import {
  entryInput,
  loadWorkspace,
  notify,
  request,
  saveEntry,
  saveTrack,
  showDemo,
  toggleDemo,
  trackInput,
  workspace,
} from "../store";
const busy = ref(false);
const fileInput = ref<HTMLInputElement>();
const archiveCount = computed(
  () =>
    workspace.value.entries.filter((e) => e.archived).length +
    workspace.value.tracks.filter((t) => t.archived).length,
);
async function exportData() {
  busy.value = true;
  try {
    const data = await request("/export");
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `nest-backup-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify("备份已导出，包含全部个人内容与归档记录");
  } catch (error) {
    notify((error as Error).message);
  } finally {
    busy.value = false;
  }
}
async function importData(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  busy.value = true;
  try {
    if (file.size > 10 * 1024 * 1024) throw new Error("备份文件不能超过 10 MB");
    let data: unknown;
    try {
      data = JSON.parse(await file.text());
    } catch {
      throw new Error("无法读取 JSON，请选择栖知导出的备份文件");
    }
    const result = await request<{ imported: number }>("/import", "POST", data);
    await loadWorkspace();
    notify(`已导入 ${result.imported} 条新记录，相同 ID 的本地内容保持不变`);
  } catch (error) {
    notify((error as Error).message);
  } finally {
    busy.value = false;
    input.value = "";
  }
}
async function restore(id: string, kind: "entry" | "track") {
  busy.value = true;
  try {
    if (kind === "entry") {
      const item = workspace.value.entries.find((e) => e.id === id)!;
      await saveEntry({ ...entryInput(item), archived: false }, id);
    } else {
      const item = workspace.value.tracks.find((t) => t.id === id)!;
      await saveTrack({ ...trackInput(item), archived: false }, id);
    }
    notify("已恢复到工作区");
  } catch (error) {
    notify((error as Error).message);
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="page-heading">
    <div>
      <div class="eyebrow">YOURS, BY DESIGN</div>
      <h1>我的数据</h1>
      <p>学习留下的东西，应当一直掌握在自己手里。</p>
    </div>
  </section>
  <div class="settings-grid">
    <section class="panel settings-panel">
      <span class="settings-icon"><HardDrive :size="26" /></span>
      <h2>本地优先，安心积累</h2>
      <p>
        资料、笔记、路线和学习记录保存在这台电脑的 SQLite
        数据库里。应用不会自动把内容同步到第三方。
      </p>
      <div class="storage-summary">
        <span
          ><strong>{{ workspace.entries.length }}</strong> 份积累</span
        ><span
          ><strong>{{ workspace.tracks.length }}</strong> 条路线</span
        ><span
          ><strong>{{ workspace.sessions.length }}</strong> 次记录</span
        >
      </div>
      <div class="local-status"><Check :size="16" />数据服务已连接</div>
    </section>
    <section class="panel settings-panel">
      <span class="settings-icon blue"><Database :size="26" /></span>
      <h2>让数据跟着你走</h2>
      <p>
        导出 JSON
        保存完整备份；在另一台电脑导入，就能继续积累。导入采用合并方式，相同 ID
        的记录不会覆盖本地版本。
      </p>
      <div class="backup-actions">
        <button class="button primary" :disabled="busy" @click="exportData">
          <Download :size="17" />导出备份</button
        ><button
          class="button secondary"
          :disabled="busy"
          @click="fileInput?.click()"
        >
          <Upload :size="17" />导入备份</button
        ><input
          ref="fileInput"
          type="file"
          accept=".json,application/json"
          class="sr-only"
          aria-label="选择备份文件"
          @change="importData"
        />
      </div>
      <span class="muted">支持栖知 JSON 备份，最大 10 MB。</span>
    </section>
  </div>
  <section class="panel demo-setting">
    <div>
      <h2>示例内容</h2>
      <p>
        首次使用附带一组学习示例。关闭后，工作区和统计只展示你的真实积累；示例数据仍会保留在备份中。
      </p>
    </div>
    <label class="toggle"
      ><input
        type="checkbox"
        :checked="showDemo"
        @change="toggleDemo(($event.target as HTMLInputElement).checked)"
      /><span></span><span class="sr-only">显示示例内容</span></label
    >
  </section>
  <section class="panel archive-panel">
    <div class="section-heading">
      <h2>
        <FolderArchive :size="20" />归档空间
        <span class="count">{{ archiveCount }}</span>
      </h2>
    </div>
    <p class="muted">
      归档只是暂时收起。恢复之后，它们会重新出现在原来的位置。
    </p>
    <div v-if="!archiveCount" class="archive-empty">这里还没有归档内容。</div>
    <div
      v-for="entry in workspace.entries.filter((e) => e.archived)"
      :key="entry.id"
      class="archive-row"
    >
      <span
        >{{ entry.title }}
        <small
          >·
          {{
            { note: "笔记", resource: "资料", project: "项目" }[entry.kind]
          }}</small
        ></span
      ><button
        class="text-button"
        :disabled="busy"
        @click="restore(entry.id, 'entry')"
      >
        <ArchiveRestore :size="16" />恢复
      </button>
    </div>
    <div
      v-for="track in workspace.tracks.filter((t) => t.archived)"
      :key="track.id"
      class="archive-row"
    >
      <span>{{ track.title }} <small>· 学习路线</small></span
      ><button
        class="text-button"
        :disabled="busy"
        @click="restore(track.id, 'track')"
      >
        <ArchiveRestore :size="16" />恢复
      </button>
    </div>
  </section>
  <p class="settings-footnote">
    当前为单人本地版本，尚未加入登录与跨设备同步。个人备份与数据库已配置为不随
    Git 提交。
  </p>
</template>
