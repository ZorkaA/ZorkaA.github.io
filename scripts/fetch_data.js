const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup (credentials will come from environment variables)
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Helper to flatten nested objects
function flattenObject(obj, parent = '', result = {}) {
  for (const key in obj) {
    const newKey = parent ? `${parent}_${key}` : key;
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      flattenObject(obj[key], newKey, result);
    } else {
      result[newKey] = obj[key];
    }
  }
  return result;
}

async function fetchSquads() {
  const response = await axios.get('https://wbapi.wbpjs.com/squad/getSquadList');
  return response.data; // ["a", "b", "c"]
}

async function fetchSquadMembers(squadName) {
  const response = await axios.get(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
  return response.data; // Array of member objects
}

async function fetchPlayerData(uid) {
  const response = await axios.get(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
  return response.data; // Player object
}

async function loadExistingUids() {
  const csvPath = path.join(__dirname, '../data/squadmembers.csv');
  try {
    const data = await fs.readFile(csvPath, 'utf8');
    return new Set(data.split('\n').filter(line => line.trim()));
  } catch (error) {
    return new Set();
  }
}

async function saveUids(uids) {
  const csvPath = path.join(__dirname, '../data/squadmembers.csv');
  await fs.writeFile(csvPath, Array.from(uids).join('\n'));
}

async function main() {
  const currentDate = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

  // Step 1: Fetch squads
  const squads = await fetchSquads();

  // Step 2: Fetch squad members and collect UIDs
  let allMembers = [];
  for (const squad of squads) {
    const members = await fetchSquadMembers(squad);
    allMembers = allMembers.concat(members);
  }
  const existingUids = await loadExistingUids();
  const newUids = new Set(allMembers.map(member => member.uid));
  const combinedUids = new Set([...existingUids, ...newUids]);
  await saveUids(combinedUids);

  // Step 3: Fetch player data and insert into Supabase
  for (const uid of combinedUids) {
    try {
      const playerData = await fetchPlayerData(uid);
      const flattenedData = flattenObject(playerData);
      const dataToInsert = {
        uid: playerData.uid,
        date: currentDate,
        ...flattenedData,
      };

      const { error } = await supabase
        .from('player_stats_subset')
        .upsert(dataToInsert, { onConflict: ['uid', 'date'] });

      if (error) {
        console.error(`Error inserting data for UID ${uid}:`, error);
      } else {
        console.log(`Inserted data for UID ${uid}`);
      }
    } catch (error) {
      console.error(`Failed to fetch data for UID ${uid}:`, error);
    }
  }
}

main().catch(console.error);
