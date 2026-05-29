import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import aiohttp  # <--- WAJIB DITAMBAHKAN UNTUK PENGATURAN KONEKTOR

load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN') or os.getenv('DISCORD_TOKEN')

if not TOKEN:
    jalur_secret_hf = "/space_secrets/DISCORD_TOKEN"
    if os.path.exists(jalur_secret_hf):
        with open(jalur_secret_hf, "r") as f:
            TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

# =====================================================================
# RAKITAN BOT KUSTOM UNTUK BYPASS DNS JARINGAN CLOUD
# =====================================================================
class BadakBypassBot(commands.Bot):
    async def setup_hook(self):
        # Memaksa bot menggunakan DNS Google & Cloudflare secara permanen
        resolver = aiohttp.AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
        connector = aiohttp.TCPConnector(resolver=resolver, use_dns_cache=False)
        
        # Masukkan konektor kustom ke dalam sesi HTTP bawaan bot
        self.http.connector = connector

# Ganti inisialisasi bot biasa dengan kelas kustom kita di atas
bot = BadakBypassBot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Yahoo! Berhasil menyinkronkan {len(synced)} perintah Slash!", flush=True)
    except Exception as e:
        print(f"Gagal sinkronisasi perintah: {e}", flush=True)
    print(f'Bot {bot.user.name} sudah aktif dan siap berkelana!', flush=True)


# === PERINTAH SLASH TETAP SAMA ===
@bot.tree.command(name="bothelp", description="Menampilkan dokumen mantra perintah Papilio Warden")
async def bothelp(ctx: discord.Interaction):
    embed = discord.Embed(title="📖 KAMPUS WANGSHENG - DOKUMENTASI BOT", color=discord.Color.from_rgb(241, 90, 34))
    embed.add_field(name="`/listall`", value="Menampilkan struktur semua role.", inline=False)
    embed.add_field(name="`/listmember [nama_role]`", value="Mencari anggota spesifik.", inline=False)
    await ctx.response.send_message(embed=embed)

@bot.tree.command(name="listmember", description="Melihat daftar anggota dari satu role tertentu")
async def listmember(ctx: discord.Interaction, nama_role: str):
    role = discord.utils.get(ctx.guild.roles, name=nama_role)
    if role is None:
        await ctx.response.send_message(f"❌ Role '{nama_role}' tidak ditemukan.", ephemeral=True)
        return
    daftar_nama = [f"- {member.display_name}" for member in role.members]
    pesan = f"**📊 Daftar Anggota Role {role.name}:**\n" + "\n".join(daftar_nama)
    await ctx.response.send_message(pesan[:2000])

@bot.tree.command(name="listall", description="Menampilkan seluruh kasta role dan anggotanya")
async def listall(ctx: discord.Interaction):
    await ctx.response.defer()
    
    output = [f"**📊 DAFTAR ANGGOTA {ctx.guild.name.upper()}**", "---"]
    daftar_bot = []

    for role in sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True):
        if role.is_default() or role.is_bot_managed(): 
            continue
        
        manusia_members = [m.display_name for m in role.members if not m.bot]
        bot_members = [m.display_name for m in role.members if m.bot]
        
        for nama_bot in bot_members:
            if nama_bot not in daftar_bot:
                daftar_bot.append(nama_bot)
        
        if manusia_members:
            output.append(f"🔹 **{role.name}:**")
            for nama in manusia_members:
                output.append(f"- {nama}")
            output.append("") 

    if daftar_bot:
        output.append("🤖 **Bot:**")
        for nama_bot in daftar_bot:
            output.append(f"- {nama_bot}")

    pesan_full = "\n".join(output)
    
    await ctx.followup.send(pesan_full[:2000])


# === SERVER WEB HUGGING FACE ===
class KustomWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = "<html><body style='background:#1e1e2e;color:#f15a22;text-align:center;'><h1>Papilio Warden Status: ACTIVE 24/7</h1></body></html>"
        self.wfile.write(bytes(html, "utf-8"))

def jalankan_server_palsu():
    httpd = HTTPServer(('0.0.0.0', 7860), KustomWebHandler)
    print("🌍 Server web palsu aktif di port 7860!", flush=True)
    httpd.serve_forever()


# === LOGIKA REKONEKSI MENUNGGU JARIKAN AKTIF ===
async def start_bot_dengan_retry():
    while True:
        try:
            print("🔄 Mencoba mengetuk pintu server Discord...", flush=True)
            await bot.start(TOKEN)
        except Exception as e:
            print(f"⚠️ Gagal connect karena blokir jaringan ({e}). Mengulang dalam 10 detik...", flush=True)
            await asyncio.sleep(10)

async def main():
    threading.Thread(target=jalankan_server_palsu, daemon=True).start()
    async with bot:
        await start_bot_dengan_retry()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Eror fatal luar: {e}", flush=True)