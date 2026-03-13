import { RouteInfo } from "@/types/chat";

const SPECIALIST_COLORS: Record<string, string> = {
  jira: "bg-blue-100 text-blue-800 border-blue-200",
  confluence: "bg-purple-100 text-purple-800 border-purple-200",
  figma: "bg-orange-100 text-orange-800 border-orange-200",
  basic: "bg-gray-100 text-gray-700 border-gray-200",
};

const DECISION_LABELS: Record<string, string> = {
  jira_blocker_query: "Jira — Blocker Query",
  jira_ticket_query: "Jira — Ticket Query",
  confluence_docs_query: "Confluence — Docs Query",
  confluence_release_notes_query: "Confluence — Release Notes",
  figma_screen_query: "Figma — Screen Query",
  figma_component_query: "Figma — Component Query",
  cross_source_comparison: "Cross-Source Comparison",
  unknown_topic_fallback: "Unknown Topic Fallback",
};

export function RoutePanel({ route }: { route: RouteInfo }) {
  const isBlocked = route.guard_status === "blocked";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-4">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Pipeline Route
      </h2>

      {/* Guard status */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 w-20 shrink-0">Guard</span>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium border ${
            isBlocked
              ? "bg-red-100 text-red-700 border-red-200"
              : "bg-green-100 text-green-700 border-green-200"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              isBlocked ? "bg-red-500" : "bg-green-500"
            }`}
          />
          {isBlocked ? "blocked" : "allowed"}
        </span>
        {route.guard_reason && (
          <span className="text-xs text-red-500 font-mono">
            ({route.guard_reason})
          </span>
        )}
      </div>

      {/* Specialists */}
      <div className="flex items-start gap-2">
        <span className="text-xs text-gray-500 w-20 shrink-0 pt-0.5">
          Specialists
        </span>
        <div className="flex flex-wrap gap-1.5">
          {route.selected_specialists.length === 0 ? (
            <span className="text-xs text-gray-400 italic">none</span>
          ) : (
            route.selected_specialists.map((s) => (
              <span
                key={s}
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium border capitalize ${
                  SPECIALIST_COLORS[s] ?? "bg-gray-100 text-gray-600 border-gray-200"
                }`}
              >
                {s}
              </span>
            ))
          )}
        </div>
      </div>

      {/* Orchestrator decision */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 w-20 shrink-0">Decision</span>
        {route.orchestrator_decision ? (
          <span className="rounded-full bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
            {DECISION_LABELS[route.orchestrator_decision] ??
              route.orchestrator_decision}
          </span>
        ) : (
          <span className="text-xs text-gray-400 italic">none</span>
        )}
      </div>
    </div>
  );
}
