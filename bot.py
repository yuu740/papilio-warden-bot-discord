import os
import discord
from discord.ext import commands
# Impor library untuk membaca file .env
from dotenv import load_dotenv

# Memuat data dari file .env
load_dotenv()
# Mengambil token yang disimpan dengan nama DISCORD_TOKEN
TOKEN = os.getenv('DISCORD_TOKEN')

# Mengaktifkan izin membaca member dan pesan
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

# Menentukan prefix perintah teks menggunakan tanda seru (!)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Yahoo! Bot {bot.user.name} sudah berhasil online!')

@bot.command()
async def listmember(ctx, *, nama_role: str):
    # Mencari role berdasarkan nama yang diketik di Discord
    role = discord.utils.get(ctx.guild.roles, name=nama_role)
    
    if role is None:
        await ctx.send(f"Role '{nama_role}' tidak ditemukan di server ini.")
        return
        
    # Mengambil nama panggilan (display name) semua member di role tersebut
    daftar_nama = [member.display_name for member in role.members]
    
    if not daftar_nama:
        await ctx.send(f"Gak ada member di dalam role **{role.name}**.")
    else:
        # Menggabungkan daftar nama menjadi baris teks ke bawah
        pesan = f"**📊 Daftar Anggota Role {role.name}:**\n" + "\n".join(daftar_nama)
        await ctx.send(pesan)

# Menjalankan bot menggunakan variabel TOKEN dari file .env
bot.run(TOKEN)