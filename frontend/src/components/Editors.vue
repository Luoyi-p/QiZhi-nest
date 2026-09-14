<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { Archive, ArrowUpRight, Plus, Save, Trash2 } from "lucide-vue-next";
import Modal from "./Modal.vue";
import {
  initialKind,
  initialTrack,
  modal,
  selectedEntry,
  selectedTrack,
} from "../ui";
import {
  entryInput,
  notify,
  saveEntry,
  saveSession,
  saveTrack,
  trackInput,
  tracks,
} from "../store";
import type { EntryInput, TrackInput } from "../types";

const busy = ref(false);
const error = ref("");
const entry = reactive<EntryInput>(
  selectedEntry.value
    ? JSON.parse(JSON.stringify(entryInput(selectedEntry.value)))
    : {
        kind: initialKind.value,
        title: "",
        content: "",
        url: "",
        tags: [],
        track_id: initialTrack.value,
        starred: false,
        archived: false,
        status: "inbox",
      },
);
const track = reactive<TrackInput>(
  selectedTrack.value
    ? JSON.parse(JSON.stringify(trackInput(selectedTrack.value)))
    : {
        title: "",
        description: "",
        color: "green",
        milestones: [{ title: "", done: false }],
        archived: false,
      },
);
const tags = ref(entry.tags.join(", "));
const session = reactive({
  title: "",
  minutes: 25,
  track_id: initialTrack.value,
});
const archiveConfirm = ref(false);
const title = computed(() =>
  modal.value === "entry"
    ? selectedEntry.value
      ? "编辑这份积累"
      : "捕捉新的积累"
    : modal.value === "track"
      ? selectedTrack.value
        ? "我的学习路线"
        : "开启一条学习路线"
      : "记录一次学习",
);
async function submit() {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  try {
    if (modal.value === "entry") {
      entry.tags = tags.value
        .split(/[,，]/)
        .map((t) => t.trim())
        .filter(Boolean);
      await saveEntry({ ...entry }, selectedEntry.value?.id);
    } else if (modal.value === "track") {
      await saveTrack(
        {
          ...track,
          milestones: track.milestones.filter((m) => m.title.trim()),
        },
        selectedTrack.value?.id,
      );
    } else {
      await saveSession({ ...session });
    }
    notify("已保存到你的工作台");
    modal.value = null;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
async function archive() {
  if (busy.value) return;
  if (!archiveConfirm.value) {
    archiveConfirm.value = true;
    return;
  }
  busy.value = true;
  error.value = "";
  try {
    if (selectedEntry.value)
      await saveEntry(
        { ...entryInput(selectedEntry.value), archived: true },
        selectedEntry.value.id,
      );
    else if (selectedTrack.value)
      await saveTrack(
        { ...trackInput(selectedTrack.value), archived: true },
        selectedTrack.value.id,
      );
    notify("已归档，可在数据管理中恢复");
    modal.value = null;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <Modal :title="title" :busy="busy" @close="modal = null">
    <form @submit.prevent="submit">
      <fieldset :disabled="busy">
        <template v-if="modal === 'entry'">
          <label
            >内容类型<select v-model="entry.kind">
              <option value="resource">资料收藏</option>
              <option value="note">学习笔记</option>
              <option value="project">实践项目</option>
            </select></label
          >
          <label
            >标题<input
              v-model="entry.title"
              required
              maxlength="180"
              placeholder="给这份积累起个名字"
          /></label>
          <label v-if="entry.kind !== 'note'"
            >链接 <span class="optional">可选</span>
            <div class="input-with-action">
              <input
                v-model="entry.url"
                type="url"
                maxlength="2000"
                placeholder="https://…"
              /><a
                v-if="/^https?:\/\//i.test(entry.url)"
                :href="entry.url"
                target="_blank"
                rel="noopener noreferrer"
                class="icon-button"
                aria-label="打开链接"
                ><ArrowUpRight :size="18"
              /></a></div
          ></label>
          <label
            >{{ entry.kind === "note" ? "笔记正文" : "描述与想法"
            }}<textarea
              v-model="entry.content"
              :rows="entry.kind === 'note' ? 10 : 5"
              maxlength="50000"
              placeholder="记下关键内容、自己的理解，以及下一步想做的事…"
            />
          </label>
          <div class="form-grid">
            <label
              >关联学习路线<select v-model="entry.track_id">
                <option :value="null">独立积累</option>
                <option v-for="t in tracks" :key="t.id" :value="t.id">
                  {{ t.title }}
                </option>
                <option
                  v-if="
                    entry.track_id &&
                    !tracks.some((t) => t.id === entry.track_id)
                  "
                  :value="entry.track_id"
                >
                  原关联路线（已隐藏或归档）
                </option>
              </select></label
            ><label
              >状态<select v-model="entry.status">
                <option value="inbox">待探索</option>
                <option value="active">进行中</option>
                <option value="done">已完成</option>
              </select></label
            >
          </div>
          <label
            >标签 <span class="optional">用逗号分隔，最多 12 个</span
            ><input v-model="tags" placeholder="Vue, 响应式, 实践"
          /></label>
          <label class="check-label"
            ><input v-model="entry.starred" type="checkbox" />
            置顶到我的常用入口</label
          >
        </template>
        <template v-else-if="modal === 'track'">
          <label
            >路线名称<input
              v-model="track.title"
              required
              maxlength="120"
              placeholder="例如：从零构建一个 Python 服务"
          /></label>
          <label
            >我为什么想学它<textarea
              v-model="track.description"
              rows="3"
              maxlength="1000"
              placeholder="写下这条路线想抵达的地方…"
            />
          </label>
          <label
            >标记颜色<select v-model="track.color">
              <option value="green">松绿</option>
              <option value="blue">雾蓝</option>
              <option value="orange">琥珀</option>
              <option value="purple">鸢紫</option>
            </select></label
          >
          <div class="section-label">
            学习里程碑 <span class="optional">勾选即可记录完成</span>
          </div>
          <div
            v-for="(milestone, index) in track.milestones"
            :key="index"
            class="milestone-edit"
          >
            <input
              v-model="milestone.done"
              type="checkbox"
              :aria-label="`完成第 ${index + 1} 步`"
            /><input
              v-model="milestone.title"
              maxlength="200"
              :aria-label="`第 ${index + 1} 步名称`"
              :placeholder="`第 ${index + 1} 个小目标`"
            /><button
              type="button"
              class="icon-button"
              :aria-label="`移除第 ${index + 1} 步`"
              @click="track.milestones.splice(index, 1)"
            >
              <Trash2 :size="16" />
            </button>
          </div>
          <button
            type="button"
            class="text-button"
            :disabled="track.milestones.length >= 50"
            @click="track.milestones.push({ title: '', done: false })"
          >
            <Plus :size="16" /> 添加一步
          </button>
        </template>
        <template v-else>
          <p class="form-intro">
            不必学很多。为今天真正弄懂的一件事，留下一条记录。
          </p>
          <label
            >这次学了什么<input
              v-model="session.title"
              required
              maxlength="180"
              placeholder="例如：实现并理解了一个 useFetch"
          /></label>
          <div class="form-grid">
            <label
              >投入时间（分钟）<input
                v-model.number="session.minutes"
                required
                type="number"
                min="1"
                max="1440" /></label
            ><label
              >关联路线<select v-model="session.track_id">
                <option :value="null">独立学习</option>
                <option v-for="t in tracks" :key="t.id" :value="t.id">
                  {{ t.title }}
                </option>
              </select></label
            >
          </div>
          <div class="duration-presets">
            <button
              v-for="minutes in [15, 25, 45, 60]"
              :key="minutes"
              type="button"
              :class="['chip', { selected: session.minutes === minutes }]"
              @click="session.minutes = minutes"
            >
              {{ minutes }} 分钟
            </button>
          </div>
        </template>
      </fieldset>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <p v-if="archiveConfirm" class="form-error">
        归档后会从工作区隐藏，已有内容与关联都会保留。再次点击确认。
      </p>
      <div class="modal-footer">
        <button
          v-if="selectedEntry || selectedTrack"
          class="text-button muted"
          type="button"
          :disabled="busy"
          @click="archive"
        >
          <Archive :size="16" />{{ archiveConfirm ? "确认归档" : "归档" }}
        </button>
        <div class="footer-actions">
          <button
            type="button"
            class="button secondary"
            :disabled="busy"
            @click="modal = null"
          >
            取消</button
          ><button type="submit" class="button primary" :disabled="busy">
            <Save :size="16" />{{ busy ? "正在保存…" : "保存" }}
          </button>
        </div>
      </div>
    </form>
  </Modal>
</template>
