# Update fogis-api-client-timmyBird to v0.2.4 to fix API parameter issues

## Description

The application is currently experiencing 500 Server Error responses when trying to fetch team players and officials data. This is due to a parameter name issue in fogis-api-client-timmyBird v0.2.3, where the API client is using `"lagid"` as the parameter name instead of the expected `"matchlagid"`.

Version 0.2.4 of the API client fixes this issue by updating the parameter names to match what the server expects.

## Error Details

```
API request failed: 500 Server Error: Internal Server Error for url: https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetMatchdeltagareListaForMatchlag
```

The error occurs in the following methods:
- `fetch_team_players_json`
- `fetch_team_officials_json`

## Root Cause

In v0.2.3, the API client uses:
```python
payload = {"lagid": team_id_int}
```

But the server expects:
```python
payload = {"matchlagid": team_id_int}
```

This parameter name mismatch causes the 500 Server Error.

## Tasks

1. Update requirements.txt to use fogis-api-client-timmyBird v0.2.4:
   ```diff
   # API client
   -fogis-api-client-timmyBird==0.2.3
   +fogis-api-client-timmyBird==0.2.4
   ```

2. Ensure the virtual environment is using the updated version:
   - Run `pip install -r requirements.txt --upgrade` to update dependencies

3. Verify that the application works correctly with the updated dependency:
   - Test fetching team players and officials data
   - Ensure no 500 Server Errors occur

## Expected Outcome

- The application successfully fetches team players and officials data without 500 Server Errors
- All API requests use the correct parameter names

## Priority

High - This should be addressed immediately as it affects core functionality and prevents the application from working correctly.

## Related Issues/PRs

- This is a follow-up to the previous API client update (see api_client_update_issue.md)
