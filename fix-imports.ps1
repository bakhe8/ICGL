# Fix all imports script
Get-ChildItem -Path backend,api -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    
    if ($content -match "from icgl\." -or $content -match "import icgl\.") {
        Write-Host "Fixing: $($_.FullName)"
        
        # Replace imports
        $content = $content -replace 'from icgl\.', 'from backend.'
        $content = $content -replace 'import icgl\.', 'import backend.'
        $content = $content -replace 'from \.\.agents', 'from backend.agents'
        $content = $content -replace 'from \.\.kb', 'from backend.kb'
        $content = $content -replace 'from \.\.governance', 'from backend.governance'
        $content = $content -replace 'from \.\.hdal', 'from backend.hdal'
        $content = $content -replace 'from \.\.llm', 'from backend.llm'
        $content = $content -replace 'from \.\.memory', 'from backend.memory'
        $content = $content -replace 'from \.\.policies', 'from backend.policies'
        $content = $content -replace 'from \.\.sentinel', 'from backend.sentinel'
        $content = $content -replace 'from \.\.chat', 'from backend.chat'
        $content = $content -replace 'from \.\.config', 'from backend.config'
        $content = $content -replace 'from \.\.utils', 'from backend.utils'
        
        Set-Content $_.FullName $content
        Write-Host "  ✓ Fixed"
    }
}
Write-Host "Done!"
