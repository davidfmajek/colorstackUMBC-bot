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

1. Create these roles (Server Settings → Roles), above `@everyone` and below Admins:
   - Verifying
   - Name Set
   - Rules Agreed
   - Intro Done

   Freshman / Sophomore / Junior / Senior / Alumni and colorstackers should already exist.

2. Fill in every ID in the `CONFIG` section of `colorstack_bot.py`. Enable Developer Mode (User Settings → Advanced), then right-click a role or channel and choose **Copy ID**.

3. Set channel permissions so each role can only see its own step, and `@everyone` sees none of them:

   | Channel | Visible to |
   |---|---|
   | `#start-here` | Verifying |
   | `#welcome-and-rules` | Name Set |
   | `#get-roles` | Rules Agreed |
   | `#introductions` | year roles |
   | `#linkedin` | Intro Done |

   The bot assigns Verifying on join so new members see `#start-here` immediately.

4. In the Discord Developer Portal, enable **Server Members Intent** and **Message Content Intent**.

5. Set `DISCORD_BOT_TOKEN` in the environment (or paste it into `CONFIG`), then run:

   ```bash
   pip install -r requirements.txt
   python colorstack_bot.py
   ```

6. Once the bot is online, an admin should type `!post_start` in `#start-here` and `!post_rules` in `#welcome-and-rules` to post the Start button and the rules checkmark message.
