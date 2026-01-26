
const IdeaSummary = ({ idea, summary }: { idea: string; summary: string }) => (
    <div className="bg-white border rounded p-4 mb-4">
        <h2 className="font-semibold text-gray-700 mb-2">ملخص الفكرة</h2>
        <div className="text-sm text-gray-700 mb-1">الفكرة المدخلة:</div>
        <div className="bg-gray-50 p-2 rounded text-xs text-gray-600 mb-2">{idea}</div>
        <div className="text-sm text-gray-700 mb-1">ما فهمه النظام:</div>
        <div className="bg-blue-50 p-2 rounded text-xs text-blue-700">{summary}</div>
    </div>
);

export default IdeaSummary;
