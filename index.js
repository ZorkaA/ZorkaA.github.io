#!/usr/bin/env node

async function getPlayerStats(uid) {
  try {
    const response = await fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();


    const totalKills = Object.values(data.kills_per_weapon || {}).reduce((sum, val) => sum + val, 0);


    const totalDeaths = Object.values(data.deaths || {}).reduce((sum, val) => sum + val, 0);


    const lastSeenTime = new Date(data.time * 1000); // Convert Unix timestamp to milliseconds
    const now = new Date();
    const diffSeconds = Math.floor((now - lastSeenTime) / 1000);
    let timeAgo;
    if (diffSeconds < 60) {
      timeAgo = `${diffSeconds} Seconds Ago`;
    } else if (diffSeconds < 3600) {
      timeAgo = `${Math.floor(diffSeconds / 60)} Minutes Ago`;
    } else if (diffSeconds < 86400) {
      timeAgo = `${Math.floor(diffSeconds / 3600)} Hours Ago`;
    } else {
      timeAgo = `${Math.floor(diffSeconds / 86400)} Days Ago`;
    }

    //MM/DD/YY HH:MM:SS AM/PM GMT
    const formattedTime = lastSeenTime.toLocaleString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: '2-digit',
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'GMT'
    }) + ' GMT';


    console.log('**********');
    console.log(`Stats for ${data.nick} (${uid}):`);
    console.log(`Kills: ${totalKills}`);
    console.log(`Deaths: ${totalDeaths}`);
    console.log(`Level: ${data.level}`);
    console.log(`XP: ${data.xp}`);
    console.log(`Last Seen: ${timeAgo} (${formattedTime})`);
    console.log('**********');
  } catch (error) {
    console.error('Error fetching player stats:', error.message);
    process.exit(1);
  }
}


const uid = process.argv[2];
if (!uid) {
  console.error('Please provide a UID as an argument.');
  process.exit(1);
}


getPlayerStats(uid);
