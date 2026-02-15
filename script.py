import os
import discord
from discord.ext import commands
import time
import random
from myserver import server_on

# ================= TOKEN =================


# ================= CONFIG =================
LOG_CHANNEL_ID = 1470417750319960168

ROLE_ID = 1069133664362963045  # บทบาทแชร์ดิส
CHANNEL_ID = 1472149753826377780  # ห้องแจ้งแชร์สำเร็จ
STICKY_CHANNEL_ID = 1227127117519519764

# ระบบรับยศยืนยัน (เพิ่มใหม่)
CONFIRM_ROLE_ID = 1049292011997503498
CONFIRM_CHANNEL_ID = 1472547979641749690

EMBED_COLOR = 0x00ff88

# ================= INTENTS =================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

cooldown = {}
sticky_messages = {}

# ================= READY =================
@bot.event
async def on_ready():
    bot.add_view(ConfirmRoleView())
    print(f"🤖 Logged in as {bot.user}")

# ==================================================
# 1️⃣ ระบบอั่งเปา (ของเดิมคุณครบ)
# ==================================================

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
            content=f"📢 แจ้งเตือนถึง <@848068744303083551>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(users=True)
        )

        await interaction.response.send_message(
            "✅ ส่งซองอั่งเปาเรียบร้อยแล้ว",
            ephemeral=True
        )

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
                "• ราคายศรวมทั้งหมด : __**100฿**__ *(คุ้มกว่า!)* 🔥 🔥 🔥\n\n"
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

# ==================================================
# 2️⃣ ระบบแชร์ดิส (ครบสุ่มข้อความ + embed เดิมคุณ)
# ==================================================

@bot.event
async def on_member_update(before, after):

    before_roles = set(before.roles)
    after_roles = set(after.roles)
    added_roles = after_roles - before_roles

    if not added_roles:
        return

    for role in added_roles:
        if role.id == ROLE_ID:

            channel = bot.get_channel(CHANNEL_ID)
            if not channel:
                return

            giver = None
            async for entry in after.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.member_role_update
            ):
                if entry.target.id == after.id:
                    giver = entry.user
                    break

            status_messages = [
                "🎀 เย้! คุณได้แชร์สำเร็จแล้ว~",
                "💖 ขอบคุณที่แชร์ดิสนะ!",
                "🌟 แชร์เก่งมากเลย!",
                "✨ ได้รับยศเรียบร้อยแล้ว!",
                "🎉 สำเร็จแล้ว! ขอบคุณมากนะ~"
            ]

            random_status = random.choice(status_messages)

            embed = discord.Embed(
                title="<a:Verify:1145246019668418620>  __แชร์สำเร็จเรียบร้อยแล้ว!__  <a:bell_2:1472134346449354844>",
                color=EMBED_COLOR
            )

            embed.set_author(
                name=after.display_name,
                icon_url=after.display_avatar.url
            )

            embed.set_thumbnail(url=after.display_avatar.url)

            embed.add_field(
                name=" ",
                value=f"`👤 ผู้ใช้ :` {after.mention}",
                inline=False
            )

            embed.add_field(
                name=" ",
                value=f"`🏅 ได้รับยศ :` {role.mention}",
                inline=False
            )

            if giver:
                embed.add_field(
                    name=" ",
                    value=f"`👮 ให้โดย :` {giver.mention}",
                    inline=False
                )
                embed.add_field(name=" ", value=" ", inline=False)

            embed.add_field(
                name=" ",
                value=f"```🟢 สถานะแชร์ดิส : {random_status}```",
                inline=False
            )

            embed.set_image(
                url="https://i.postimg.cc/8PjM2Y45/rainbow-water-falling.gif"
            )

            embed.set_footer(
                text=after.guild.name,
                icon_url=after.guild.icon.url if after.guild.icon else None
            )

            embed.timestamp = discord.utils.utcnow()

            msg = await channel.send(embed=embed)
            await msg.add_reaction("✅")

# ================= STICKY SYSTEM =================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id == STICKY_CHANNEL_ID:

        old_message = sticky_messages.get(message.channel.id)

        if old_message:
            try:
                await old_message.delete()
            except discord.HTTPException:
                pass

        sticky_embed = discord.Embed(
            title=" <a:loading_1:1145245426304417823> ส่งหลักฐานการแชร์ได้ที่นี่ <a:star_1:1472134208993497202>",
            description=" ``` โปรดรอแอดมินตรวจสอบหลักฐานสักครู่ 💖```",
            color=0xff66cc
        )

        new_message = await message.channel.send(embed=sticky_embed)
        sticky_messages[message.channel.id] = new_message

    await bot.process_commands(message)

# ==================================================
# 3️⃣ ระบบรับยศยืนยัน (เพิ่มใหม่)
# ==================================================

class ConfirmRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="กดรับยศ",
        style=discord.ButtonStyle.success,
        custom_id="confirm_role_button",
        emoji=discord.PartialEmoji(
            name="correct_2",
            id=1472134441248751788
        )
    )
    async def confirm_role(self, interaction: discord.Interaction, _):

        if interaction.channel.id != CONFIRM_CHANNEL_ID:
            await interaction.response.send_message(
                "❌ กดได้เฉพาะห้องที่กำหนด",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(CONFIRM_ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                "❌ ไม่พบบทบาท",
                ephemeral=True
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "❌ คุณกดรับยศนี้ไปแล้ว",
                ephemeral=True
            )
            return

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            f"✅ คุณได้รับยศ {role.mention} เรียบร้อยแล้ว",
            ephemeral=True
        )

@bot.command()
async def test(ctx):

    if ctx.channel.id != CONFIRM_CHANNEL_ID:
        return

    embed = discord.Embed(
        title="กดที่อีโมจิ  <a:correct_2:1472134441248751788>  เพื่อรับยศสมาชิก <a:gift_1:1472607090705961041> ",
        description=" <a:star_1:1472134208993497202> กดปุ่มด้านล่างเพื่อรับยศ <@&1049292011997503498>  <a:star_1:1472134208993497202> ",
        color=0xFF0000  # สีแดง

    )
    embed.set_image(
        url="https://i.postimg.cc/Cx4ybpLQ/standard.gif"
    )

    embed.set_footer(
        text=" ! เซิร์ฟนี้มีระบบซื้อยศผ่านซองอั่งเปา TrueWallet ตลอด 24ชม.",
        icon_url="https://i.postimg.cc/CM8jvhy7/DOHEE-icon-png.png"
    )

    await ctx.send(embed=embed, view=ConfirmRoleView())

# ================= RUN =================

server_on()

bot.run(os.getenv("TOKEN"))
