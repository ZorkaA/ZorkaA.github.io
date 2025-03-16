const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup (credentials from environment variables)
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Helper to flatten nested objects
function flattenObject(obj, parent = '', result = {}) {
  for (const key in obj) {
    const newKey = parent ? `${parent}_${key}` : key;
    if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
      flattenObject(obj[key], newKey, result);
    } else {
      result[newKey] = obj[key];
    }
  }
  return result;
}

// Helper to determine SQL type based on value
function getSqlType(value) {
  if (typeof value === 'number') {
    return Number.isInteger(value) ? 'BIGINT' : 'FLOAT';
  } else if (typeof value === 'boolean') {
    return 'BOOLEAN';
  } else {
    return 'TEXT';
  }
}

// Dynamically update table schema
async function updateTableSchema(tableName, data) {
  const { data: columns, error } = await supabase.rpc('get_table_columns', { table_name: tableName });
  if (error) throw error;

  const existingColumns = new Set(columns.map(col => col.column_name));
  const flattenedData = flattenObject(data);
  
  for (const [key, value] of Object.entries(flattenedData)) {
    if (!existingColumns.has(key)) {
      const sqlType = getSqlType(value);
      const query = `ALTER TABLE ${tableName} ADD COLUMN IF NOT EXISTS "${key}" ${sqlType};`;
      const { error: alterError } = await supabase.rpc('execute_sql', { query });
      if (alterError) {
        console.error(`Failed to add column ${key}:`, alterError);
      } else {
        console.log(`Added column ${key} as ${sqlType}`);
      }
    }
  }
}

async function fetchSquads() {
  const response = await axios.get('https://wbapi.wbpjs.com/squad/getSquadList');
  return response.data;
}

async function fetchSquadMembers(squadName) {
  const response = await axios.get(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
  return response.data;
}

async function fetchPlayerData(uid) {
  const response = await axios.get(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
  return response.data;
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
  const tableName = 'player_stats';

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
      console.log(`Fetched player data for UID ${uid}:`, JSON.stringify(playerData, null, 2));
      const flattenedData = flattenObject(playerData);
      const dataToInsert = {
        uid: playerData.uid,
        date: currentDate,
        ...flattenedData,
      };

      // Dynamically update schema if new columns are detected
      await updateTableSchema(tableName, playerData);

      const { error } = await supabase
        .from(tableName)
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
