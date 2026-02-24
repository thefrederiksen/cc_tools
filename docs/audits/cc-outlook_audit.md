# cc_outlook API Audit Report

**Date:** 2026-02-17
**Auditor:** Claude Opus 4.5
**Tool Version:** 0.1.0
**Underlying API:** Microsoft Graph API (via O365 Python library)

---

## Executive Summary

cc_outlook provides a solid foundation for Outlook email and calendar operations using the O365 Python library, which wraps the Microsoft Graph API. The implementation covers basic email operations (list, read, send, search, delete, move) and calendar functionality (list events, create events). However, the Microsoft Graph API offers significantly more capabilities that could enhance LLM-driven workflows.

**Current Coverage:** ~35% of available API capabilities
**Quick Wins Identified:** 18 high-value features
**Documentation Quality:** Good (README is clear, has troubleshooting)

---

## Current Implementation Analysis

### Implemented Features

#### Email Operations
| Feature | CLI Command | API Method | Status |
|---------|-------------|------------|--------|
| List messages | `list` | `list_messages()` | OK |
| Read message | `read <id>` | `get_message()` | OK |
| Send email | `send` | `send_message()` | OK |
| Create draft | (internal) | `create_draft()` | OK |
| Delete message | `delete` | `delete_message()` | OK |
| Move message | `move` | `move_message()` | OK |
| Mark read/unread | `mark-read` | `mark_as_read()` | OK |
| Search messages | `search` | `search_messages()` | OK |
| List folders | `folders` | `list_folders()` | OK |
| Create folder | (internal) | `create_folder()` | OK |

#### Calendar Operations
| Feature | CLI Command | API Method | Status |
|---------|-------------|------------|--------|
| List calendars | `calendar list` | `list_calendars()` | OK |
| Get events | `calendar events` | `get_events()` | OK |
| Create event | `calendar create` | `create_event()` | OK |

#### Account Management
| Feature | CLI Command | Status |
|---------|-------------|--------|
| Add account | `accounts add` | OK |
| List accounts | `accounts list` | OK |
| Set default | `accounts default` | OK |
| Delete account | `accounts delete` | OK |
| Auth status | `auth status` | OK |
| Force reauth | `auth --force` | OK |

---

## Gap Analysis: Unexposed API Capabilities

### HIGH PRIORITY - Quick Wins (High LLM Value, Low Effort)

#### 1. Reply/Reply-All/Forward Messages
**API:** `POST /messages/{id}/reply`, `POST /messages/{id}/replyAll`, `POST /messages/{id}/forward`
**O365:** `message.reply()`, `message.reply_all()`, `message.forward()`
**Value:** Essential for conversational email workflows
**Effort:** Low - O365 library already supports this
**Recommendation:** Add `reply`, `reply-all`, `forward` CLI commands

#### 2. Message Categories/Labels
**API Property:** `categories` on message resource
**Value:** Categorize/tag emails for organization
**Effort:** Low - Just expose existing property
**Recommendation:** Add `--category` flag to send/list, add `categorize` command

#### 3. Message Importance/Priority
**API Property:** `importance` (low, normal, high)
**Current:** Exposed in API wrapper but not CLI
**Value:** Filter/set email priority
**Effort:** Very Low
**Recommendation:** Add `--importance` flag to send command

#### 4. Flag Messages (Follow-up)
**API Property:** `flag` with followupFlag type
**Value:** Mark emails for follow-up with due dates
**Effort:** Low
**Recommendation:** Add `flag` command with due date support

#### 5. Conversation Threading
**API Property:** `conversationId`, `conversationIndex`
**Value:** Group emails by conversation
**Effort:** Low
**Recommendation:** Add `--conversation` flag to list, add `conversation` command

#### 6. Internet Message Headers
**API Property:** `internetMessageHeaders`
**Value:** Access raw email headers, useful for debugging/analysis
**Effort:** Low - requires `$select` query
**Recommendation:** Add `--headers` flag to `read` command

#### 7. Get User Profile
**API:** `GET /me`
**Current:** Minimal `get_profile()` exists
**Missing:** Full user profile data
**Recommendation:** Enhance `profile` command with full user data

#### 8. Mailbox Settings - Automatic Replies (Out of Office)
**API:** `GET/PATCH /me/mailboxSettings/automaticRepliesSetting`
**Value:** Set/get out-of-office messages
**Effort:** Medium
**Recommendation:** Add `settings auto-reply` subcommands

