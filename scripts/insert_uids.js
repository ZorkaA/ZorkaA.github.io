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

async function main() {
  try {
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

    // Step 4: Insert data in batches
    const batchSize = 500;
    for (let i = 0; i < uidsData.length; i += batchSize) {
      const batch = uidsData.slice(i, i + batchSize);
      console.log(`Upserting batch ${i / batchSize + 1} of ${Math.ceil(uidsData.length / batchSize)} (${batch.length} records)`);
      const { data, error } = await supabase
        .from('uids')
        .upsert(batch, { onConflict: 'uid' })
        .select();
      if (error) {
        console.error(`Batch upsert failed:`, JSON.stringify(error, null, 2));
        throw error;
      } else {
        console.log(`Batch upsert succeeded:`, data.length);
      }
    }

    console.log('All data inserted successfully');
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
    throw error;
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
