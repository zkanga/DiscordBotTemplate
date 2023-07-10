from discord.ext import commands

from bot_utils.globals import bot, logger

from datetime import datetime

definite_dates = {
    "Starfield": datetime(2023, 9, 6, 0, 0, 0)
    , "Darktide": datetime(2022, 11, 30, 10, 0, 0)
    , "Payday 3": datetime(2023, 9, 21, 0, 0, 0)
    , "Armored Core VI": datetime(2023, 8, 25, 0, 0, 0)
    , "Baldur's Gate 3": datetime(2023, 8, 31, 0, 0, 0)
    , "Wizard with a Gun": datetime(2024, 1, 1, 0, 0, 0)
    , "Ark 2": datetime(2024, 1, 1, 0, 0, 0)
    , "Haunted Chocolatier": datetime(2025, 1, 1, 0, 0, 0)
    , "Nightingale": datetime(2024, 1, 1, 0, 0, 0)

}

indefinite_dates = {
    "Baldur's Gate 3"
    , "Nightingale"
    , "Haunted Chocolatier"
    , "Ark 2"
    , "Wizard with a Gun"
    , "Baldur's Gate 3"
}


def date_diff(date_name, d1, d2=datetime.now(), suffix=""):
    diff = d1 - d2
    days_diff = abs(diff.days)

    if d1 < d2:
        date_label = f"since {date_name} came out"
    else:
        date_label = f"until {date_name} comes out"

    out = f"~{days_diff / 30.437:.2f} month(s) or {days_diff} day(s) {date_label} on {d1.strftime('%x')}{suffix}"
    return out


class DateTracker(commands.Cog):
    """Commands to dates"""

    def __init__(self):
        self.bot = bot

    @commands.command()
    async def track(self, ctx):
        """Find information about stored date(s)"""
        message = str(ctx.message.content)
        out = []
        dates = []
        for date_name in definite_dates.keys():
            if date_name in message:
                if date_name in indefinite_dates:
                    suffix = " (Allegedly)"
                else:
                    suffix = ""
                dates.append(date_name)
                out.append(date_diff(date_name, definite_dates[date_name], suffix=suffix))
        out = '\n' + '\n'.join(out)
        await ctx.send(f"{out}\nTracked {', '.join(dates)} {ctx.author.mention}")
        logger.info(f"Tracker: SUCCESSFULLY served {dates} date info to {ctx.author} in {ctx.guild}")

    @commands.command()
    async def dates(self, ctx):
        """Dates that can be tracked"""
        delim = "\n\t !track "
        out = f"Valid commands are :{delim}"
        out += delim.join(sorted(list(definite_dates.keys())))
        await ctx.send(f"{out}\n{ctx.author.mention}")
