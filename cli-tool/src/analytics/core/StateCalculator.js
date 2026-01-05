const chalk = require('chalk');

/**
 * StateCalculator - Handles all conversation state determination logic
 * Extracted from monolithic analytics.js for better maintainability
 */
class StateCalculator {
  constructor() {
    // Cache for process states to avoid repeated calculations
    this.processCache = new Map();
  }

  /**
   * Get time since last activity in milliseconds
   * @param {Date|string} timestamp - Last activity timestamp
   * @returns {number} Milliseconds since activity
   */
  getTimeSinceLastActivity(timestamp) {
    if (!timestamp) return 0;
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return 0;
    return Date.now() - date.getTime();
  }

  /**
   * Check if activity is recent (within 1 hour)
   * @param {Date|string} timestamp - Activity timestamp
   * @returns {boolean} True if within 1 hour
   */
  isRecentActivity(timestamp) {
    if (!timestamp) return false;
    const diff = this.getTimeSinceLastActivity(timestamp);
    return diff > 0 && diff < 3600000; // 1 hour
  }

  /**
   * Main state determination logic with process information
   * @param {Array} messages - Parsed conversation messages
   * @param {Date} lastModified - File last modification time
   * @param {Object} runningProcess - Active process information
   * @returns {string} Conversation state
   */
  determineConversationState(messages, lastModified, runningProcess = null) {
    const now = new Date();
    const safeMessages = Array.isArray(messages) ? messages.filter(m => m && m.timestamp) : [];
    const safeLastModified = lastModified instanceof Date ? lastModified : (lastModified ? new Date(lastModified) : new Date(0));
    
    const fileTimeDiff = now - safeLastModified;
    const fileMinutesAgo = fileTimeDiff / (1000 * 60);

    // Enhanced detection: Look for real Gemini CLI activity indicators
    const geminiActivity = this.detectRealGeminiActivity(safeMessages, safeLastModified);
    
    let status = 'Inactive';
    if (geminiActivity.isActive) {
      status = geminiActivity.status;
    } else if (fileMinutesAgo < 5) {
      status = 'Gemini CLI working...';
    } else if (runningProcess && runningProcess.hasActiveCommand) {
      status = 'Active session';
    } else if (safeMessages.length === 0) {
      status = fileMinutesAgo < 5 ? 'Waiting for input...' : 'Idle';
    } else {
      // Logic for active conversations
      const sortedMessages = [...safeMessages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      const lastMessage = sortedMessages[sortedMessages.length - 1];
      const lastMessageTime = new Date(lastMessage.timestamp);
      const lastMessageMinutesAgo = (now - lastMessageTime) / (1000 * 60);

      if (lastMessage.role === 'user') {
        if (lastMessageMinutesAgo < 3) status = 'Gemini CLI working...';
        else if (lastMessageMinutesAgo < 10) status = 'Awaiting response...';
        else if (lastMessageMinutesAgo < 30) status = 'User typing...';
        else status = 'Recently active';
      } else if (lastMessage.role === 'assistant') {
        if (lastMessageMinutesAgo < 10) status = 'Awaiting user input...';
        else if (lastMessageMinutesAgo < 30) status = 'User typing...';
        else status = 'Recently active';
      } else if (fileMinutesAgo < 10 || lastMessageMinutesAgo < 30) {
        status = 'Recently active';
      } else if (fileMinutesAgo < 60 || lastMessageMinutesAgo < 120) {
        status = 'Idle';
      }
    }

    const lastMessage = safeMessages.length > 0 ? [...safeMessages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)).pop() : null;
    const lastUserMessage = safeMessages.filter(m => m.role === 'user').sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
    const lastAssistantMessage = safeMessages.filter(m => m.role === 'assistant').sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];

