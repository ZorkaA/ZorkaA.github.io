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

async function fetchSquads() {
  const response = await axiosInstance.get('https://wbapi.wbpjs.com/squad/getSquadList');
  return response.data;
}

async function fetchSquadMembers(squadName) {
  const response = await axiosInstance.get(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
  return response.data;
}

// Health check function
async function checkSupabaseHealth() {
  try {
    const response = await axios.get(`${supabaseUrl}/healthz`, {
      headers: { Authorization: `Bearer ${supabaseKey}` }
    });
    console.log('Supabase health check:', response.status, response.data);
  } catch (error) {
    console.error('Health check failed:', JSON.stringify(error.response ? error.response.data : error.message, null, 2));
  }
}

async function main() {
  try {
    // Step 1: Check Supabase connectivity
    console.log('Checking Supabase health...');
    await checkSupabaseHealth();

    // Step 2: Test single insert
    console.log('Testing single insert...');
    const { data: testData, error: testError } = await supabase
      .from('uids')
      .insert({ uid: 'test123', name: 'TestUser' });
    if (testError) {
      console.error('Test insert failed:', JSON.stringify(testError, null, 2));
      throw testError;
    } else {
      console.log('Test insert succeeded:', JSON.stringify(testData, null, 2));
    }

    // Step 3: Fetch squads
    const squads = await fetchSquads();
    console.log('Fetched squads:', squads);

    // Step 4: Fetch squad members and collect UID/name pairs
    let allMembers = [];
    for (const squad of squads) {
      try {
        const members = await fetchSquadMembers(squad);
        console.log(`Fetched members for squad ${squad}:`, members.length);
        allMembers = allMembers.concat(members);
      } catch (error) {
        console.error(`Failed to fetch members for squad ${squad}:`, JSON.stringify(error, null, 2));
      }
    }

    // Step 5: Prepare data for insertion
    const uidsData = allMembers.map(member => ({
      uid: member.uid,
      name: member.nick
    }));
    const uniqueUids = new Set(uidsData.map(d => d.uid)).size;
    console.log('Total unique UIDs to insert:', uniqueUids);
    console.log('Sample data:', JSON.stringify(uidsData.slice(0, 3), null, 2));

    // Step 6: Insert data (single batch for now)
    console.log('Starting Supabase upsert...');
    const { data, error } = await supabase
      .from('uids')
      .upsert(uidsData, { onConflict: 'uid' });
    if (error) {
      console.error('Upsert failed:', JSON.stringify(error, null, 2));
      throw error;
    } else {
      console.log('Upsert succeeded:', data ? data.length : 'unknown');
    }
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
    throw error; // Re-throw to ensure outer catch logs it
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
