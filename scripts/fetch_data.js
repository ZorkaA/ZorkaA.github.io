const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup
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
  console.log(`Fetching existing columns for table ${tableName}`);
  const { data: columns, error } = await supabase.rpc('get_table_columns', { table_name: tableName });
  if (error) {
    console.error('Failed to fetch columns:', JSON.stringify(error, null, 2));
    throw error;
  }
  console.log('Existing columns:', columns);

  const existingColumns = new Set(columns.map(col => col.col_name));
  const flattenedData = flattenObject(data);
  console.log('New columns to check:', Object.keys(flattenedData));

  for (const [key, value] of Object.entries(flattenedData)) {
    if (!existingColumns.has(key)) {
      const sqlType = getSqlType(value);
      const query = `ALTER TABLE ${tableName} ADD COLUMN IF NOT EXISTS "${key}" ${sqlType};`;
      console.log(`Executing query: ${query}`);
      const { error: alterError } = await supabase.rpc('execute_sql', { query });
      if (alterError) {
        console.error(`Failed to add column ${key}:`, JSON.stringify(alterError, null, 2));
      } else {
        console.log(`Added column ${key} as ${sqlType}`);
      }
    }
  }
}

const authHeader = 'Basic ' + Buffer.from(process.env.RATS_USER + ':' + process.env.RATS_PASS).toString('base64');

async function fetchPlayerList() {
  const response = await axios.get('http://ratsstats.ddns.net/get_player_list.php?squad=true', {
    headers: { 'Authorization': authHeader }
  });
  return response.data;
}

async function fetchPlayerData(uid) {
  const response = await axios.get(`http://ratsstats.ddns.net/get_player_stats.php?uid=${uid}`, {
    headers: { 'Authorization': authHeader }
  });
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
  const currentDate = new Date().toISOString().split('T')[0];
  const tableName = 'player_stats_subset';

  try {
    // Step 1: Fetch all players (includes squad info)
    const allMembers = await fetchPlayerList();
    console.log('Fetched players:', allMembers.length);

    // Step 2: Collect UIDs
    const existingUids = await loadExistingUids();
    const newUids = new Set(allMembers.map(member => member.uid));
    const combinedUids = new Set([...existingUids, ...newUids]);
    await saveUids(combinedUids);
    console.log('Total UIDs to process:', combinedUids.size);

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

        await updateTableSchema(tableName, playerData);

        const { error } = await supabase
          .from(tableName)
          .upsert(dataToInsert, { onConflict: ['uid', 'date'] });

        if (error) {
          console.error(`Error inserting data for UID ${uid}:`, JSON.stringify(error, null, 2));
        } else {
          console.log(`Inserted data for UID ${uid}`);
        }
      } catch (error) {
        console.error(`Failed to process UID ${uid}:`, JSON.stringify(error, null, 2));
      }
    }
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
