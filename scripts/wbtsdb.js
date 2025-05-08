const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
console.log('Supabase URL:', supabaseUrl ? 'Set' : 'Not set');
console.log('Supabase Key:', supabaseKey ? 'Set (hidden)' : 'Not set');
const supabase = createClient(supabaseUrl, supabaseKey);

// Axios with timeout
const axiosInstance = axios.create({ timeout: 60000 }); // 60 seconds timeout

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

// Helper to determine SQL type (all numbers as FLOAT)
function getSqlType(value) {
  if (typeof value === 'number') {
    return 'FLOAT';
  } else if (typeof value === 'boolean') {
    return 'BOOLEAN';
  } else {
    return 'TEXT';
  }
}

// Update table schema for a batch
async function ensureSchemaForBatch(tableName, batchData) {
  console.log(`Fetching existing columns for ${tableName}...`);
  const { data: columns, error } = await supabase.rpc('get_table_columns', { table_name: tableName });
  if (error) {
    console.error('Failed to fetch columns:', JSON.stringify(error, null, 2));
    throw error;
  }
  const existingColumns = new Set(columns.map(col => col.col_name));
  console.log('Existing columns:', columns.map(col => col.col_name));

  let newColumnsAdded = false;
  for (const record of batchData) {
    const flattenedData = flattenObject(record);
    for (const [key, value] of Object.entries(flattenedData)) {
      if (!existingColumns.has(key)) {
        const sqlType = getSqlType(value);
        const query = `ALTER TABLE ${tableName} ADD COLUMN IF NOT EXISTS "${key}" ${sqlType};`;
        console.log(`Executing: ${query}`);
        const { error: alterError } = await supabase.rpc('execute_sql', { query });
        if (alterError) {
          console.error(`Failed to add column ${key}:`, JSON.stringify(alterError, null, 2));
          throw alterError;
        } else {
          console.log(`Added column ${key} as ${sqlType}`);
          existingColumns.add(key);
          newColumnsAdded = true;
        }
      }
    }
  }

  if (newColumnsAdded) {
    console.log('Waiting 10 seconds for schema cache to refresh...');
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
}

async function fetchPlayerData(uid) {
  try {
    const response = await axiosInstance.get(`https://wbapi.wbpjs.com/players/getPlayer?uid=${uid}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch data for UID ${uid}:`, JSON.stringify({
      message: error.message,
      code: error.code,
    }, null, 2));
    return null; // Skip this UID
  }
}

async function fetchAllUids() {
  const allUids = [];
  let page = 0;
  const pageSize = 1000; // Supabase default limit
  while (true) {
    const { data, error } = await supabase
      .from('uids')
      .select('uid')
      .range(page * pageSize, (page + 1) * pageSize - 1);
    if (error) {
      console.error('Failed to fetch UIDs:', JSON.stringify(error, null, 2));
      throw error;
    }
    allUids.push(...data.map(row => row.uid));
    if (data.length < pageSize) break; // No more pages
    page++;
  }
  return allUids;
}

async function main() {
  const currentDate = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  try {
    // Step 1: Fetch all UIDs from the uids table
    console.log('Fetching UIDs from Supabase...');
    const uids = await fetchAllUids();
    console.log('Total UIDs to process:', uids.length);

    // Step 2: Fetch and insert player data in batches
    const batchSize = 50;
    for (let i = 0; i < uids.length; i += batchSize) {
      const batchUids = uids.slice(i, i + batchSize);
      console.log(`Processing batch ${i / batchSize + 1} of ${Math.ceil(uids.length / batchSize)} (${batchUids.length} UIDs)`);

      const batchData = [];
      for (const uid of batchUids) {
        const playerData = await fetchPlayerData(uid);
        if (playerData) {
          const flattenedData = flattenObject(playerData);
          batchData.push({
            uid: playerData.uid,
            date: currentDate,
            ...flattenedData
          });
        }
      }

      if (batchData.length > 0) {
        await ensureSchemaForBatch('wbtsdb', batchData);

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
      } else {
        console.log('No valid data in batch, skipping upsert');
      }
    }

    console.log('All player stats inserted successfully');
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
    throw error;
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
