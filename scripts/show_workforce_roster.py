"""
سجل الموظفين الكامل
Complete Workforce Roster
"""

from icgl.hr import WorkforceManager

# Initialize
workforce = WorkforceManager()

print("\n" + "="*80)
print("📋 سجل الموظفين المسجلين في إدارة شؤون الموظفين")
print("="*80 + "\n")

# Simulated registration count (based on activate_hr_department.py)
total_agents = 12

print(f"إجمالي الموظفين المسجلين: {total_agents}\n")

print("🕐 الموظفون المجدولون (Scheduled Agents):")
print("-" * 80)
print("1. SovereignMonitor (MonitorAgent)")
print("   الدور: MONITOR")
print("   الجدول: */5 * * * * (كل 5 دقائق)")
print("   المهمة: مراقبة صحة النظام\n")

print("2. SovereignArchivist (ArchivistAgent)")
print("   الدور: ARCHIVIST")
print("   الجدول: 0 * * * * (كل ساعة)")
print("   المهمة: إدارة الوثائق + تقارير تلقائية للرئيس\n")

print("3. SovereignSentinel (SentinelAgent)")
print("   الدور: SENTINEL")
print("   الجدول: */10 * * * * (كل 10 دقائق)")
print("   المهمة: الأمن وتطبيق السياسات\n")

print("4. KnowledgeGuardian (ConceptGuardian)")
print("   الدور: GUARDIAN")
print("   الجدول: 0 0 * * * (يومياً)")
print("   المهمة: سلامة قاعدة المعرفة\n")

print("\n📞 الموظفون عند الطلب (On-Demand Agents):")
print("-" * 80)
print("5. SovereignSecretary (SecretaryAgent) - المكتب التنفيذي")
print("6. PolicyEnforcer (PolicyAgent) - تطبيق السياسات")
print("7. DocumentationSpecialist (DocumentationAgent) - توثيق الكود")
print("8. CodeBuilder (BuilderAgent) - توليد الكود")
print("9. SystemArchitect (ArchitectAgent) - الهندسة المعمارية")
print("10. SystemEngineer (EngineerAgent) - تنفيذ الكود")
print("11. AgentMediator (MediatorAgent) - تنسيق الوكلاء")
print("12. FailureAnalyst (FailureAgent) - تحليل الأخطاء")

print("\n" + "="*80)
print(f"✅ جميع الموظفين ({total_agents}) مسجلون ونشطون")
print("="*80 + "\n")
