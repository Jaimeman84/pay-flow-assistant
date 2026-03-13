import { Citation } from "@/types/chat";

const SOURCE_STYLES: Record<string, { badge: string; icon: string }> = {
  jira: {
    badge: "bg-blue-50 border-blue-200 text-blue-800",
    icon: "🔵",
  },
  confluence: {
    badge: "bg-purple-50 border-purple-200 text-purple-800",
    icon: "📄",
  },
  figma: {
    badge: "bg-orange-50 border-orange-200 text-orange-800",
    icon: "🎨",
  },
  basic: {
    badge: "bg-gray-50 border-gray-200 text-gray-700",
    icon: "📚",
  },
};

export function CitationsPanel({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Citations
        </h2>
        <p className="text-xs text-gray-400 italic">No citations for this response.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Citations ({citations.length})
      </h2>
      <div className="space-y-2">
        {citations.map((c) => {
          const style = SOURCE_STYLES[c.source] ?? SOURCE_STYLES.basic;
          return (
            <div
              key={`${c.source}-${c.id}`}
              className={`flex items-start gap-2.5 rounded-lg border p-2.5 ${style.badge}`}
            >
              <span className="text-sm leading-none mt-0.5">{style.icon}</span>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold">{c.id}</span>
                  <span className="capitalize text-xs opacity-70">{c.source}</span>
                </div>
                <p className="text-xs mt-0.5 leading-snug">{c.title}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
