# SCIM Bulk Import - Complete Administrator Workflow
# This script demonstrates how to select a realm and perform bulk import

# Configuration
$baseUrl = "http://localhost:8000"
$username = "admin"
$password = "admin123"
$csvFile = "sample_users_import.csv"

# Create authentication header
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${password}"))
$headers = @{
    'Authorization' = "Basic $auth"
    'Content-Type' = 'application/json'
}

Write-Host "🚀 SCIM Bulk Import Workflow" -ForegroundColor Green
Write-Host "=" * 50

# Step 1: List available realms
Write-Host "`n1️⃣ Discovering Available Realms..." -ForegroundColor Yellow
try {
    $realms = Invoke-RestMethod -Uri "$baseUrl/admin/realms" -Method Get -Headers $headers
    
    Write-Host "✅ Found $($realms.Count) available realms:" -ForegroundColor Green
    foreach ($realm in $realms) {
        Write-Host "   • $($realm.realm_id) - $($realm.name)" -ForegroundColor Cyan
        Write-Host "     Description: $($realm.description)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed to retrieve realms: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Let administrator select realm
Write-Host "`n2️⃣ Realm Selection..." -ForegroundColor Yellow

if ($realms.Count -eq 1) {
    $selectedRealm = $realms[0]
    Write-Host "🎯 Auto-selecting the only available realm: $($selectedRealm.realm_id)" -ForegroundColor Green
} else {
    Write-Host "Please select a realm for bulk import:"
    for ($i = 0; $i -lt $realms.Count; $i++) {
        Write-Host "   $($i + 1). $($realms[$i].realm_id) - $($realms[$i].name)" -ForegroundColor Cyan
    }
    
    do {
        $selection = Read-Host "Enter realm number (1-$($realms.Count))"
        $selectedIndex = [int]$selection - 1
    } while ($selectedIndex -lt 0 -or $selectedIndex -ge $realms.Count)
    
    $selectedRealm = $realms[$selectedIndex]
    Write-Host "✅ Selected realm: $($selectedRealm.realm_id)" -ForegroundColor Green
}

# Step 3: Verify CSV file exists
Write-Host "`n3️⃣ CSV File Validation..." -ForegroundColor Yellow
if (-not (Test-Path $csvFile)) {
    Write-Host "❌ CSV file '$csvFile' not found!" -ForegroundColor Red
    Write-Host "Available sample files:" -ForegroundColor Yellow
    Get-ChildItem "*.csv" | ForEach-Object { Write-Host "   • $($_.Name)" -ForegroundColor Cyan }
    exit 1
}

$fileSize = (Get-Item $csvFile).Length
Write-Host "✅ CSV file found: $csvFile ($([math]::Round($fileSize/1KB, 2)) KB)" -ForegroundColor Green

# Step 4: Perform dry run first (recommended)
Write-Host "`n4️⃣ Performing Dry Run (Validation Only)..." -ForegroundColor Yellow

$dryRunForm = @{
    file = Get-Item $csvFile
    dry_run = "true"
    skip_duplicates = "true"
    continue_on_error = "true"
}

try {
    $dryRunHeaders = @{
        'Authorization' = "Basic $auth"
    }
    
    $dryRunResponse = Invoke-RestMethod -Uri "$baseUrl/scim/v2/Realms/$($selectedRealm.realm_id)/Users/bulk-import" -Method Post -Form $dryRunForm -Headers $dryRunHeaders
    
    Write-Host "✅ Dry run completed successfully!" -ForegroundColor Green
    Write-Host "   • Total rows: $($dryRunResponse.total_rows)" -ForegroundColor Cyan
    Write-Host "   • Validation errors: $($dryRunResponse.validation_errors)" -ForegroundColor Cyan
    Write-Host "   • Would succeed: $($dryRunResponse.successful_imports)" -ForegroundColor Green
    Write-Host "   • Would fail: $($dryRunResponse.failed_imports)" -ForegroundColor Red
    
    if ($dryRunResponse.validation_errors -gt 0 -or $dryRunResponse.failed_imports -gt 0) {
        Write-Host "`n⚠️ Issues found in dry run:" -ForegroundColor Yellow
        foreach ($result in $dryRunResponse.results) {
            if ($result.status -eq "error") {
                Write-Host "   Row $($result.row_number): $($result.error)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "❌ Dry run failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Ask for confirmation to proceed with actual import
Write-Host "`n5️⃣ Actual Import Confirmation..." -ForegroundColor Yellow
$confirm = Read-Host "Proceed with actual import? (y/N)"

if ($confirm -match '^[Yy]') {
    Write-Host "`n6️⃣ Performing Actual Bulk Import..." -ForegroundColor Yellow
    
    $importForm = @{
        file = Get-Item $csvFile
        dry_run = "false"
        skip_duplicates = "true"
        continue_on_error = "true"
    }
    
    try {
        $importResponse = Invoke-RestMethod -Uri "$baseUrl/scim/v2/Realms/$($selectedRealm.realm_id)/Users/bulk-import" -Method Post -Form $importForm -Headers $dryRunHeaders
        
        Write-Host "🎉 Bulk import completed!" -ForegroundColor Green
        Write-Host "   • Total processed: $($importResponse.total_rows)" -ForegroundColor Cyan
        Write-Host "   • Successfully imported: $($importResponse.successful_imports)" -ForegroundColor Green
        Write-Host "   • Failed: $($importResponse.failed_imports)" -ForegroundColor Red
        Write-Host "   • Processing time: $($importResponse.processing_time_seconds) seconds" -ForegroundColor Cyan
        
        # Show detailed results
        if ($importResponse.results.Count -gt 0) {
            Write-Host "`n📊 Detailed Results:" -ForegroundColor Yellow
            foreach ($result in $importResponse.results) {
                if ($result.status -eq "success") {
                    Write-Host "   ✅ Row $($result.row_number): $($result.username) - $($result.message)" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ Row $($result.row_number): $($result.username) - $($result.error)" -ForegroundColor Red
                }
            }
        }
        
    } catch {
        Write-Host "❌ Import failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Import cancelled by user" -ForegroundColor Yellow
}

Write-Host "`n✅ Bulk import workflow completed!" -ForegroundColor Green
