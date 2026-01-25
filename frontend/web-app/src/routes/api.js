const express = require('express');
const router = express.Router();

// Existing endpoints

// New test endpoint
router.get('/test', (req, res) => {
  res.status(200).send('Test endpoint is working!');
});

module.exports = router;