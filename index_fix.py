import re

with open("wb/tsstats/index.html", "r") as f:
    content = f.read()

# Remove the supabase script tag
content = content.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>', '')
content = re.sub(r"const supabaseUrl = '[^']+';\n\s*const supabaseKey = '[^']+';\n\s*const supabaseClient = supabase\.createClient\(supabaseUrl, supabaseKey\);", "", content)

# Define the new fetch logic
new_fetch = """// Fetch data from Turso
            try {
                const TURSO_URL = 'https://wb-zorkaa.aws-us-east-1.turso.io';
                // IMPORTANT: Replace this with a READ-ONLY token generated via `turso db tokens create wb --read-only`
                const TURSO_TOKEN = 'INSERT_READ_ONLY_TOKEN_HERE';

                const sql = "SELECT date, " + metrics.map(m => m.column).join(', ') + " FROM wbtsdb WHERE uid = ? AND date >= ? ORDER BY date ASC";
                const args = [selectedUid, startDate];

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

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                const execResult = result.results[0].response.result;
                
                const data = execResult.cols.length > 0 && execResult.rows.length > 0 
                    ? execResult.rows.map((row, rowIndex) => {
                        const obj = {};
                        execResult.cols.forEach((col, colIndex) => {
                            let val = row[colIndex].value;
                            if (row[colIndex].type === 'float') val = parseFloat(val);
                            if (row[colIndex].type === 'integer') val = parseInt(val, 10);
                            obj[col.name] = val;
                        });
                        return obj;
                    })
                    : [];

                if (data.length === 0) {
                    document.getElementById('error-message').style.display = 'block';
                    alert('No data found for this UID in the selected time period.');
                    return;
                }
"""

# Replace the supabase try block with the new fetch block
# The original starts with `            // Fetch data from Supabase\n            try {`
# and ends with `                    if (!uidCheck || uidCheck.length === 0) {\n                        alert('No data found for this UID. Please verify the UID is correct.');\n                    } else {\n` plus some lines.

# Instead of regex, I'll just use string replacement on a known chunk.
start_idx = content.find('            // Fetch data from Supabase')
end_idx = content.find('                // Check if all requested metrics', start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_fetch + content[end_idx:]

with open("wb/tsstats/index.html", "w") as f:
    f.write(content)
