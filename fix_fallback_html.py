with open("wb/tsstats/index.html", "r") as f:
    lines = f.readlines()

# Add Supabase Script back
for i, line in enumerate(lines):
    if "<script src=\"https://d3js.org/d3.v7.min.js\"></script>" in line:
        lines.insert(i, '    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n')
        break

# Find the place to add Supabase client initialization
for i, line in enumerate(lines):
    if "let yScaleType = 'linear';" in line:
        lines.insert(i+1, "        // Supabase setup\n        const supabaseUrl = 'https://vviprqpyqkwjdtqqlmde.supabase.co';\n        const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aXBycXB5cWt3amR0cXFsbWRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxMDUxNzMsImV4cCI6MjA0NTY4MTE3M30.ftmjdgdJPjOox5SpxDNoQ3kJX0vfbhRoEHharLcI4eM';\n        const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);\n\n")
        break

# Rewrite the fetch logic to fallback
start = -1
end = -1
for i, line in enumerate(lines):
    if "// Fetch data from Turso" in line:
        start = i
    if "updateChart(data, metrics);" in line and start != -1:
        end = i + 1
        break

if start != -1 and end != -1:
    new_code = """            // Fetch data with Turso, fallback to Supabase
            let data = null;
            try {
                console.log("Attempting to fetch from Turso...");
                const TURSO_URL = 'https://wb-zorkaa.aws-us-east-1.turso.io';
                const TURSO_TOKEN = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3ODg3Njk0NTMsImlkIjoiMDFhMDdhOWUtMjcwMS03ZTc1LWIxNjgtMmY3NTBhODdkY2Y2Iiwia2lkIjoiWXdIOURLS0hPSHpydmRBYWZwZFUtbXpVbXVXUFRoQ0E2eElkWS1VQmVfWSIsInJpZCI6IjQxM2ZjYTJhLTMwYTktNGUyZS04NmM3LWQ5MGFiYjVlZWExOCJ9.1LDhLKRRomV24VAbrtHP-8ZN3rPl9n8GiGrAqy9efLfAl0-PxXAeNenA55N0KsXLXRXZ4zsj5nxfB1K8uWjRDA';

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
                
                data = (execResult && execResult.cols && execResult.cols.length > 0 && execResult.rows && execResult.rows.length > 0)
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

            } catch (tursoError) {
                console.warn('Turso failed, falling back to Supabase:', tursoError);
                try {
                    const query = supabaseClient
                        .from('wbtsdb')
                        .select(`date, ${metrics.map(m => m.column).join(', ')}`)
                        .eq('uid', selectedUid)
                        .gte('date', startDate)
                        .order('date', { ascending: true });
                    
                    const { data: supaData, error: supaError } = await query;
                    if (supaError) throw supaError;
                    data = supaData;
                } catch (supaError) {
                    console.error('Supabase fallback error:', supaError);
                    alert('Error fetching data from both primary (Turso) and backup (Supabase) databases.');
                    document.getElementById('error-message').style.display = 'block';
                    return;
                }
            }

            if (!data || data.length === 0) {
                document.getElementById('error-message').style.display = 'block';
                alert('No data found for this UID in the selected time period.');
                return;
            }

            document.getElementById('error-message').style.display = 'none';
            updateChart(data, metrics);
"""
    lines[start:end] = [new_code]

with open("wb/tsstats/index.html", "w") as f:
    f.writelines(lines)
