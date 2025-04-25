#!/usr/bin/env node

const axios = require('axios');
const { program } = require('commander');

// Define the CLI program
program
  .version('1.0.0')
  .description('Fetch player stats from wbapi.wbpjs.com')
  .requiredOption('-u, --uid <uid>', 'Player UID to query')
  .action(async (options) => {
    const uid = options.uid;
    const apiUrl = `https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`;

    try {
      const response = await axios.get(apiUrl);
      const data = response.data;

      // Calculate total kills and deaths by summing kills_per_weapon and deaths
      const totalKills = Object.values(data.kills_per_weapon || {}).reduce((sum, val) => sum + val, 0);
      const totalDeaths = Object.values(data.deaths || {}).reduce((sum, val) => sum + val, 0);

      // Output formatted stats
      console.log('**********');
      console.log(`Stats for ${data.nick} (${data.uid}):`);
      console.log(`Kills: ${totalKills}`);
      console.log(`Deaths: ${totalDeaths}`);
      console.log(`Level: ${data.level}`);
      console.log(`XP: ${data.xp}`);
      console.log('**********');
    } catch (error) {
      console.error('Error fetching player stats:', error.message);
      process.exit(1);
    }
  });

// Parse command-line arguments
program.parse(process.argv);
