const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
console.log('Supabase URL:', supabaseUrl ? 'Set' : 'Not set');
console.log('Supabase Key:', supabaseKey ? 'Set (hidden)' : 'Not set');
const supabase = createClient(supabaseUrl, supabaseKey);

// Axios with timeout
const axiosInstance = axios.create({ timeout: 30000 }); // 30 seconds timeout

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

// Helper to determine SQL type
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
async function updateTableSchema(tableName, sampleData) {
  console.log(`Fetching existing columns for ${tableName}...`);
  const { data: columns, error } = await supabase.rpc('get_table_columns', { table_name: tableName });
  if (error) {
    console.error('Failed to fetch columns:', JSON.stringify(error, null, 2));
    throw error;
  }
  console.log('Existing columns:', columns.map(col => col.col_name));

  const existingColumns = new Set(columns.map(col => col.col_name));
  const flattenedData = flattenObject(sampleData);
  console.log('New columns to check:', Object.keys(flattenedData).length);

  for (const [key, value] of Object.entries(flattenedData)) {
    if (!existingColumns.has(key)) {
      const sqlType = getSqlType(value);
      const query = `ALTER TABLE ${tableName} ADD COLUMN IF NOT EXISTS "${key}" ${sqlType};`;
      console.log(`Executing: ${query}`);
      const { error: alterError } = await supabase.rpc('execute_sql', { query });
      if (alterError) {
        console.error(`Failed to add column ${key}:`, JSON.stringify(alterError, null, 2));
      } else {
        console.log(`Added column ${key} as ${sqlType}`);
      }
    }
  }
}

async function fetchPlayerData(uid) {
  const response = await axiosInstance.get(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
  return response.data;
}

async function main() {
  const currentDate = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  try {
    // Step 1: Fetch UIDs from the uids table
    console.log('Fetching UIDs from Supabase...');
    const { data: uidsData, error: uidsError } = await supabase
      .from('uids')
      .select('uid');
    if (uidsError) {
      console.error('Failed to fetch UIDs:', JSON.stringify(uidsError, null, 2));
      throw uidsError;
    }
    const uids = uidsData.map(row => row.uid);
    console.log('Total UIDs to process:', uids.length);

    // Step 2: Fetch sample player data for schema update
    if (uids.length > 0) {
      const sampleUid = uids[0];
      console.log(`Fetching sample data for UID ${sampleUid}...`);
      const sampleData = await fetchPlayerData(sampleUid);
      await updateTableSchema('wbtsdb', sampleData);
    } else {
      console.log('No UIDs found, skipping processing');
      return;
    }

    // Step 3: Fetch and insert player data in batches
    const batchSize = 100;
    for (let i = 0; i < uids.length; i += batchSize) {
      const batchUids = uids.slice(i, i + batchSize);
      console.log(`Processing batch ${i / batchSize + 1} of ${Math.ceil(uids.length / batchSize)} (${batchUids.length} UIDs)`);

      const batchData = [];
      for (const uid of batchUids) {
        try {
          const playerData = await fetchPlayerData(uid);
          const flattenedData = flattenObject(playerData);
          batchData.push({
            uid: playerData.uid,
            date: currentDate,
            ...flattenedData
          });
        } catch (error) {
          console.error(`Failed to fetch data for UID ${uid}:`, JSON.stringify(error, null, 2));
        }
      }

      if (batchData.length > 0) {
        console.log(`Upserting ${batchData.length} records...`);
        const { data, error } = await supabase
          .from('wbtsdb')
          .upsert(batchData, { onConflict: ['uid', 'date'] })
          .select();
        if (error) {
          console.error('Batch upsert failed:', JSON.stringify(error, null, 2));
          throw error;
        } else {
          console.log(`Batch upsert succeeded:`, data.length);
        }
      }
    }

    console.log('All player stats inserted successfully');
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
    throw error;
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
