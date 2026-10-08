import { computed, ref } from "vue";
import type {
  Entry,
  EntryInput,
  Session,
  SessionInput,
  Track,
  TrackInput,
  Workspace,
} from "./types";

export const workspace = ref<Workspace>({
  version: 1,
  tracks: [],
  entries: [],
  sessions: [],
});
export const loading = ref(true);
export const loadError = ref("");
export const notice = ref("");
export const showDemo = ref(localStorage.getItem("nest-show-demo") !== "false");
let noticeTimer: ReturnType<typeof setTimeout>;
export function notify(message: string) {
  notice.value = message;
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => {
    notice.value = "";
  }, 4500);
}
export function toggleDemo(value: boolean) {
  showDemo.value = value;
  localStorage.setItem("nest-show-demo", String(value));
}
export const entries = computed(() =>
  workspace.value.entries.filter(
    (e) => !e.archived && (showDemo.value || !e.demo),
  ),
);
export const tracks = computed(() =>
  workspace.value.tracks.filter(
    (t) => !t.archived && (showDemo.value || !t.demo),
  ),
);
export const sessions = computed(() =>
  workspace.value.sessions.filter((s) => showDemo.value || !s.demo),
);
export function trackName(id: string | null) {
  return workspace.value.tracks.find((t) => t.id === id)?.title || "未关联路线";
}
export function progress(track: Track) {
  return track.milestones.length
    ? Math.round(
        (track.milestones.filter((m) => m.done).length /
          track.milestones.length) *
          100,
      )
    : 0;
}
export function dayKey(value: string | Date) {
  const date = new Date(value);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
export function shortDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}
export async function request<T>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`/api${path}`, {
      method,
      headers:
        data === undefined ? undefined : { "Content-Type": "application/json" },
      body: data === undefined ? undefined : JSON.stringify(data),
      signal: controller.signal,
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(
        typeof payload.detail === "string"
          ? payload.detail
          : "内容未通过校验，请检查标题、链接和输入长度",
      );
    }
    return (await response.json()) as T;
  } catch (error) {
    if (
      error instanceof TypeError ||
      (error instanceof DOMException && error.name === "AbortError")
    )
      throw new Error("连接不到服务，请确认 Python 后端已启动，然后重试。");
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
export async function loadWorkspace() {
  loading.value = true;
  loadError.value = "";
  try {
    workspace.value = await request<Workspace>("/workspace");
  } catch (error) {
    loadError.value = (error as Error).message;
  } finally {
    loading.value = false;
  }
}
export function entryInput(entry: Entry): EntryInput {
  const {
    kind,
    title,
    content,
    url,
    tags,
    track_id,
    starred,
    archived,
    status,
  } = entry;
  return {
    kind,
    title,
    content,
    url,
    tags,
    track_id,
    starred,
    archived,
    status,
  };
}
export function trackInput(track: Track): TrackInput {
  const { title, description, color, milestones, archived } = track;
  return { title, description, color, milestones, archived };
}
export async function saveEntry(data: EntryInput, id?: string) {
  const record = await request<Entry>(
    id ? `/entries/${encodeURIComponent(id)}` : "/entries",
    id ? "PUT" : "POST",
    data,
  );
  workspace.value.entries = [
    record,
    ...workspace.value.entries.filter((e) => e.id !== record.id),
  ];
  return record;
}
export async function saveTrack(data: TrackInput, id?: string) {
  const record = await request<Track>(
    id ? `/tracks/${encodeURIComponent(id)}` : "/tracks",
    id ? "PUT" : "POST",
    data,
  );
  workspace.value.tracks = workspace.value.tracks.some((t) => t.id === record.id)
    ? workspace.value.tracks.map((t) => (t.id === record.id ? record : t))
    : [record, ...workspace.value.tracks];
  return record;
}
export async function saveSession(data: SessionInput) {
  const record = await request<Session>("/sessions", "POST", data);
  workspace.value.sessions.unshift(record);
  return record;
}
const starring = new Set<string>();
export async function toggleStar(entry: Entry) {
  if (starring.has(entry.id)) return;
  starring.add(entry.id);
  try {
    await saveEntry(
      { ...entryInput(entry), starred: !entry.starred },
      entry.id,
    );
  } catch (error) {
    notify((error as Error).message);
  } finally {
    starring.delete(entry.id);
  }
}
