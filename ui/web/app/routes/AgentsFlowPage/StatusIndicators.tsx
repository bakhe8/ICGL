
const StatusIndicators = ({ status }: { status: string }) => (
    <div className="flex gap-3 items-center mb-4">
        <span className={`px-3 py-1 rounded-full font-bold text-sm ${status === 'success' ? 'bg-green-100 text-green-700' : status === 'warning' ? 'bg-yellow-100 text-yellow-700' : status === 'error' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}`}>{
            status === 'success' ? 'نجاح' : status === 'warning' ? 'تحذير' : status === 'error' ? 'تضارب' : 'غير محدد'
        }</span>
    </div>
);

export default StatusIndicators;
