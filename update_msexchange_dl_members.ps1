# Powershell
#
# Provided with a list of Patterns, this script retrieves the list of Group Members belonging to various AD Groups
# whose name matches with the given pattern. The Group members are then made part of the desired Mail Distribution List.
# Usage: ./update_msexchange_dl_members.ps1 pattern1,pattern2,pattern3
#

param([Parameter(Mandatory=$true)][String[]]$PATTERNS)
$PATTERN_PREFIX=""
$PATTERN_SUFFIX="*"
$DISTRIBUTION_LIST=""
$MEMBERS = New-Object System.Collections.Generic.HashSet[String]
ForEach ($PATTERN in $PATTERNS) {
    $SEARCH_PATTERN="$($PATTERN_PREFIX)$($PATTERN)$($PATTERN_SUFFIX)"
    Write-Output "Fetching the Members of AD Groups with Name matching $SEARCH_PATTERN"
    Get-ADGroup -Filter "Name -like '$SEARCH_PATTERN'" | ForEach-Object -Process {
        Get-ADGroupMember -Identity $_.Name | ForEach-Object -Process {
            $MEMBERS.Add($_.SamAccountName) | Out-Null
        }
    }
}
$MEMBERS_LIST = [Microsoft.ActiveDirectory.Management.ADPrincipal[]]@($MEMBERS)
Write-Output "Adding Members to $DISTRIBUTION_LIST DL"
Add-ADGroupMember -Identity "$DISTRIBUTION_LIST" -Members $MEMBERS_LIST
