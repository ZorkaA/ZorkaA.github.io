import re

with open("wb/tsstats/index.html", "r") as f:
    content = f.read()

# Remove supabase script
content = content.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>', '')

# Replace supabase initialization and searchUid logic
search_func_old = """        async function searchUid() {
            selectedUid = document.getElementById('uidInput').value.trim();
            if (!selectedUid) {
                alert('Please enter a UID');
                return;
            }

            try {
                // Determine date filter based on selected time period
                let dateFilter = new Date();
                if (timePeriod === '7d') {
                    dateFilter.setDate(dateFilter.getDate() - 7);
                } else if (timePeriod === '30d') {
                    dateFilter.setDate(dateFilter.getDate() - 30);
                } else if (timePeriod === '90d') {
                    dateFilter.setDate(dateFilter.getDate() - 90);
                } else {
                    dateFilter = null; // 'all' time
                }

                let query = supabaseClient
                    .from('wbtsdb')
                    .select('*')
                    .eq('uid', selectedUid)
                    .order('date', { ascending: true });

                if (dateFilter) {
                    query = query.gte('date', dateFilter.toISOString().split('T')[0]);
                }

                const { data, error } = await query;

                if (error) {
                    throw error;
                }

                if (data.length === 0) {
                    alert('No data found for this UID in the selected time period.');
                    return;
                }

                updateChart(data);
            } catch (error) {
                console.error('Error fetching data:', error);
                alert('An error occurred while fetching data.');
            }
        }"""

search_func_new = """        const TURSO_URL = 'https://wb-zorkaa.aws-us-east-1.turso.io';
        // IMPORTANT: Replace this with a READ-ONLY token generated via `turso db tokens create wb --read-only`
        const TURSO_TOKEN = 'INSERT_READ_ONLY_TOKEN_HERE';

        async function tursoQuery(sql, args = []) {
            const response = await fetch(`${TURSO_URL}/v2/pipeline`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${TURSO_TOKEN}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    requests: [
                        { type: 'execute', stmt: { sql, args: args.map(a => ({ type: 'text', value: String(a) })) } },
                        { type: 'close' }
                    ]
                })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const result = await response.json();
            const execResult = result.results[0].response.result;
            return execResult.cols.map((col, colIndex) => {
                return execResult.rows.map(row => {
                    let val = row[colIndex].value;
                    if (row[colIndex].type === 'float') val = parseFloat(val);
                    if (row[colIndex].type === 'integer') val = parseInt(val, 10);
                    return val;
                });
            })[0].map((_, rowIndex) => {
                const obj = {};
                execResult.cols.forEach((col, colIndex) => {
                    let val = execResult.rows[rowIndex][colIndex].value;
                    if (execResult.rows[rowIndex][colIndex].type === 'float') val = parseFloat(val);
                    if (execResult.rows[rowIndex][colIndex].type === 'integer') val = parseInt(val, 10);
                    obj[col.name] = val;
                });
                return obj;
            });
        }

        async function searchUid() {
            selectedUid = document.getElementById('uidInput').value.trim();
            if (!selectedUid) {
                alert('Please enter a UID');
                return;
            }

            try {
                let dateFilter = new Date();
                if (timePeriod === '7d') {
                    dateFilter.setDate(dateFilter.getDate() - 7);
                } else if (timePeriod === '30d') {
                    dateFilter.setDate(dateFilter.getDate() - 30);
                } else if (timePeriod === '90d') {
                    dateFilter.setDate(dateFilter.getDate() - 90);
                } else {
                    dateFilter = null;
                }

                let sql = "SELECT * FROM wbtsdb WHERE uid = ?";
                let args = [selectedUid];

                if (dateFilter) {
                    sql += " AND date >= ?";
                    args.push(dateFilter.toISOString().split('T')[0]);
                }
                
                sql += " ORDER BY date ASC";

                const data = await tursoQuery(sql, args);

                if (data.length === 0) {
                    alert('No data found for this UID in the selected time period.');
                    return;
                }

                updateChart(data);
            } catch (error) {
                console.error('Error fetching data:', error);
                alert('An error occurred while fetching data. Check Turso connection and token.');
            }
        }"""

content = content.replace(search_func_old, search_func_new)

# Remove old supabase init variables
content = re.sub(r"const supabaseUrl = '[^']+';\n\s*const supabaseKey = '[^']+';\n\s*const supabaseClient = supabase\.createClient\(supabaseUrl, supabaseKey\);", "", content)

with open("wb/tsstats/index.html", "w") as f:
    f.write(content)