#### 9. Attachments - List/Download
**API:** `GET /messages/{id}/attachments`
**Current:** `has_attachments` flag shown, but no download
**Value:** Critical for document workflows
**Effort:** Medium
**Recommendation:** Add `attachments list <id>`, `attachments download <id> <attachment_id>`

#### 10. Calendar View (Date Range)
**API:** `GET /me/calendarView?startDateTime=X&endDateTime=Y`
**Value:** More intuitive date range queries
**Current:** Uses `days_ahead` parameter
**Recommendation:** Add `--from` and `--to` date parameters

#### 11. Delete/Update Calendar Events
**API:** `DELETE /events/{id}`, `PATCH /events/{id}`
**Current:** Can create but not modify/delete events
**Value:** Complete calendar management
**Effort:** Low
**Recommendation:** Add `calendar delete <id>`, `calendar update <id>`

#### 12. Online Meeting Info
**API Property:** `isOnlineMeeting`, `onlineMeeting`, `onlineMeetingProvider`
**Value:** Teams meeting links, join URLs
**Current:** Not exposed in event output
**Effort:** Very Low
**Recommendation:** Include online meeting info in event display

#### 13. Event Attendee Response Status
**API Property:** `responseStatus` on attendees
**Value:** See who accepted/declined meetings
**Effort:** Very Low
**Recommendation:** Show attendee response status in event display

#### 14. Accept/Decline/Tentative Calendar Events
**API:** `POST /events/{id}/accept`, `/decline`, `/tentativelyAccept`
**Value:** Respond to meeting invitations
**Effort:** Low
**Recommendation:** Add `calendar respond <id> --accept|--decline|--tentative`

#### 15. Free/Busy Schedule
**API:** `POST /me/calendar/getSchedule`
**Value:** Check availability before scheduling
**Effort:** Medium
**Recommendation:** Add `calendar availability` command

#### 16. Working Hours
**API:** `GET /me/mailboxSettings/workingHours`
**Value:** Know user's working schedule
**Effort:** Low
**Recommendation:** Add `settings working-hours` command

#### 17. Delta Queries (Sync Changes)
**API:** `GET /me/messages/delta`, `GET /me/events/delta`
**Value:** Efficient sync - only get changed items
**Effort:** Medium-High
**Recommendation:** Add `sync` command for incremental updates

#### 18. Batch Requests
**API:** `POST /$batch`
**Value:** Multiple operations in single request
**Effort:** Medium
**Recommendation:** Consider for bulk operations

---

### MEDIUM PRIORITY - Extended Features

#### Message Operations
| Feature | API Endpoint | Notes |
|---------|-------------|-------|
| Copy message | `POST /messages/{id}/copy` | Copy to folder |
| Get MIME content | `GET /messages/{id}/$value` | Raw message |
| Send with MIME | `POST /me/sendMail` with MIME | Advanced sending |
| Permanently delete | `POST /messages/{id}/permanentDelete` | Skip trash |
| Focused Inbox | `inferenceClassification` | Priority inbox |
| Message rules | `/mailFolders/inbox/messageRules` | Auto-sorting |

#### Calendar Operations
| Feature | API Endpoint | Notes |
|---------|-------------|-------|
| Recurring events | `recurrence` property | Series master |
| Event instances | `GET /events/{id}/instances` | Expand recurring |
| Cancel meeting | `POST /events/{id}/cancel` | Organizer action |
| Propose new time | `POST /events/{id}/tentativelyAccept` with body | Attendee action |
| Snooze/dismiss reminder | `/events/{id}/snoozeReminder` | Reminder mgmt |
| Calendar groups | `/calendarGroups` | Organize calendars |

#### Contacts (Not Implemented)
| Feature | API Endpoint | Notes |
|---------|-------------|-------|
| List contacts | `GET /me/contacts` | Address book |
| Search contacts | `GET /me/contacts?$search=X` | Find people |
| Contact folders | `GET /me/contactFolders` | Organization |

---

### LOW PRIORITY - Advanced Features

- **Change notifications (webhooks):** Real-time updates
- **Extended properties:** Custom MAPI properties
- **Open extensions:** Custom data storage
- **Shared mailboxes:** Access other users' mail
- **Mail tips:** Get recipient info before sending
- **Search folders:** Saved searches
- **User photo:** Profile picture

---

