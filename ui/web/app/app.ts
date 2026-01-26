document.addEventListener('DOMContentLoaded', () => {
    const testGovernanceButton = document.getElementById('test-governance-btn');
    
    if (testGovernanceButton) {
        testGovernanceButton.addEventListener('click', () => {
            console.log('Test Governance button clicked');
        });
    }
});