    return {
      status,
      hasRunningProcess: !!runningProcess,
      lastActivity: lastMessage ? new Date(lastMessage.timestamp) : safeLastModified,
      messageCount: safeMessages.length,
      lastUserMessage: lastUserMessage ? new Date(lastUserMessage.timestamp) : null,
      lastAssistantMessage: lastAssistantMessage ? new Date(lastAssistantMessage.timestamp) : null,
      timeSinceLastActivity: lastMessage ? (now - new Date(lastMessage.timestamp)) : (now - safeLastModified),
      isRecent: this.isRecentActivity(lastMessage ? lastMessage.timestamp : safeLastModified),
      runningProcess
    };
  }

  /**
   * Quick state calculation without file I/O for ultra-fast updates
   * @param {Object} conversation - Conversation object
   * @param {Array} runningProcesses - Array of active processes
   * @returns {Object} Conversation state object
   */
  quickStateCalculation(conversation, runningProcesses) {
    // Check if there's an active process for this conversation
    const activeProcess = runningProcesses.find(process => 
      (process.workingDir && process.workingDir.includes(conversation.project)) ||
      (process.cwd && process.cwd.includes(conversation.project)) ||
      (process.command && process.command.includes(conversation.project)) ||
      conversation.runningProcess // Already matched
    );
    
    if (!activeProcess) {
      return {
        status: conversation.status || 'idle',
        hasRunningProcess: false,
        lastModified: conversation.lastModified
      };
    }
    
    // Simple heuristic based on file modification time
    const now = new Date();
    const lastModified = new Date(conversation.lastModified);
    const timeDiff = (now - lastModified) / 1000; // seconds
    
    let status = 'active';
    if (timeDiff < 30) {
      status = 'Gemini CLI working...';
    } else if (timeDiff < 300) {
      status = 'Awaiting user input...';
    } else {
      status = 'User typing...';
    }

    return {
      status,
      hasRunningProcess: true,
      runningProcess: activeProcess,
      lastModified: conversation.lastModified
    };
  }

  /**
   * Determine conversation status (active/recent/inactive)
   * @param {Array} messages - Parsed conversation messages
   * @param {Date} lastModified - File last modification time
   * @returns {string} Conversation status
   */
  determineConversationStatus(messages, lastModified) {
    const now = new Date();
    const safeMessages = Array.isArray(messages) ? messages.filter(m => m && m.timestamp) : [];
    const safeLastModified = lastModified instanceof Date ? lastModified : (lastModified ? new Date(lastModified) : new Date(0));
    
    const timeDiff = now - safeLastModified;
    const minutesAgo = timeDiff / (1000 * 60);

    if (safeMessages.length === 0) {
      return minutesAgo < 5 ? 'active' : 'idle';
    }

    // Sort messages by timestamp
    const sortedMessages = [...safeMessages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const lastMessage = sortedMessages[sortedMessages.length - 1];
    const lastMessageTime = new Date(lastMessage.timestamp);
    const lastMessageMinutesAgo = (now - lastMessageTime) / (1000 * 60);

    // More balanced logic - active conversations and recent activity
    if (lastMessage.role === 'user') {
      if (lastMessageMinutesAgo < 5) return 'waiting';
      return 'active';
    } else if (lastMessage.role === 'assistant') {
      if (lastMessageMinutesAgo < 10) return 'completed';
      return 'active';
    }

    // Use file modification time for recent activity
    if (minutesAgo < 5) return 'active';
    if (minutesAgo < 60) return 'idle';
    return 'inactive';
  }

  /**
   * Detect real Gemini CLI activity based on conversation patterns and file activity
   * @param {Array} messages - Conversation messages
   * @param {Date} lastModified - File last modification time
   * @returns {Object} Activity detection result
   */
  detectRealGeminiActivity(messages, lastModified) {
    const now = new Date();
    const fileMinutesAgo = (now - lastModified) / (1000 * 60);
    
    if (!messages || messages.length === 0) {
      return { isActive: false, status: 'No messages' };
    }
    
    // Sort messages by timestamp
    const sortedMessages = messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const lastMessage = sortedMessages[sortedMessages.length - 1];
    const lastMessageTime = new Date(lastMessage.timestamp);
    const messageMinutesAgo = (now - lastMessageTime) / (1000 * 60);
    
    // Real activity indicators:
    
    // 1. Very recent file modification (Gemini CLI just wrote to the conversation file)
    if (fileMinutesAgo < 1) {
      return { isActive: true, status: 'Gemini CLI working...' };
    }
    
    // 2. Recent user message with recent file activity (Gemini is processing)
    if (lastMessage.role === 'user' && messageMinutesAgo < 5 && fileMinutesAgo < 10) {
      return { isActive: true, status: 'Gemini CLI working...' };
    }
    
    // 3. Recent assistant message with very recent file activity (might still be working)
    if (lastMessage.role === 'assistant' && messageMinutesAgo < 2 && fileMinutesAgo < 5) {
      return { isActive: true, status: 'Gemini CLI finishing...' };
    }
    
    // 4. Look for tool activity patterns (tools often indicate active sessions)
    const recentMessages = sortedMessages.slice(-3);
    const hasRecentTools = recentMessages.some(msg => 
      (Array.isArray(msg.content) && msg.content.some(block => block.type === 'tool_use')) ||
      (msg.toolResults && msg.toolResults.length > 0)
    );
    
    if (hasRecentTools && messageMinutesAgo < 10 && fileMinutesAgo < 15) {
      return { isActive: true, status: 'Active session' };
    }
    
    // 5. Rapid message exchange pattern (back-and-forth conversation)
    if (sortedMessages.length >= 2) {
      const lastTwoMessages = sortedMessages.slice(-2);
      const timeBetweenLast = Math.abs(
        new Date(lastTwoMessages[1].timestamp) - new Date(lastTwoMessages[0].timestamp)
      ) / (1000 * 60); // minutes
      
      if (timeBetweenLast < 5 && messageMinutesAgo < 15 && fileMinutesAgo < 20) {
        return { isActive: true, status: 'Active conversation' };
      }
    }
    
    return { isActive: false, status: null };
  }

  /**
   * Get CSS class for conversation state styling
   * @param {string} conversationState - The conversation state
   * @returns {string} CSS class name
   */
  getStateClass(conversationState) {
    if (conversationState.includes('working') || conversationState.includes('Working')) {
      return 'working';
    }
    if (conversationState.includes('typing') || conversationState.includes('Typing')) {
      return 'typing';
    }
    return '';
  }

  /**
   * Clear any cached state information
   */
  clearCache() {
    this.processCache.clear();
  }
}

module.exports = StateCalculator;