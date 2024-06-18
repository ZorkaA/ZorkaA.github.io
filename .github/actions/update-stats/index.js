const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const process = require('process');

const statsFile = path.join(__dirname, '../../../stats.json');
const googleDriveApiKey = process.env.GOOGLE_DRIVE_API_KEY;
const googleDriveFolderId = process.env.GOOGLE_DRIVE_FOLDER_ID;

async function main() {
  const auth = new google.auth.JWT({
    email: process.env.GOOGLE_DRIVE_SERVICE_ACCOUNT_EMAIL,
    key: process.env.GOOGLE_DRIVE_API_KEY.replace(/\\n/g, '\n'),
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });

  const drive = google.drive({ version: 'v3', auth });

  const res = await drive.files.list({
    q: `'${googleDriveFolderId}' in parents and mimeType='text/csv' and name contains 'apidb'`,
    fields: 'files(id, name)',
  });

  const files = res.data.files;
  const dates = files.map(file => {
    const datePart = file.name.split('_')[0];
    return new Date(datePart);
  });

  const stats = {
    firstPull: dates.length ? new Date(Math.min(...dates)).toDateString() : 'N/A',
    lastPull: dates.length ? new Date(Math.max(...dates)).toDateString() : 'N/A',
    totalPulls: files.length,
  };

  fs.writeFileSync(statsFile, JSON.stringify(stats, null, 2));
}

main().catch(console.error);
