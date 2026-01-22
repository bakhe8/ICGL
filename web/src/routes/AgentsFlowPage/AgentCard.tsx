
export type AgentInfo = {
    name: string;
    role: string;
    status: string;
    lastTask: string;
    recommendation?: string;
};

const AgentCard = ({ agent, onDetails }: { agent: AgentInfo; onDetails: () => void }) => (
    <div className="bg-white border rounded shadow-sm p-4 flex flex-col gap-2 min-w-[180px]">
        <div className="font-bold text-blue-700 text-lg">{agent.name}</div>
        <div className="text-xs text-gray-500 mb-1">{agent.role}</div>
        <div className={`text-xs px-2 py-1 rounded-full w-fit ${agent.status === 'active' ? 'bg-green-100 text-green-700' : agent.status === 'waiting' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>{agent.status === 'active' ? 'نشط' : agent.status === 'waiting' ? 'بانتظار' : 'غير محدد'}</div>
        <div className="text-sm text-gray-700">آخر مهمة: {agent.lastTask}</div>
        {agent.recommendation && <div className="text-xs text-blue-500">توصية: {agent.recommendation}</div>}
        <button onClick={onDetails} className="mt-2 bg-blue-50 text-blue-700 px-3 py-1 rounded hover:bg-blue-100 text-xs">تفاصيل أكثر</button>
    </div>
);

export default AgentCard;
