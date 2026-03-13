import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatResponse } from "@/types/chat";
import { RoutePanel } from "./RoutePanel";
import { CitationsPanel } from "./CitationsPanel";
import { DebugTrace } from "./DebugTrace";

export function ResponseView({ response }: { response: ChatResponse }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
      {/* Answer — wider column */}
      <div className="lg:col-span-3 rounded-xl border border-gray-200 bg-white p-5">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
          Answer
        </h2>
        <div className="prose prose-sm prose-gray max-w-none
          prose-headings:font-semibold prose-headings:text-gray-800
          prose-h3:text-sm prose-h3:uppercase prose-h3:tracking-wide prose-h3:text-indigo-600 prose-h3:mt-5 prose-h3:mb-2
          prose-p:text-gray-700 prose-p:leading-relaxed
          prose-strong:text-gray-900 prose-strong:font-semibold
          prose-code:text-indigo-600 prose-code:bg-indigo-50 prose-code:px-1 prose-code:rounded prose-code:text-xs prose-code:font-mono
          prose-ul:my-1 prose-li:my-0.5 prose-li:text-gray-700
          prose-blockquote:border-l-indigo-200 prose-blockquote:text-gray-500 prose-blockquote:text-xs prose-blockquote:not-italic
          prose-hr:border-gray-100
          prose-em:text-gray-400 prose-em:text-xs prose-em:not-italic">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {response.answer}
          </ReactMarkdown>
        </div>
      </div>

      {/* Pipeline internals — narrower column */}
      <div className="lg:col-span-2 space-y-3">
        <RoutePanel route={response.route} />
        <CitationsPanel citations={response.citations} />
        <DebugTrace debug={response.debug} />
      </div>
    </div>
  );
}
