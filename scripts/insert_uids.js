const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
console.log('Supabase URL:', supabaseUrl ? 'Set' : 'Not set');
console.log('Supabase Key:', supabaseKey ? 'Set (hidden)' : 'Not set');
const supabase = createClient(supabaseUrl, supabaseKey);

// Axios with timeout
const axiosInstance = axios.create({ timeout: 30000 });

async function fetchSquads() {
  const response = await axiosInstance.get('https://wbapi.wbpjs.com/squad/getSquadList');
  return response.data;
}

async function fetchSquadMembers(squadName) {
  const response = await axiosInstance.get(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
  return response.data;
}

async function main() {
  try {
    // Test connectivity with a single insert
    console.log('Testing single insert...');
    const testResult = await supabase
      .from('uids')
      .upsert([{ uid: 'test123', name: 'TestUser' }], { onConflict: 'uid' })
      .timeout(10000);
    if (testResult.error) {
      console.error('Test insert failed:', JSON.stringify(testResult.error, null, 2));
      throw testResult.error;
    } else {
      console.log('Test insert succeeded:', JSON.stringify(testResult.data, null, 2));
    }

    // Step 1: Fetch squads
    const squads = await fetchSquads();
    console.log('Fetched squads:', squads);

    // Step 2: Fetch squad members and collect UID/name pairs
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

    // Step 3: Prepare data for insertion
    const uidsData = allMembers.map(member => ({
      uid: member.uid,
      name: member.nick
    }));
    const uniqueUids = new Set(uidsData.map(d => d.uid)).size;
    console.log('Total unique UIDs to insert:', uniqueUids);
    console.log('Sample data:', JSON.stringify(uidsData.slice(0, 3), null, 2));

    // Step 4: Insert into Supabase
    console.log('Starting Supabase upsert...');
    const { data, error } = await supabase
      .from('uids')
      .upsert(uidsData, { onConflict: 'uid' })
      .timeout(30000);

    if (error) {
      console.error('Upsert failed with error:', JSON.stringify(error, null, 2));
      throw error;
    } else {
      console.log('Upsert succeeded. Inserted/updated rows:', data ? data.length : 'unknown');
    }
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
