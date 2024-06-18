const { exec } = require('child_process');
const fs = require('fs');

// Load environment variables
const apiKey = process.env.GOOGLE_DRIVE_API_KEY;
const folderId = process.env.GOOGLE_DRIVE_FOLDER_ID;

// Write credentials to a file
fs.writeFileSync('credentials.json', apiKey);

// Execute the Python script
exec('python update_stats.py', (err, stdout, stderr) => {
  if (err) {
    console.error(`Error: ${stderr}`);
    process.exit(1);
  }
  console.log(`Output: ${stdout}`);
});
