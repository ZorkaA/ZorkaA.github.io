# Backend Configuration Instructions

To fully resolve the CORS issues when searching from `zorkaa.github.io`, the backend hosting `wbv.vercel.app` must be configured to allow Cross-Origin Resource Sharing (CORS).

## Required Changes for Vercel

If `wbv.vercel.app` is hosted on Vercel, you need to add or update the `vercel.json` file in that repository with the following headers.

### `vercel.json`

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
        { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version" }
      ]
    }
  ]
}
```

**Note:** You can replace `"value": "*"` with `"value": "https://zorkaa.github.io"` for better security if you only want to allow requests from that specific domain.

## Why is this needed?

Browsers enforce Same-Origin Policy. Since `zorkaa.github.io` and `wbv.vercel.app` are different origins, the browser blocks the JavaScript on the GitHub Pages site from reading the response from the Vercel app unless the Vercel app explicitly says "It's okay" via these headers.

The frontend fix we implemented (caching and client-side filtering) reduces the number of requests and fixes the 404 errors from bad queries, but the initial fetch of the player list still requires these CORS headers to be present.
