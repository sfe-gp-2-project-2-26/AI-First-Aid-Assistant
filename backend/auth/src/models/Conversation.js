import mongoose from 'mongoose';

const messageSchema = new mongoose.Schema({
  role: {
    type: String,
    required: true,
    enum: ['user', 'assistant'],
  },
  text: {
    type: String,
    required: false,
  },
  kind: {
    type: String,
    required: false, // answer, refusal, error
  },
  citations: {
    type: Array,
    default: [],
  },
  modelName: {
    type: String,
    required: false,
  }
}, {
  timestamps: { createdAt: 'timestamp', updatedAt: false }
});

const conversationSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  title: {
    type: String,
    default: 'New Conversation',
  },
  messages: [messageSchema],
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

export const Conversation = mongoose.model('Conversation', conversationSchema);

