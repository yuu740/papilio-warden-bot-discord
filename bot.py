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


# === PERINTAH 1: LIST MEMBER BERDASARKAN ROLE ===
@bot.command()
async def listmember(ctx, *, nama_role: str):
    role = discord.utils.get(ctx.guild.roles, name=nama_role)
    
    if role is None:
        await ctx.send(f"Role '{nama_role}' tidak ditemukan di server ini.")
        return
        
    daftar_nama = [member.display_name for member in role.members]
    
    if not daftar_nama:
        await ctx.send(f"Gak ada member di dalam role **{role.name}**.")
    else:
        pesan = f"**📊 Daftar Anggota Role {role.name}:**\n" + "\n".join(daftar_nama)
        if len(pesan) > 2000:
            for i in range(0, len(pesan), 1900):
                await ctx.send(pesan[i:i+1900])
        else:
            await ctx.send(pesan)


# === PERINTAH 2: LIST ALL MEMBER (MENGELOMPOKKAN PER ROLE) ===
@bot.command()
async def listall(ctx):
    # Fungsi bantuan untuk mengambil list nama berdasarkan nama role
    def get_role_members_text(role_name: str, is_bot_check: bool = False):
        if is_bot_check:
            # Khusus untuk mendeteksi semua akun bot di server
            members = [m.display_name for m in ctx.guild.members if m.bot]
        else:
            # Mencari role berdasarkan teks nama role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                return "_Role tidak ditemukan di server_"
            members = [m.display_name for m in role.members if not m.bot] # Mengabaikan bot agar tidak masuk ke role manusia
            
        if not members:
            return "_Tidak ada anggota_"
        return ", ".join(members) # Menggabungkan nama member dipisah tanda koma agar hemat karakter

    # Menyusun template output persis seperti yang kamu minta
    output = []
    output.append("**📊 DAFTAR ANGGOTA REALM OF UMBRA**")
    output.append("---")
    
    output.append("👑 **Guild Master:**")
    output.append(get_role_members_text("Guild Master"))
    output.append("") # Spasi baris kosong
    
    output.append("⚔️ **Vice Guild Master:**")
    output.append(get_role_members_text("Vice Guild Master"))
    output.append("")
    
    output.append("💼 **Manager:**")
    output.append(get_role_members_text("Manager"))
    output.append("")
    
    output.append("👤 **Shadow Dweller:**")
    output.append(get_role_members_text("Shadow Dweller"))
    output.append("")
    
    output.append("🪪 **Retired Darkian:**")
    output.append(get_role_members_text("Retired Darkian"))
    output.append("")
    
    output.append("💂 **Regular Darkian:**")
    output.append(get_role_members_text("Regular Darkian"))
    output.append("")
    
    # Kategori tambahan untuk list Bot
    output.append("🤖 **Bot:**")
    output.append(get_role_members_text("", is_bot_check=True))

    # Menggabungkan seluruh baris menjadi satu teks pesan besar
    pesan_full = "\n".join(output)
    
    # Fitur Anti-Limit (Jika terlalu panjang, potong per 1900 karakter agar tidak eror)
    if len(pesan_full) > 2000:
        for i in range(0, len(pesan_full), 1900):
            await ctx.send(pesan_full[i:i+1900])
    else:
        await ctx.send(pesan_full)


# Menjalankan bot menggunakan variabel TOKEN dari file .env
bot.run(TOKEN)