import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import sqlite3

import key
import pytz

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# SQLite 데이터베이스 연결
conn = sqlite3.connect('bot.db')
c = conn.cursor()

# 테이블 생성 - 각 서버의 로그 채널 저장
c.execute('''CREATE TABLE IF NOT EXISTS log_channels
             (guild_id INTEGER PRIMARY KEY, log_channel INTEGER)''')
conn.commit()

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready!')

@bot.slash_command(name= "logchannel")
async def setlogchannel(ctx: commands.Context, channel: discord.TextChannel):
    # 관리자만 로그 채널 설정 가능
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("관리자 권한이 필요합니다.")
        return

    c.execute('''INSERT OR REPLACE INTO log_channels (guild_id, log_channel)
                 VALUES (?, ?)''', (ctx.guild.id, channel.id))
    conn.commit()
    await ctx.respond(f"로그 채널이 {channel.mention}으로 설정되었습니다.")

@bot.event
async def on_member_join(member):
    c.execute('SELECT log_channel FROM log_channels WHERE guild_id=?', (member.guild.id,))
    result = c.fetchone()
    if result:
        log_channel_id = result[0]
        join_date = member.created_at
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = current_time - join_date
        thirty_days = timedelta(days=30)
        if difference < thirty_days:
            await member.ban(reason="계정 생성 후 30일이 지나지 않았습니다.")
            print(f"{member}는 계정 생성 후 30일이 지나지 않아 차단되었습니다.")
            # 로그를 채널에 기록
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(title="Spam Blocked", color=0xFF2D00)
                embed.add_field(name="Account creation", value=difference, inline=False)
                embed.add_field(name="Result", value="Ban", inline=False)
                embed.add_field(name="Reason", value="계정 생성 후 30일이 지나지 않았습니다.", inline=False)
                embed.set_author(name=f"{member.name} {member.id}",icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
                embed.timestamp = datetime.utcnow()

                await log_channel.send(embed=embed)
        else:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                    embed = discord.Embed(title="UserJoin", color=0x62c1cc)
                    embed.add_field(name="Account creation", value=difference, inline=False)
                    embed.add_field(name="Result", value="Pass", inline=False)
                    embed.set_author(name=f"{member.name} {member.id}",icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
                    embed.timestamp = datetime.utcnow()
                    await log_channel.send(embed=embed)

bot.run(key.discord_key)
