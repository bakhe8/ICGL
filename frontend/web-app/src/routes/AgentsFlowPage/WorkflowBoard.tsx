
const WorkflowBoard = ({ stages }: { stages: Array<{ name: string; agent: string; status: string }> }) => (
    <div className="bg-gray-50 rounded p-4 mb-6">
        <h2 className="font-semibold text-gray-700 mb-2">تدفق العمل</h2>
        <div className="flex gap-4 items-center">
            {stages.map((stage, idx) => (
                <div key={idx} className="flex flex-col items-center">
                    <div className={`rounded-full px-4 py-2 bg-blue-50 text-blue-700 font-bold border ${stage.status === 'completed' ? 'border-green-400' : 'border-gray-300'}`}>{stage.name}</div>
                    <div className="text-xs text-gray-500 mt-1">{stage.agent}</div>
                    {idx < stages.length - 1 && <span className="mx-2 text-gray-400">→</span>}
                </div>
            ))}
        </div>
    </div>
);

export default WorkflowBoard;
