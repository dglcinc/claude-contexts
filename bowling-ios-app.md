# Bowling League iOS App — Plan

## Overview

iPhone-only native SwiftUI app for the Mountain Lakes Men's Bowling League.
iPad users continue using the Flask web app at mlb.dglc.com (works well as-is).
Target audience: ~65 bowlers who want quick access to lane assignments, standings, and scores.

## Primary Use Case

Answer the question every bowler has before leaving for the alley:
**When are we bowling, where am I, and what kind of night is it?**

## Home Screen (most important)

Content depends on season state:

**Regular season** — upcoming week's lane assignments for all bowlers.
The logged-in bowler's own lane is highlighted. Shows date/time prominently.
If prior week scores aren't entered yet: "Last week results pending."
Once entered: one-line result ("Your team won 6–2 last week").

**Post-season tournaments** — tournament name + date.
For Club Championship specifically: show both team matchups and lanes
(since it functions like a regular matchup and bowlers need opponent/lane info).

**Off-season** — next season start date if known, or "Season complete" + link to final standings.

## Tab Structure

| Tab | Content |
|-----|---------|
| **Home** | Upcoming week / lane assignments; notification bell in nav bar |
| **Standings** | Team points table; week selector for history; tap team for breakdown |
| **Scores** | Browse any entered week; bowler name, games, handicap, series; tap bowler for season detail |
| **Me** | My season stats (avg, HG, HS), week-by-week history, notification preferences |

## Push Notifications

Three independently toggleable notification types (managed in Me → Notification Settings):

| Notification | When sent | Example message |
|-------------|-----------|-----------------|
| "Bowling tomorrow" | Evening before bowl date (e.g. Sunday 6pm) | "Bowling tomorrow at 7pm. You're on lanes 3-4 vs Team 2." |
| "Bowling tonight" | Morning of bowl day (e.g. 9am) | "Tonight: lanes 3-4 vs Team 2. See you there." |
| "Scores are in" | After each week's scores are entered | "Week 14 scores posted. Your team went 6-2 and moves to 2nd place." |

### Server-side notification infrastructure

- `push_tokens` table in DB: `bowler_id`, `device_token`, `platform`, `preferences` (JSON)
- APNs credentials in `.env`: `.p8` key file path, Team ID, Key ID (all free via Developer portal)
- `send_notifications.py` script — queries DB, checks trigger conditions, sends via APNs HTTP/2
- launchd timer on utility Mac runs the script on schedule
- Flask API endpoint for app to register/update device token and preferences

## Requirements

| Requirement | Detail |
|------------|--------|
| Apple Developer Account | $99/year — required for TestFlight, App Store, and APNs |
| APNs key | `.p8` key file from Developer portal (free, doesn't expire) — add Team ID + Key ID to `.env` |
| Xcode | Free, already on dev Mac |
| TestFlight | Beta distribution to bowlers before App Store submission |
| Flask REST API | New `/api/v1/` blueprint; web app unaffected |

## Architecture

### Flask REST API (new `/api/v1/` blueprint)

Key endpoints:
- `POST /api/v1/auth/request-otp` + `POST /api/v1/auth/verify-otp` → session token (stored in iOS Keychain)
- `GET /api/v1/seasons/current/upcoming` → home screen data (lane assignments, tournament info, next date)
- `GET /api/v1/seasons/{id}/standings`
- `GET /api/v1/seasons/{id}/weeks/{n}` → scores for a week
- `GET /api/v1/bowlers/me` → logged-in bowler's season stats + history
- `POST /api/v1/push/register` → device token + notification preferences
- `PATCH /api/v1/push/preferences` → update notification settings

### SwiftUI App Structure

```
BowlingApp/
├── Auth/          OTP login flow, Keychain token storage
├── Home/          Lane assignments, tournament state, upcoming date
├── Standings/     Team table, week-by-week breakdown
├── Scores/        Week browser, bowler detail
├── Me/            My stats, notification preferences
├── Models/        Codable structs matching API responses
├── API/           URLSession networking layer
└── Notifications/ APNs registration, local preference storage
```

## Build Order

1. **Apple Developer account + APNs key** — prerequisite, takes ~1 day for approval
2. **Flask REST API blueprint** — auth, lane assignments, standings, scores, push token registration
3. **SwiftUI app — core viewer** — Home screen with lane assignments, Standings, Scores, Me tab
4. **TestFlight beta** — distribute to bowlers, gather feedback
5. **Push notifications** — server-side sender script + preference UI in app
6. **App Store submission**

## Status

- [ ] Apple Developer account created
- [ ] APNs key generated
- [ ] Flask REST API blueprint
- [ ] SwiftUI app — core viewer
- [ ] TestFlight beta
- [ ] Push notifications
- [ ] App Store submission
