export interface RouteInfo {
  guard_status: "allowed" | "blocked";
  guard_reason: string | null;
  selected_specialists: string[];
  orchestrator_decision: string | null;
}

export interface Citation {
  source: "jira" | "confluence" | "figma" | "basic";
  id: string;
  title: string;
}

export interface DebugInfo {
  app_specialist_task: string | null;
  steps: string[];
}

export interface ChatResponse {
  answer: string;
  route: RouteInfo;
  citations: Citation[];
  debug: DebugInfo;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}
