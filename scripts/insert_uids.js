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
const authHeader = 'Basic ' + Buffer.from(process.env.RATS_USER + ':' + process.env.RATS_PASS).toString('base64');

async function fetchPlayerList() {
  const response = await axiosInstance.get('http://ratsstats.ddns.net/get_player_list.php?squad=true', {
    headers: { 'Authorization': authHeader }
  });
  return response.data;
}

async function main() {
  try {
    // Step 1: Fetch all players (includes squad info)
    const allMembers = await fetchPlayerList();
    console.log('Fetched players:', allMembers.length);

    // Step 2: Prepare data for insertion
    const uidsData = allMembers.map(member => ({
      uid: member.uid,
      name: member.nick
    }));
    const uniqueUids = new Set(uidsData.map(d => d.uid)).size;
    console.log('Total unique UIDs to insert:', uniqueUids);
    console.log('Sample data:', JSON.stringify(uidsData.slice(0, 3), null, 2));

    // Step 3: Insert data in batches
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
