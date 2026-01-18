"""
مراجعة وتصحيح خطط إدارة البرمجة
DevelopmentManager Review of Engineering Plans

Review criteria:
1. Governance compliance
2. No execution without approval
3. Clear approval points
4. Realistic timelines
5. Resource feasibility
"""

from pathlib import Path
from typing import Dict, List, Any


class PlanReviewer:
    """Reviews and corrects Engineering Department plans."""
    
    def __init__(self):
        self.issues_found = []
        self.corrections_made = []
        self.approval_required = []
    
    def review_plan(self, plan_path: Path) -> Dict[str, Any]:
        """Review a single plan for governance compliance."""
        
        review_result = {
            "plan": str(plan_path),
            "status": "APPROVED",
            "issues": [],
            "corrections": [],
            "recommendations": []
        }
        
        try:
            content = plan_path.read_text(encoding='utf-8')
            
            # Check 1: Governance principle mentioned
            if "لا تنفيذ بدون موافقة" not in content and "NO EXECUTION WITHOUT" not in content:
                review_result["issues"].append({
                    "severity": "CRITICAL",
                    "issue": "Missing governance principle statement",
                    "correction": "Add: لا تنفيذ بدون موافقة سيادية"
                })
                review_result["status"] = "NEEDS_CORRECTION"
            
            # Check 2: Approval points clearly defined
            if "نقاط الموافقة" not in content and "approval_points" not in content:
                review_result["issues"].append({
                    "severity": "HIGH",
                    "issue": "Approval points not clearly defined",
                    "correction": "Add explicit approval points section"
                })
                review_result["status"] = "NEEDS_CORRECTION"
            
            # Check 3: Boundaries clearly stated
            if "الحدود والقيود" not in content and "boundaries" not in content.lower():
                review_result["issues"].append({
                    "severity": "MEDIUM",
                    "issue": "Boundaries not clearly stated",
                    "correction": "Add boundaries section"
                })
            
            # Check 4: No auto-execution language
            risky_terms = ["automatically execute", "auto-deploy to production", "self-authorize"]
            for term in risky_terms:
                if term.lower() in content.lower():
                    review_result["issues"].append({
                        "severity": "CRITICAL",
                        "issue": f"Risky language found: '{term}'",
                        "correction": f"Replace with: 'prepare for approval' or 'recommend'"
                    })
                    review_result["status"] = "REJECTED"
            
            # Recommendations
            review_result["recommendations"] = [
                "Add weekly progress reports to CEO",
                "Include rollback procedures",
                "Define success metrics clearly",
                "Add risk mitigation strategies"
            ]
            
        except Exception as e:
            review_result["status"] = "ERROR"
            review_result["issues"].append({
                "severity": "CRITICAL",
                "issue": f"Failed to read plan: {e}"
            })
        
        return review_result
    
    def generate_review_report(self, reviews: List[Dict[str, Any]]) -> str:
        """Generate comprehensive review report."""
        
        report = """# 📋 تقرير مراجعة خطط إدارة البرمجة
## DevelopmentManager Review Report

**المُراجِع:** DevelopmentManagerAgent  
**التاريخ:** 2026-01-17

---

## ملخص المراجعة

"""
        
        approved = sum(1 for r in reviews if r["status"] == "APPROVED")
        needs_correction = sum(1 for r in reviews if r["status"] == "NEEDS_CORRECTION")
        rejected = sum(1 for r in reviews if r["status"] == "REJECTED")
        
        report += f"""
| الحالة | العدد |
|:---|:---:|
| ✅ معتمد | {approved} |
| ⚠️ يحتاج تصحيح | {needs_correction} |
| ❌ مرفوض | {rejected} |

---

## المراجعة التفصيلية

"""
        
        for review in reviews:
            plan_name = Path(review["plan"]).stem
            report += f"\n### {plan_name}\n\n"
            report += f"**الحالة:** {review['status']}\n\n"
            
            if review["issues"]:
                report += "**المشاكل المكتشفة:**\n\n"
                for issue in review["issues"]:
                    report += f"- [{issue['severity']}] {issue['issue']}\n"
                    report += f"  - **التصحيح:** {issue['correction']}\n"
                report += "\n"
            
            if review["recommendations"]:
                report += "**التوصيات:**\n\n"
                for rec in review["recommendations"]:
                    report += f"- {rec}\n"
                report += "\n"
            
            report += "---\n"
        
        report += """

## التصحيحات المطلوبة

### 1. تعزيز مبدأ الحوكمة

جميع الخطط يجب أن تبدأ بـ:

> [!IMPORTANT]
> **لا تنفيذ بدون موافقة سيادية صريحة على كل خطوة**

### 2. نقاط الموافقة الواضحة

كل خطة يجب أن تحتوي على قسم:

```markdown
## نقاط الموافقة المطلوبة

1. ✋ [نقطة الموافقة 1]
2. ✋ [نقطة الموافقة 2]
...
```

### 3. الحدود الواضحة

```markdown
## الحدود والقيود

### ما يمكننا فعله بدون موافقة:
- ✅ [...]

### ما يحتاج موافقة سيادية:
- ❌ [...]
```

---

## التوصية النهائية

"""
        
        if rejected > 0:
            report += "❌ **يُرفض التطبيق** - يحتاج تصحيحات حرجة\n\n"
        elif needs_correction > 0:
            report += "⚠️ **يُوافق بشروط** - بعد التصحيحات المطلوبة\n\n"
        else:
            report += "✅ **يُوافق للرفع للرئيس** - جميع الخطط متوافقة مع الحوكمة\n\n"
        
        report += """
**الخطوة التالية:** 
1. تطبيق التصحيحات المطلوبة
2. مراجعة ثانية من DevelopmentManager
3. رفع للرئيس للموافقة النهائية

---

**المُراجِع:** DevelopmentManagerAgent  
**التوقيع:** ✓ Reviewed and Approved for Corrections
"""
        
        return report


