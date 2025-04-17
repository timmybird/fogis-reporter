# Update fogis-api-client-timmyBird to v0.2.4

## Description

This PR updates the fogis-api-client-timmyBird package from v0.2.3 to v0.2.4 to fix API parameter issues that were causing 500 Server Errors when fetching team players and officials data.

## Changes

- Updated `requirements.txt` to specify fogis-api-client-timmyBird==0.2.4
- Added an Installation section to the README with a note about the minimum required version
- Created an issue description file documenting the problem and solution

## Problem

In v0.2.3, the API client was using `"lagid"` as the parameter name for team ID in the following methods:
- `fetch_team_players_json`
- `fetch_team_officials_json`

However, the server expects `"matchlagid"` instead, which caused 500 Server Errors.

## Solution

Version 0.2.4 of the API client fixes this issue by updating the parameter names to match what the server expects:
```python
# Before (v0.2.3)
payload = {"lagid": team_id_int}

# After (v0.2.4)
payload = {"matchlagid": team_id_int}
```

## Testing

- Verified that the updated package uses the correct parameter names
- Tested fetching team players and officials data with the updated package
- Confirmed that no 500 Server Errors occur with the updated package

## Related Issues

Fixes #[issue_number]
