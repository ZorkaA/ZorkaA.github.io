const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

// Supabase setup
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Axios with timeout
const axiosInstance = axios.create({ timeout: 30000 }); // 30 seconds timeout

async function fetchSquads() {
  const response = await axiosInstance.get('https://wbapi.wbpjs.com/squad/getSquadList');
  return response.data; // Array of squad names
}

async function fetchSquadMembers(squadName) {
  const response = await axiosInstance.get(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
  return response.data; // Array of member objects
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
    console.log('Total unique UIDs to insert:', new Set(uidsData.map(d => d.uid)).size);

    // Step 4: Insert into Supabase
    const { error } = await supabase
      .from('uids')
      .upsert(uidsData, { onConflict: 'uid' })
      .timeout(10000); // 10s timeout

    if (error) {
      console.error('Error inserting uids:', JSON.stringify(error, null, 2));
    } else {
      console.log('Inserted uids successfully:', uidsData.length);
    }
  } catch (error) {
    console.error('Main process failed:', JSON.stringify(error, null, 2));
  }
}

main().catch(error => console.error('Script failed:', JSON.stringify(error, null, 2)));
