# ColorStack@UMBC Onboarding Bot

Discord bot that gates new members through a sequential onboarding flow.

## Flow

1. New member joins → gets **Verifying** → sees only `#start-here`
2. Clicks **Start** → modal asks first/last name → nickname set, **Verifying** removed, **Name Set** added → unlocks `#welcome-and-rules`
3. Reacts with ✅ on the rules message → **Rules Agreed** added → unlocks `#get-roles`
4. Picks a year role in `#get-roles` (Carl-bot reaction roles; this bot does not handle that step)
5. Posts anything in `#introductions` → **Intro Done** added → unlocks `#linkedin`
6. Posts a message containing `linkedin.com` in `#linkedin` → **colorstackers** added → unlocks the rest of the server

## Setup

1. Create these roles (Server Settings → Roles):
   - Verifying
   - Name Set
   - Rules Agreed
   - Intro Done

   Freshman / Sophomore / Junior / Senior / Alumni and colorstackers should already exist.

   **Role hierarchy matters — this bit us repeatedly during setup.** Drag the bot's own role (**ColorStack Onboarding**) so it sits *above every role it needs to grant*: Verifying, Name Set, Rules Agreed, Intro Done, **and colorstackers**. A bot can never assign a role that outranks its own — Discord fails the request with a `403 Forbidden (error code: 50013)` if you get this wrong, silently if you haven't added error handling. Only Admins needs to sit above the bot; the bot never touches Admins.

   Carl-bot needs the same treatment for the year roles (Freshman/Sophomore/Junior/Senior/Alumni) — make sure carl-bot's role sits above all five.

2. Fill in every ID in the CONFIG section of `colorstack_bot.py`. Enable Developer Mode (User Settings → Advanced), then right-click a role or channel and choose Copy ID.

3. Set channel permissions so each role can only see its own step, and `@everyone` sees none of them:

   | Channel | Visible to |
   |---|---|
   | `#start-here` | Verifying |
   | `#welcome-and-rules` | Name Set |
   | `#get-roles` | Rules Agreed |
   | `#introductions` | year roles |
   | `#linkedin` | Intro Done |

   The bot assigns Verifying on join so new members see `#start-here` immediately.

   **Every one of these channels also needs the bot's own role explicitly added to its permission list**, with View Channel, Send Messages, Read Message History, and Add Reactions allowed. Being invited to the server with the right OAuth permissions is not enough — an explicit `@everyone` deny on a private channel blocks the bot too unless its role is separately added. The same applies to carl-bot on `#get-roles`, since carl-bot needs to see reactions there to grant year roles.

4. In the Discord Developer Portal, enable **Server Members Intent** and **Message Content Intent**.

5. Add a `Procfile` (no extension) alongside the bot with:
   ```
   worker: python colorstack_bot.py
   ```
   Railway (and similar platforms) need this to know how to start the bot — without it, the build succeeds but nothing runs.

6. Set `DISCORD_BOT_TOKEN` as an environment variable on your host (never commit it to the repo), then run:
   ```
   pip install -r requirements.txt
   python colorstack_bot.py
   ```

7. Once the bot is online, an admin should type `!post_start` in `#start-here` and `!post_rules` in `#welcome-and-rules` to post the Start button and the rules checkmark message.

## Notes / gotchas learned the hard way

- **The Start button survives restarts.** `on_ready` calls `bot.add_view(StartView())` so a button posted before a redeploy still works after one. You do not need to re-run `!post_start` after every deploy.
- **The rules-reaction message does not have this same protection.** `RULES_MESSAGE_ID` is stored in memory and resets to `None` on every restart. In practice this is harmless (the reaction check simply stops filtering by message ID and accepts any ✅ in the channel), but if you ever post more than one rules message, re-run `!post_rules` after a fresh deploy to be safe.
- **Testing must use a real alt account with no elevated roles.** Testing with your own Admin account will always fail the nickname/role steps, since the bot can never modify someone who outranks it — you'll now see a clear error message instead of silence, but it still won't complete successfully.
- **`!post_start` / `!post_rules` are admin-only** (`@commands.has_permissions(administrator=True)`). If a non-admin tries them, they now get a clear "You need Administrator permission" message instead of silence.
- Errors during onboarding (Forbidden, missing role/channel config, etc.) are posted directly in the relevant channel so they're visible without digging through hosting logs.