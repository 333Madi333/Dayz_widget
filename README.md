# Агония PVE 1 player widget

A small web page that shows how many players are on the DayZ server **Агония PVE 1**
(109.248.4.73:2308, Chernarus) and how busy it is at each hour of the day.

## How it works

The DZSA Launcher API only tells you the player count right now, so something has to
check it regularly and keep the history. This setup uses GitHub for both, for free:

1. **`collect.py`** asks DZSA for the current count
   (`https://dayzsalauncher.com/api/v1/query/109.248.4.73/2309`; 2309 is the query port,
   2308 is the game port) and appends `[unix time, players]` to `data/history.json`.
   It keeps the last 45 days.
2. **`.github/workflows/collect.yml`** runs `collect.py` every 10 minutes on GitHub
   Actions and commits the updated `data/history.json`.
3. **`index.html`** is the widget. GitHub Pages serves it, it reads `data/history.json`,
   and it refreshes itself every 5 minutes. It shows:
   - the latest player count out of the max, with how long ago it was checked
   - a bar per hour of the day with the average players over the last 7 or 30 days
   - an orange line with today's readings on top
   - the busiest hour, the quietest hour and today's peak
   - a switch between your own time zone and Moscow time

## Setup (about 5 minutes)

1. Create a new **public** repository on GitHub, for example `dayz-online`.
2. Upload everything in this folder, including the hidden `.github` folder.
   (On the GitHub website: Add file → Upload files, then drag the folder contents in.
   If the `.github` folder doesn't upload, create the file
   `.github/workflows/collect.yml` by hand with Add file → Create new file and paste it.)
3. **Settings → Actions → General → Workflow permissions**: choose
   *Read and write permissions* and save.
4. **Actions** tab → *Record player count* → **Run workflow** once, to check it works.
   `data/history.json` should get its first point.
5. **Settings → Pages**: Source *Deploy from a branch*, branch `main`, folder `/ (root)`.
   After a minute the widget is live at `https://<your-username>.github.io/<repo>/`.

The hour averages fill in over the first day and become reliable after about a week.

## Changing things

- Different server: edit `SERVER_IP` and `QUERY_PORT` at the top of `collect.py`.
- Check more or less often: edit the `cron` line in the workflow (GitHub's minimum is
  every 5 minutes, and it often runs a few minutes late).
- Embed it elsewhere (Discord bot page, website): use an `<iframe>` pointing at the
  Pages URL.

## Things to know

- GitHub pauses scheduled workflows in a repository with no activity for 60 days.
  The collector's own commits normally count as activity, but if the line stops
  moving, open the Actions tab and re-enable the workflow.
- If DZSA can't reach the server at a given check, that check is skipped rather than
  recorded as 0 players.
