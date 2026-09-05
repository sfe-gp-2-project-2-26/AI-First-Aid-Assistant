import { Conversation } from '../models/Conversation.js';

export const handleChat = async (req, res) => {
  try {
    const { conversation_id, query } = req.body;
    const user = req.user; // from optionalAuth

    if (!query) {
      return res.status(400).json({ error: 'Query is required.' });
    }

    let conversation = null;

    // Only process conversation logic if user is authenticated
    if (user) {
      if (conversation_id) {
        conversation = await Conversation.findOne({
          _id: conversation_id,
          user_id: user.user_id,
        });
        if (!conversation) {
          return res.status(404).json({ error: 'Conversation not found or access denied.' });
        }
      } else {
        // Generate title from query (first 30 chars)
        const title = query.length > 30 ? query.substring(0, 30) + '...' : query;
        conversation = new Conversation({
          user_id: user.user_id,
          title: title,
          messages: []
        });
      }

      // Save user message
      conversation.messages.push({
        role: 'user',
        text: query,
      });
      await conversation.save();
    }

    // Call Python backend
    // Since this runs in Docker, process.env.PYTHON_BACKEND_URL will be http://backend:3000
    // If running locally without docker, it could be http://localhost:3000
    const pythonUrl = process.env.PYTHON_BACKEND_URL || 'http://backend:3000';
    
    // We must use fetch
    const response = await fetch(`${pythonUrl}/api/v1/generation/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      const errorText = await response.text();
      let detail = 'Error from Python backend';
      try {
        const errJson = JSON.parse(errorText);
        detail = errJson.detail || detail;
      } catch (e) {}
      return res.status(response.status).json({ error: detail });
    }

    const aiResponse = await response.json();

    // Save AI response if user is authenticated
    if (user && conversation) {
      conversation.messages.push({
        role: 'assistant',
        kind: aiResponse.result.answer ? 'answer' : 'refusal',
        text: aiResponse.result.answer || aiResponse.result.refusal_reason || 'No reliable guidance found.',
        citations: aiResponse.result.citations || [],
        modelName: aiResponse.result.model_name || null
      });
      await conversation.save();
    }

    // Return the response directly
    return res.status(200).json({
      conversation_id: conversation ? conversation._id : null,
      ...aiResponse
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Internal server error during chat.' });
  }
};

