const { google } = require('googleapis');

async function fetchData() {
  const auth = new google.auth.GoogleAuth({
    keyFile: './service_account_key.json',
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });

  const drive = google.drive({ version: 'v3', auth });

  const folderId = process.env.GOOGLE_DRIVE_FOLDER_ID;
  const response = await drive.files.list({
    q: `'${folderId}' in parents and mimeType='text/csv'`,
    fields: 'files(id, name, createdTime)',
  });

  return response.data.files;
}

fetchData().then(files => console.log(files)).catch(err => console.error(err));