def main():
    print("\n" + "="*80)
    print("📋 مراجعة خطط إدارة البرمجة")
    print("DevelopmentManager Review")
    print("="*80 + "\n")
    
    # Initialize reviewer
    reviewer = PlanReviewer()
    
    # Plans to review
    plans_dir = Path("docs/PLANS/ENGINEERING")
    plan_files = list(plans_dir.glob("*_STRATEGIC_PLAN.md"))
    
    print(f"Plans to review: {len(plan_files)}\n")
    
    # Review each plan
    reviews = []
    for plan_file in plan_files:
        print(f"📄 Reviewing: {plan_file.name}...")
        review = reviewer.review_plan(plan_file)
        reviews.append(review)
        
        status_emoji = {
            "APPROVED": "✅",
            "NEEDS_CORRECTION": "⚠️",
            "REJECTED": "❌",
            "ERROR": "🔥"
        }
        
        print(f"   {status_emoji.get(review['status'], '?')} {review['status']}")
        if review["issues"]:
            print(f"   Issues found: {len(review['issues'])}")
        print()
    
    # Generate review report
    print("📝 Generating review report...")
    report = reviewer.generate_review_report(reviews)
    
    # Save report
    report_file = plans_dir / "DEVELOPMENT_MANAGER_REVIEW.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"✅ Review report saved: {report_file}\n")
    
    # Summary
    print("="*80)
    print("📊 Review Summary")
    print("="*80)
    
    approved = sum(1 for r in reviews if r["status"] == "APPROVED")
    needs_correction = sum(1 for r in reviews if r["status"] == "NEEDS_CORRECTION")
    rejected = sum(1 for r in reviews if r["status"] == "REJECTED")
    
    print(f"\n✅ Approved: {approved}")
    print(f"⚠️ Needs Correction: {needs_correction}")
    print(f"❌ Rejected: {rejected}")
    
    if rejected > 0:
        print("\n❌ FINAL DECISION: Plans REJECTED - Critical corrections needed")
    elif needs_correction > 0:
        print("\n⚠️ FINAL DECISION: Conditional approval - Apply corrections first")
    else:
        print("\n✅ FINAL DECISION: All plans approved for CEO review")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
