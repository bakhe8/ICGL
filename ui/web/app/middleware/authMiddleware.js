// Import necessary libraries and services
const jwt = require('jsonwebtoken');
const HDALBridgeService = require('../services/hdalBridgeService');

// Middleware to protect routes
const authMiddleware = async (req, res, next) => {
    try {
        const token = req.headers.authorization.split(' ')[1];
        const decoded = await HDALBridgeService.validateToken(token);
        req.user = decoded;
        next();
    } catch (error) {
        res.status(401).json({ message: 'Not authorized' });
    }
};

module.exports = authMiddleware;