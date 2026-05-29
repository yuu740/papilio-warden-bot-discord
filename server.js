const { Client, GatewayIntentBits, EmbedBuilder, REST, Routes } = require('discord.js');
const http = require('http');

// 1. Inisialisasi Token dari Environment System Glitch (.env)
const TOKEN = process.env.DISCORD_TOKEN;

if (!TOKEN) {
    console.error("❌ EROR UTAMA: Token DISCORD_TOKEN tidak ditemukan di panel .env Glitch kamu!");
    process.exit(1);
}

// 2. Racik Izin Akses (Intents) - Sama seperti Python
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// Definisi Struktur Perintah Slash
const commands = [
    {
        name: 'bothelp',
        description: 'Menampilkan dokumen mantra perintah Papilio Warden'
    },
    {
        name: 'listmember',
        description: 'Melihat daftar anggota dari satu role tertentu',
        options: [
            {
                name: 'nama_role',
                type: 3, // Type 3 adalah STRING
                description: 'Nama role yang ingin dicari',
                required: true
            }
        ]
    },
    {
        name: 'listall',
        description: 'Menampilkan seluruh kasta role dan anggotanya'
    }
];

// 3. Sinkronisasi Otomatis Perintah Slash saat Bot Menyala (on_ready)
client.once('ready', async () => {
    try {
        console.log(`🔄 Menyinkronkan perintah Slash ke Discord...`);
        const rest = new REST({ version: '10' }).setToken(TOKEN);
        
        // Mendaftarkan perintah secara global ke seluruh server yang mengundang bot
        await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: commands }
        );
        
        console.log(`Yahoo! Berhasil menyinkronkan ${commands.length} perintah Slash!`);
    } catch (error) {
        console.error(`Gagal sinkronisasi perintah: ${error}`);
    }
    console.log(`Bot ${client.user.tag} sudah aktif dan siap berkelana!`);
});

// 4. Logika Penanganan Perintah Masuk (Interaction Create)
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    const { commandName } = interaction;

    // === PERINTAH 1: SLASH HELP COMMAND ===
    if (commandName === 'bothelp') {
        const embed = new EmbedBuilder()
            .setTitle('📖 KAMPUS WANGSHENG - DOKUMENTASI BOT')
            .setDescription('Halo! Aku bot kustom pemantau member. Berikut adalah mantra perintah yang bisa kamu gunakan lewat perintah `/`: ')
            .setColor([241, 90, 34])
            .addFields(
                { name: '`/listall`', value: 'Menampilkan struktur semua role.', inline: false },
                { name: '`/listmember [nama_role]`', value: 'Mencari anggota spesifik.', inline: false }
            );
        
        await interaction.reply({ embeds: [embed] });
    }

    // === PERINTAH 2: SLASH LIST MEMBER PER ROLE ===
    if (commandName === 'listmember') {
        const namaRole = interaction.options.getString('nama_role');
        // Mencari role berdasarkan nama di server
        const role = interaction.guild.roles.cache.find(r => r.name.toLowerCase() === namaRole.toLowerCase());

        if (!role) {
            return interaction.reply({ content: `❌ Role '${namaRole}' tidak ditemukan.`, ephemeral: true });
        }

        // Ambil semua anggota di dalam role tersebut
        await interaction.guild.members.fetch(); // Ambil cache member terbaru
        const daftarNama = role.members.map(member => `- ${member.displayName}`);

        if (daftarNama.length === 0) {
            return interaction.reply({ content: `👻 Gak ada member di dalam role **${role.name}**.` });
        }

        const pesan = `**📊 Daftar Anggota Role ${role.name}:**\n` + daftarNama.join('\n');
        await interaction.reply({ content: pesan.substring(0, 2000) });
    }

    // === PERINTAH 3: SLASH LIST ALL DINAMIS ===
    if (commandName === 'listall') {
        await interaction.deferReply();
        await interaction.guild.members.fetch();

        let output = [`**📊 DAFTAR ANGGOTA ${interaction.guild.name.toUpperCase()}**`, '---'];

        // Urutkan role berdasarkan posisi tertinggi (sama seperti logika sorted python)
        const rolesDinamis = Array.from(interaction.guild.roles.cache.values())
            .sort((a, b) => b.position - a.position);

        for (const role of rolesDinamis) {
            // Abaikan @everyone (default) dan role bot managed
            if (role.id === interaction.guild.id || role.managed) continue;

            const manusiaMembers = role.members
                .filter(m => !m.user.bot)
                .map(m => m.displayName);

            output.push(`🔹 **${role.name}:**`);
            if (manusiaMembers.length === 0) {
                output.push(`_- Tidak ada anggota_`);
            } else {
                manusiaMembers.forEach(nama => output.push(`- ${nama}`));
            }
            output.push('');
        }

        const pesanFull = output.join('\n');
        await interaction.editReply({ content: pesanFull.substring(0, 2000) });
    }
});

// 5. Membuat Server Web Asli agar Glitch Mendeteksi Aplikasi Hidup
const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end("<html><body style='background:#1e1e2e;color:#f15a22;text-align:center;font-family:sans-serif;padding-top:50px;'><h1>🦋 Papilio Warden Status: ACTIVE (Node.js)</h1></body></html>");
});

// Glitch secara otomatis menyuntikkan port lewat process.env.PORT
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🌍 Server web pemantau aktif di port ${PORT}!`);
});

// Jalankan Bot masuk ke Discord
client.login(TOKEN);