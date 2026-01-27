const express = require('express');
const path = require('path');

const app = express();
const dist = path.resolve(__dirname, '..', 'frontend', 'web-app', 'dist');

app.use('/app', express.static(dist, { index: false }));
app.get('/app/*', (req, res) => {
    res.sendFile(path.join(dist, 'index.html'));
});

const port = process.env.PORT || 8081;
app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`Serving frontend build at http://127.0.0.1:${port}/app/`);
});
