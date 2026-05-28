import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Sinkronisasi perintah otomatis saat bot menyala
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Yahoo! Berhasil menyinkronkan {len(synced)} perintah Slash!")
    except Exception as e:
        print(f"Gagal sinkronisasi perintah: {e}")
    print(f'Bot {bot.user.name} sudah aktif 24 jam dan siap berkelana!')


# === PERINTAH 1: SLASH HELP COMMAND ===
@bot.tree.command(name="bothelp", description="Menampilkan dokumen mantra perintah Papilio Warden")
async def bothelp(ctx: discord.Interaction):
    embed = discord.Embed(
        title="📖 KAMPUS WANGSHENG - DOKUMENTASI BOT",
        description="Halo! Aku bot kustom pemantau member. Berikut adalah mantra perintah yang bisa kamu gunakan lewat perintah `/`:",
        color=discord.Color.from_rgb(241, 90, 34)
    )
    embed.add_field(
        name="`/listall`", 
        value="Menampilkan struktur semua role di server ini beserta daftar anggotanya dalam bentuk poin kustom.", 
        inline=False
    )
    embed.add_field(
        name="`/listmember [nama_role]`", 
        value="Mencari dan menjabarkan spesifik anggota dari satu role yang kamu ketik.", 
        inline=False
    )
    embed.set_footer(text=f"Request oleh: {ctx.user.display_name}", icon_url=ctx.user.display_avatar.url)
    
    # Menggunakan response.send_message khusus untuk Slash Command
    await ctx.response.send_message(embed=embed)


# === PERINTAH 2: SLASH LIST MEMBER PER ROLE ===
@bot.tree.command(name="listmember", description="Melihat daftar anggota dari satu role tertentu")
async def listmember(ctx: discord.Interaction, nama_role: str):
    role = discord.utils.get(ctx.guild.roles, name=nama_role)
    
    if role is None:
        await ctx.response.send_message(f"❌ Role '{nama_role}' tidak ditemukan di server ini.", ephemeral=True)
        return
        
    daftar_nama = [f"- {member.display_name}" for member in role.members]
    
    if not daftar_nama:
        await ctx.response.send_message(f"👻 Gak ada member di dalam role **{role.name}**.")
    else:
        pesan = f"**📊 Daftar Anggota Role {role.name}:**\n" + "\n".join(daftar_nama)
        if len(pesan) > 2000:
            # Kirim potongan pertama
            await ctx.response.send_message(pesan[0:1900])
            # Kirim sisanya lewat follow-up
            for i in range(1900, len(pesan), 1900):
                await ctx.followup.send(pesan[i:i+1900])
        else:
            await ctx.response.send_message(pesan)


# === PERINTAH 3: SLASH LIST ALL DINAMIS ===
@bot.tree.command(name="listall", description="Menampilkan seluruh kasta role dan anggotanya")
async def listall(ctx: discord.Interaction):
    # Mengirim tanda "bot sedang memikirkan data" agar tidak terkena timeout 3 detik dari Discord
    await ctx.response.defer()
    
    output = []
    output.append(f"**📊 DAFTAR ANGGOTA {ctx.guild.name.upper()}**")
    output.append("---")
    
    roles_dinamis = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    
    for role in roles_dinamis:
        if role.is_default() or role.is_bot_managed():
            continue
            
        manusia_members = [m.display_name for m in role.members if not m.bot]
        
        output.append(f"🔹 **{role.name}:**")
        if not manusia_members:
            output.append("_- Tidak ada anggota_")
        else:
            for nama in manusia_members:
                output.append(f"- {nama}")
        output.append("")

    all_bots = [m.display_name for m in ctx.guild.members if m.bot]
    output.append("🤖 **Bot:**")
    if not all_bots:
        output.append("_- Tidak ada bot_")
    else:
        for bot_name in all_bots:
            output.append(f"- {bot_name}")

    pesan_full = "\n".join(output)
    
    if len(pesan_full) > 2000:
        baris = pesan_full.split("\n")
        chunk = ""
        is_first = True
        for b in baris:
            if len(chunk) + len(b) + 1 > 1900:
                if is_first:
                    await ctx.followup.send(chunk)
                    is_first = False
                else:
                    await ctx.followup.send(chunk)
                chunk = b
            else:
                chunk += "\n" + b if chunk else b
        if chunk:
            await ctx.followup.send(chunk)
    else:
        await ctx.followup.send(pesan_full)

async def main():
    # Membuat session baru yang bersih di dalam loop async
    async with bot:
        await bot.start(TOKEN)

# Menjalankan bot dengan penanganan eror loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot dimatikan secara manual.")
    except Exception as e:
        print(f"⚠️ Terjadi gangguan koneksi pada bot: {e}")