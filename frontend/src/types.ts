export type Kind = "resource" | "note" | "project";
export type Page =
  | "home"
  | "tracks"
  | "library"
  | "notes"
  | "projects"
  | "timeline"
  | "settings";
export interface Milestone {
  title: string;
  done: boolean;
}
export interface TrackInput {
  title: string;
  description: string;
  color: "green" | "blue" | "orange" | "purple";
  milestones: Milestone[];
  archived: boolean;
}
export interface Track extends TrackInput {
  id: string;
  created_at: string;
  demo: boolean;
}
export interface EntryInput {
  kind: Kind;
  title: string;
  content: string;
  url: string;
  tags: string[];
  track_id: string | null;
  starred: boolean;
  archived: boolean;
  status: "inbox" | "active" | "done";
}
export interface Entry extends EntryInput {
  id: string;
  created_at: string;
  updated_at: string;
  demo: boolean;
}
export interface SessionInput {
  title: string;
  minutes: number;
  track_id: string | null;
}
export interface Session extends SessionInput {
  id: string;
  created_at: string;
  demo: boolean;
}
export interface Workspace {
  version: 1;
  tracks: Track[];
  entries: Entry[];
  sessions: Session[];
}
