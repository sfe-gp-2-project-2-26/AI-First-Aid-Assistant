import express from 'express';
import { handleChat } from '../controllers/chatController.js';
import { optionalAuth } from '../middleware/authMiddleware.js';

const router = express.Router();

// optionalAuth allows both guests and logged-in users to use chat
router.post('/', optionalAuth, handleChat);

export default router;

