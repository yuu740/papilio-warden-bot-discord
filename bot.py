import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

# Menghapus help command bawaan agar kita bisa membuat help kustom sendiri
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Yahoo! Bot {bot.user.name} sudah berhasil online dan siap berkelana!')


# === PERINTAH 1: DOCUMENTATION / HELP COMMAND ===
@bot.command(name="bothelp")
async def bothelp(ctx):
    embed = discord.Embed(
        title="📖 KAMPUS WANGSHENG - DOKUMENTASI BOT",
        description="Halo! Aku bot kustom pemantau member. Berikut adalah mantra perintah yang bisa kamu gunakan:",
        color=discord.Color.from_rgb(241, 90, 34) # Warna oranye khas Hu Tao
    )
    embed.add_field(
        name="`!listall`", 
        value="Menampilkan struktur semua role di server ini beserta daftar anggotanya dalam bentuk poin kustom.", 
        inline=False
    )
    embed.add_field(
        name="`!listmember [Nama Role]`", 
        value="Mencari dan menjabarkan spesifik anggota dari satu role yang kamu ketik.\n*Contoh: !listmember Shadow Dweller*", 
        inline=False
    )
    embed.set_footer(text=f"Request oleh: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


# === PERINTAH 2: LIST MEMBER BERDASARKAN ROLE ===
@bot.command()
async def listmember(ctx, *, nama_role: str):
    role = discord.utils.get(ctx.guild.roles, name=nama_role)
    
    if role is None:
        await ctx.send(f"❌ Role '{nama_role}' tidak ditemukan di server ini.")
        return
        
    daftar_nama = [f"- {member.display_name}" for member in role.members]
    
    if not daftar_nama:
        await ctx.send(f"👻 Gak ada member di dalam role **{role.name}**.")
    else:
        pesan = f"**📊 Daftar Anggota Role {role.name}:**\n" + "\n".join(daftar_nama)
        if len(pesan) > 2000:
            for i in range(0, len(pesan), 1900):
                await ctx.send(pesan[i:i+1900])
        else:
            await ctx.send(pesan)


# === PERINTAH 3: DINAMIS LIST ALL (UNTUK SEMUA SERVER) ===
@bot.command()
# Buka tanda pagar (#) di bawah ini jika ingin MEMBATASI perintah hanya untuk Role tertentu:
# @commands.has_any_role("Guild Master", "Manager", "Admin") 
async def listall(ctx):
    output = []
    # 1. Otomatis mengambil nama server di mana perintah ini diketik
    output.append(f"**📊 DAFTAR ANGGOTA {ctx.guild.name.upper()}**")
    output.append("---")
    
    # 2. Mengambil semua role di server, diurutkan dari kasta tertinggi (kecuali @everyone)
    roles_dinamis = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    
    for role in roles_dinamis:
        # Mengabaikan role bawaan @everyone dan role bawaan bot agar list tidak kotor
        if role.is_default() or role.is_bot_managed():
            continue
            
        # Filter anggota manusia (bukan bot) di dalam role tersebut
        manusia_members = [m.display_name for m in role.members if not m.bot]
        
        output.append(f"🔹 **{role.name}:**")
        if not manusia_members:
            output.append("_- Tidak ada anggota_")
        else:
            # Output diubah menjadi per-point (- Nama) ke bawah
            for nama in manusia_members:
                output.append(f"- {nama}")
        output.append("") # Spasi baris antar role

    # 3. Kategori tambahan otomatis untuk semua Bot yang ada di server tersebut
    all_bots = [m.display_name for m in ctx.guild.members if m.bot]
    output.append("🤖 **Bot:**")
    if not all_bots:
        output.append("_- Tidak ada bot_")
    else:
        for bot_name in all_bots:
            output.append(f"- {bot_name}")

    pesan_full = "\n".join(output)
    
    # Mengirim pesan dengan pengaman batas 2000 karakter Discord
    if len(pesan_full) > 2000:
        baris = pesan_full.split("\n")
        chunk = ""
        for b in baris:
            if len(chunk) + len(b) + 1 > 1900:
                await ctx.send(chunk)
                chunk = b
            else:
                chunk += "\n" + b if chunk else b
        if chunk:
            await ctx.send(chunk)
    else:
        await ctx.send(pesan_full)


# === ERROR HANDLING (Jika role yang di-restrict diakses orang biasa) ===
@listall.error
async def listall_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("🙅‍♂️ *Ayaaa*, kamu tidak punya wewenang khusus untuk memanggil daftar arsip rahasia ini!")

bot.run(TOKEN)