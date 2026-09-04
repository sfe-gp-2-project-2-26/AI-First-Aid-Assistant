import express from "express";
import {
  getConversations,
  getConversation,
  deleteConversation,
  renameConversation,
} from "../controllers/conversationController.js";
import { requireAuth } from "../middleware/authMiddleware.js";

const router = express.Router();

router.use(requireAuth);

router.get("/", getConversations);
router.get("/:conversation_id", getConversation);
router.delete("/:conversation_id", deleteConversation);
router.patch("/:conversation_id", renameConversation);

export default router;
