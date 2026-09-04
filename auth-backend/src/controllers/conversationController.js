import { Conversation } from "../models/Conversation.js";

export const getConversations = async (req, res) => {
  try {
    const user_id = req.user.user_id;
    // return conversations sorted by updated_at descending, omit messages for list
    const conversations = await Conversation.find({ user_id })
      .select("-messages")
      .sort({ updated_at: -1 });
    res.status(200).json(conversations);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch conversations." });
  }
};

export const getConversation = async (req, res) => {
  try {
    const { conversation_id } = req.params;
    const user_id = req.user.user_id;

    const conversation = await Conversation.findOne({
      _id: conversation_id,
      user_id,
    });

    if (!conversation) {
      return res.status(404).json({ error: "Conversation not found." });
    }

    res.status(200).json(conversation);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch conversation." });
  }
};

export const deleteConversation = async (req, res) => {
  try {
    const { conversation_id } = req.params;
    const user_id = req.user.user_id;

    const result = await Conversation.deleteOne({
      _id: conversation_id,
      user_id,
    });

    if (result.deletedCount === 0) {
      return res
        .status(404)
        .json({ error: "Conversation not found or unauthorized." });
    }

    res.status(200).json({ message: "Conversation deleted." });
  } catch (error) {
    res.status(500).json({ error: "Failed to delete conversation." });
  }
};

export const renameConversation = async (req, res) => {
  try {
    const { conversation_id } = req.params;
    const { title } = req.body;
    const user_id = req.user.user_id;

    if (!title) {
      return res.status(400).json({ error: "Title is required." });
    }

    const conversation = await Conversation.findOneAndUpdate(
      { _id: conversation_id, user_id },
      { title },
      { new: true },
    );

    if (!conversation) {
      return res
        .status(404)
        .json({ error: "Conversation not found or unauthorized." });
    }

    res.status(200).json(conversation);
  } catch (error) {
    res.status(500).json({ error: "Failed to rename conversation." });
  }
};
