#!/usr/bin/env node

(async () => {
  const fetch = (await import('node-fetch')).default;

  async function getPlayerStats(uid) {
    try {
      const response = await fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      // Calculate total kills by summing all kills_per_weapon values
      const totalKills = Object.values(data.kills_per_weapon || {}).reduce((sum, val) => sum + val, 0);

      // Calculate total deaths by summing all deaths values
      const totalDeaths = Object.values(data.deaths || {}).reduce((sum, val) => sum + val, 0);

      // Format the output
      console.log('**********');
      console.log(`Stats for ${data.nick} (${uid}):`);
      console.log(`Kills: ${totalKills}`);
      console.log(`Deaths: ${totalDeaths}`);
      console.log(`Level: ${data.level}`);
      console.log(`XP: ${data.xp}`);
      console.log('**********');
    } catch (error) {
      console.error('Error fetching player stats:', error.message);
      process.exit(1);
    }
  }

  // Get UID from command-line arguments
  const uid = process.argv[2];
  if (!uid) {
    console.error('Please provide a UID as an argument.');
    console.error('Example: node index.js 61615f38d142af62453c6a90');
    process.exit(1);
  }

  // Run the function
  await getPlayerStats(uid);
})();
