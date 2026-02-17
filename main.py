import os
import discord
from discord.ext import commands
import time
from myserver import server_on

LOG_CHANNEL_ID = 1473257303666069639

# ===== Intents =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

cooldown = {}  # user_id : last_time

# ===== Ready =====
@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")

# ===== Modal (ต้องอยู่ก่อน View) =====
class AngpaoModal(discord.ui.Modal, title="ส่งลิงก์อั่งเปา"):
    link = discord.ui.TextInput(
        label="ลิงก์ซองอั่งเปา",
        placeholder="https://gift.truemoney.com/campaign/?v=xxxxxxxxxxxxxxx",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.link.value.startswith("https://gift.truemoney.com/"):
            await interaction.response.send_message(
                "❌ ลิงก์ไม่ถูกต้อง",
                ephemeral=True
            )
            return

        cooldown[interaction.user.id] = time.time()

        log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)

        embed = discord.Embed(
            title="🧧 มีการส่งลิงก์อั่งเปา ",
            color=0x00ff99
        )
        embed.add_field(name="ผู้ส่ง", value=interaction.user.mention)
        embed.add_field(name="เซิร์ฟเวอร์", value=interaction.guild.name)
        embed.add_field(name="ลิงก์", value=self.link.value)

        await log_channel.send(
            content=f"📢 แจ้งเตือนถึง <@{848068744303083551}>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(users=True)
        )

        await interaction.response.send_message(
            "✅ ส่งซองอั่งเปาเรียบร้อยแล้ว",
            ephemeral=True
        )

# ===== View =====
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🧧 ส่งลิงก์อั่งเปา", style=discord.ButtonStyle.green)
    async def send_angpao(self, interaction: discord.Interaction, _):
        user_id = interaction.user.id
        now = time.time()

        if user_id in cooldown and now - cooldown[user_id] < 10:
            await interaction.response.send_message(
                "⏱️ กรุณารอ 10 วินาทีก่อนส่งใหม่",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(AngpaoModal())

    @discord.ui.button(label="🛒 ดูราคายศ", style=discord.ButtonStyle.gray)
    async def rank_info(self, interaction: discord.Interaction, _):
        embed = discord.Embed(
            title="🛒 รายละเอียดราคายศ 🔻",
            description=(
                "<@&1082885961953853540>\n"
                "• ราคายศรวมทั้งหมด : __**100฿**__ *(คุ้มกว่า!)* 🔥  🔥  🔥\n\n"

                "<@&1082668970718527508>\n"
                "• ตัวอย่างห้อง: <#1051070486500626502>\n"
                "• ราคายศ : __**79฿**__\n\n"

                "<@&1082667309254054008>\n"
                "• ตัวอย่างห้อง: <#1064082990990381127>\n"
                "• ราคายศ : __**40฿**__\n\n"

                "<@&1082667313163157515>\n"
                "• ตัวอย่างห้อง: <#1049681634728869949>\n"
                "• ราคายศ : __**20฿**__"
            ),
            color=0xFFD700
        )

        embed.set_footer(text="🧧 ชำระผ่านซองอั่งเปา TrueWallet เท่านั้น")

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )


# ===== Command setup =====
@bot.command()
async def setup(ctx):
    embed = discord.Embed(
        title="🧧 ซื้อยศด้วยซองอั่งเปา __TrueWallet !__",
        description="* ใส่จำนวนเงินในซองตามราคายศที่กำหนด",
        color=0xffc0cb
    )
    embed.set_image(url="https://i.postimg.cc/9FqtF8fq/aungpao-truewallet-01.png")

    embed.set_footer(
        text=" ชำระผ่านซองอั่งเปา TrueWallet 24ชม.",
        icon_url="https://i.postimg.cc/c6GHg5YB/image.png"
    )

    await ctx.send(embed=embed, view=MainView())

server_on()

bot.run(os.getenv("TOKEN"))