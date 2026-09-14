import { ref } from "vue";
import type { Entry, Kind, Page, Track } from "./types";

const pages: Page[] = [
  "home",
  "tracks",
  "library",
  "notes",
  "projects",
  "timeline",
  "settings",
];
function hashPage(): Page {
  const value = location.hash.slice(1) as Page;
  return pages.includes(value) ? value : "home";
}
export const page = ref<Page>(hashPage());
export const query = ref("");
export const trackFilter = ref("");
export const modal = ref<"entry" | "track" | "session" | null>(null);
export const selectedEntry = ref<Entry | null>(null);
export const selectedTrack = ref<Track | null>(null);
export const initialKind = ref<Kind>("resource");
export const initialTrack = ref<string | null>(null);
window.addEventListener("hashchange", () => {
  page.value = hashPage();
  query.value = "";
  trackFilter.value = "";
});
export function navigate(target: Page) {
  page.value = target;
  location.hash = target;
  query.value = "";
  trackFilter.value = "";
}
export function openEntry(
  kind: Kind = "resource",
  entry: Entry | null = null,
  trackId: string | null = null,
) {
  selectedTrack.value = null;
  initialKind.value = kind;
  selectedEntry.value = entry;
  initialTrack.value = trackId;
  modal.value = "entry";
}
export function openTrack(track: Track | null = null) {
  selectedEntry.value = null;
  selectedTrack.value = track;
  modal.value = "track";
}
export function openSession(trackId: string | null = null) {
  selectedEntry.value = null;
  selectedTrack.value = null;
  initialTrack.value = trackId;
  modal.value = "session";
}