## Unused Parameters Analysis

### send_message() - Missing CLI Exposure
| Parameter | In API | In CLI | Notes |
|-----------|--------|--------|-------|
| `importance` | Yes | No | Add `--importance` flag |
| `html` | Yes | No | Add `--html` flag |
| `bcc` | Yes | No | Add `--bcc` flag |

### create_event() - Missing CLI Exposure
| Parameter | In API | In Notes | Notes |
|-----------|--------|----------|-------|
| `body` | Yes | No | Add `--body` flag |
| `all_day` | Yes | No | Add `--all-day` flag |

### list_messages() - Missing Filter Options
| Parameter | Available | In CLI | Notes |
|-----------|-----------|--------|-------|
| `$orderby` | Yes | No | Add `--sort` flag |
| `$filter` | Yes | Limited | Expose more filter options |
| `$select` | Yes | No | Optimize responses |

---

## Ignored Response Fields

### Message Response
Fields returned by API but not displayed:
- `categories` - Could show email tags
- `flag` - Follow-up status
- `conversationId` - Thread grouping
- `internetMessageId` - RFC message ID
- `webLink` - Direct Outlook link
- `inferenceClassification` - Focused/Other
- `replyTo` - Reply address

### Event Response
Fields returned but not displayed:
- `isOnlineMeeting` - Teams meeting flag
- `onlineMeeting.joinUrl` - Meeting link
- `showAs` - Free/busy status
- `sensitivity` - Private/confidential
- `responseStatus` - User's response
- `isCancelled` - Event cancelled
- `webLink` - Direct Outlook link
- `categories` - Event categories

---

## Documentation Quality Assessment

### README.md
| Aspect | Score | Notes |
|--------|-------|-------|
| Installation | Good | Clear build steps |
| Quick Start | Good | Azure setup well documented |
| Usage Examples | Good | Common commands shown |
| Troubleshooting | Good | Common issues addressed |
| API Reference | Missing | No detailed command reference |

### Missing Documentation
1. **Full command reference** with all flags
2. **Examples for complex operations** (bulk, filters)
3. **Output format documentation** (JSON structure)
4. **Error codes and handling**
5. **Rate limiting guidance**

---

## Recommended Improvements

### Phase 1 - Quick Wins (1-2 days)
1. Add `reply`, `reply-all`, `forward` commands
2. Expose `--importance`, `--html`, `--bcc` flags
3. Add `--category` flag for send/list
4. Include online meeting info in event display
5. Add `calendar delete` command
6. Show more message fields in output

### Phase 2 - Core Features (3-5 days)
1. Implement attachments list/download
2. Add `flag` command for follow-up
3. Add `calendar respond` (accept/decline)
4. Implement `settings auto-reply` commands
5. Add `--from`/`--to` date filters for events
6. Add conversation view

### Phase 3 - Advanced Features (1-2 weeks)
1. Implement delta queries for sync
2. Add free/busy schedule lookup
3. Implement batch operations
4. Add contacts support
5. Implement message rules

---

## Scopes Analysis

### Current Scopes
```python
SCOPES = [
    'https://graph.microsoft.com/Mail.ReadWrite',
    'https://graph.microsoft.com/Mail.Send',
    'https://graph.microsoft.com/Calendars.ReadWrite',
    'https://graph.microsoft.com/User.Read',
    'https://graph.microsoft.com/MailboxSettings.Read',
]
```

### Recommended Additional Scopes
| Scope | Purpose | When Needed |
|-------|---------|-------------|
| `Contacts.Read` | Read contacts | For contacts feature |
| `Contacts.ReadWrite` | Manage contacts | For contact management |
| `MailboxSettings.ReadWrite` | Set auto-reply | For settings commands |
| `Calendars.Read.Shared` | Shared calendars | For shared access |

---

## Conclusion

cc_outlook has a solid foundation but utilizes only ~35% of available Microsoft Graph API capabilities. The identified quick wins would significantly enhance LLM-driven email/calendar workflows:

1. **Reply/Forward** - Essential for email conversations
2. **Attachments** - Critical for document workflows
3. **Calendar management** - Delete/update/respond to events
4. **Mailbox settings** - Auto-reply/working hours
5. **Richer data display** - Categories, flags, meeting links

The O365 Python library already supports most of these features, making implementation straightforward. Prioritizing Phase 1 improvements would provide immediate value with minimal effort.
