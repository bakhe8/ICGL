
const HeaderBar = () => (
    <header className="bg-white border-b px-6 py-3 flex items-center justify-between shadow-sm">
        <div className="font-bold text-lg text-gray-800">ICGL Cockpit</div>
        <div className="flex gap-3">
            <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded hover:bg-blue-200">عودة</button>
            <button className="bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200">إعدادات</button>
        </div>
    </header>
);

export default HeaderBar;
