
import DashboardContainer from '../../../shared/features/admin/Dashboard/DashboardContainer';

const AdminDashboardPage = () => {
    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-1">
                <h1 className="text-3xl font-black text-slate-900 tracking-tight">Governance Dashboard | لوحة التحكم في الحوكمة</h1>
                <p className="text-slate-500 text-sm italic">Operational overview of the Sovereign Mind governance state.</p>
            </div>
            <DashboardContainer />
        </div>
    );
};

export default AdminDashboardPage;
